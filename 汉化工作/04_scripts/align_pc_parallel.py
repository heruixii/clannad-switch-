from pathlib import Path
import sys,re,math,csv,unicodedata
sys.path.insert(0,str(Path(__file__).parent))
from extract_text_islands import extract

TRIM=' \\t,()[]{}<>"\'\\\\#'
SPEAKER_ALIASES={
    ('女の子','女孩'),('声','声音'),('男','男人'),('教師','教师'),('先生','老师'),
    ('男子生徒','男学生'),('女子生徒','女学生'),('生徒','学生'),('店員','店员'),
}

def clean(s):
    s=s.strip(TRIM)
    while len(s)>=2 and s[0]=='"' and s[-1]=='"': s=s[1:-1].strip()
    return s

def norm_speaker(s):
    s=unicodedata.normalize('NFKC',s).strip(' "“”「」『』')
    return s

def cls(s):
    s=clean(s)
    m=re.match(r'^【([^】]+)】["「（(]?',s)
    if m:return 'dialogue',norm_speaker(m.group(1))
    if s.startswith('《') and '》' in s:return 'resource',''
    return 'narration',''

def speakers_compatible(a,b):
    a=norm_speaker(a); b=norm_speaker(b)
    if a==b:return True
    if a.startswith('＊') and b.startswith('＊'):return True
    return (a,b) in SPEAKER_ALIASES or (b,a) in SPEAKER_ALIASES

def cjklen(s):
    return sum(c.isalnum() or ('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in clean(s))

def text_meta(s):
    kind,speaker=cls(s)
    return (kind,speaker,max(cjklen(s),1),('「' in s or '」' in s))

def unit_cost_meta(ma,mb):
    ca,sa,la,qa=ma; cb,sb,lb,qb=mb
    cost=0.0
    if ca!=cb:
        cost += 3.4 if 'resource' in (ca,cb) else 2.4
    if ca=='dialogue' and cb=='dialogue':
        cost += -0.45 if speakers_compatible(sa,sb) else 2.6
    ratio=lb/la
    cost += min(abs(math.log(max(ratio,0.05)/0.78)),2.5)*0.72
    if qa!=qb: cost+=0.35
    return cost
def unit_cost(a,b):
    return unit_cost_meta(text_meta(a),text_meta(b))

def gap_cost(s):
    typ,_=cls(s); n=cjklen(s)
    # short gasps / ellipses / one-word labels are commonly omitted by the old Chinese build.
    if typ=='dialogue' and n<=8:return 1.05
    if typ=='resource':return 1.25
    if n<=5:return 1.25
    if n<=12:return 1.60
    return 2.05

def merge_ok(parts):
    if len(parts)<2:return True
    kinds=[cls(x) for x in parts]
    if len({k[0] for k in kinds})!=1:return False
    if kinds[0][0]=='dialogue':
        return all(speakers_compatible(kinds[0][1],k[1]) for k in kinds[1:])
    if kinds[0][0]=='resource':return False
    return True

def align_full(A,B):
    n,m=len(A),len(B); INF=1e18
    dp=[[INF]*(m+1) for _ in range(n+1)]
    prev=[[None]*(m+1) for _ in range(n+1)]
    dp[0][0]=0.0
    for i in range(n+1):
      for j in range(m+1):
        cur=dp[i][j]
        if cur>=INF: continue
        def upd(ni,nj,c,t):
          v=cur+c
          if v<dp[ni][nj]: dp[ni][nj]=v;prev[ni][nj]=(i,j,t,c)
        if i<n and j<m: upd(i+1,j+1,unit_cost(A[i],B[j]),'1:1')
        if i<n: upd(i+1,j,gap_cost(A[i]),'1:0')
        if j<m: upd(i,j+1,gap_cost(B[j]),'0:1')
        if i<n and j+1<m and merge_ok([B[j],B[j+1]]):
            upd(i+1,j+2,unit_cost(A[i],B[j]+' '+B[j+1])+0.72,'1:2')
        if i+1<n and j<m and merge_ok([A[i],A[i+1]]):
            upd(i+2,j+1,unit_cost(A[i]+' '+A[i+1],B[j])+0.72,'2:1')
    out=[];i,j=n,m
    while i or j:
      p=prev[i][j]
      if p is None: raise RuntimeError((i,j))
      pi,pj,t,c=p;out.append((pi,i,pj,j,t,c));i,j=pi,pj
    out.reverse();return out,dp[n][m]
def align_banded(A,B,band=None):
    n,m=len(A),len(B); INF=1e18
    if band is None: band=48
    def allowed(i,j):
        if n==0:return j<=band
        center=(m*i)/n
        return abs(j-center)<=band or (i==0 and j<=band) or (i==n and m-j<=band)

    MA=[text_meta(x) for x in A]; MB=[text_meta(x) for x in B]
    GAP_A=[gap_cost(x) for x in A]; GAP_B=[gap_cost(x) for x in B]
    MERGE_A=[merge_ok([A[i],A[i+1]]) for i in range(max(0,n-1))]
    MERGE_B=[merge_ok([B[j],B[j+1]]) for j in range(max(0,m-1))]
    MA2=[text_meta(A[i]+' '+A[i+1]) for i in range(max(0,n-1))]
    MB2=[text_meta(B[j]+' '+B[j+1]) for j in range(max(0,m-1))]

    rows=[{} for _ in range(n+1)]
    prev={}
    rows[0][0]=0.0
    for i in range(n+1):
        center=(m*i/n) if n else 0
        jmin=max(0,int(center-band)-2)
        jmax=min(m,int(center+band)+2)
        if i==0:jmin=0
        if i==n:jmax=m
        for j in range(jmin,jmax+1):
            cur=rows[i].get(j,INF)
            if cur>=INF:continue
            def upd(ni,nj,c,t):
                if ni>n or nj>m or not allowed(ni,nj):return
                v=cur+c
                old=rows[ni].get(nj,INF)
                if v<old:
                    rows[ni][nj]=v
                    prev[(ni,nj)]=(i,j,t,c)
            if i<n and j<m: upd(i+1,j+1,unit_cost_meta(MA[i],MB[j]),'1:1')
            if i<n: upd(i+1,j,GAP_A[i],'1:0')
            if j<m: upd(i,j+1,GAP_B[j],'0:1')
            if i<n and j+1<m and MERGE_B[j]:
                upd(i+1,j+2,unit_cost_meta(MA[i],MB2[j])+0.72,'1:2')
            if i+1<n and j<m and MERGE_A[i]:
                upd(i+2,j+1,unit_cost_meta(MA2[i],MB[j])+0.72,'2:1')
    if m not in rows[n]:
        if band>=max(n,m)+4: raise RuntimeError(('banded-unreachable',n,m,band))
        return align_banded(A,B,min(max(n,m)+4,band*2))
    out=[];i,j=n,m
    while i or j:
        p=prev.get((i,j))
        if p is None:raise RuntimeError(('backtrace',i,j,n,m,band))
        pi,pj,t,c=p;out.append((pi,i,pj,j,t,c));i,j=pi,pj
    out.reverse()
    return out,rows[n][m]
# Production default: same transitions/costs as full DP, but constrained to a wide scaled diagonal.
def align(A,B):
    return align_banded(A,B)
def scene(jp,zh):
    J=extract(Path(jp).read_bytes(),'jp'); Z=extract(Path(zh).read_bytes(),'zh')
    A=[x[2] for x in J];B=[x[2] for x in Z]; ops,score=align(A,B);return J,Z,ops,score

def main(jp,zh,out):
    J,Z,ops,score=scene(jp,zh); Path(out).parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
      w=csv.writer(f,delimiter='\t');w.writerow(['jp_start','jp_end','zh_start','zh_end','op','cost','jp_text','zh_text'])
      for a,b,c,d,t,cost in ops:w.writerow([a,b,c,d,t,f'{cost:.4f}',' / '.join(clean(J[k][2]) for k in range(a,b)),' / '.join(clean(Z[k][2]) for k in range(c,d))])
    print('jp',len(J),'zh',len(Z),'ops',len(ops),'score',round(score,2),'oneone',sum(x[4]=='1:1' for x in ops),'gaps',sum(x[4] in ('1:0','0:1') for x in ops),'splitmerge',sum(x[4] in ('1:2','2:1') for x in ops))
    for row in ops[:100]:
      a,b,c,d,t,cost=row; print(t,f'{cost:.2f}',a,c,(' / '.join(clean(J[k][2]) for k in range(a,b))).encode('unicode_escape').decode(),' => ',(' / '.join(clean(Z[k][2]) for k in range(c,d))).encode('unicode_escape').decode())
if __name__=='__main__':main(*sys.argv[1:4])



