from pathlib import Path
import sys,csv,collections,re,difflib,json,math
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
BLOCKS=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
MOD1=1000000007;MOD2=1000000009;INF=10**9

def trim(s):return (s or '').strip(' \t\"')
def kind(s):return 'D' if trim(s).startswith('【') else 'N'
def speaker(s):
 m=re.match(r'^【([^】]+)】',trim(s));return m.group(1).strip(' \"') if m else ''
def block_sim(a,b):return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
# learn JP->ZH speaker variants from trusted pairs
rows=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'))
spcnt=collections.defaultdict(collections.Counter)
for r in rows:
 if r['status'] not in SAFE:continue
 a,b=speaker(r['jp_text']),speaker(r['zh_text'])
 if a and b:spcnt[a][b]+=1
spmap={}
for a,c in spcnt.items():
 total=sum(c.values()); mx=c.most_common(1)[0][1]
 # retain observed variants with meaningful support, but never a one-off anomaly if corpus is large
 spmap[a]={b for b,n in c.items() if n>=2 or total<5 or n/total>=0.05}

def compatible(j,z):
 if kind(j['text'])!=kind(z['text']):return False
 if kind(j['text'])=='N':return True
 a,b=speaker(j['text']),speaker(z['text'])
 if not a or not b:return False
 if a in spmap:return b in spmap[a]
 return a==b

def align_forced(J,Z,js,zs):
 n,m=len(js),len(zs)
 # DP minimal gaps, matches cost 0, gaps 1, no substitutions
 F=[[INF]*(m+1) for _ in range(n+1)]; C1=[[0]*(m+1) for _ in range(n+1)]; C2=[[0]*(m+1) for _ in range(n+1)]
 F[0][0]=0;C1[0][0]=C2[0][0]=1
 for i in range(n+1):
  for j in range(m+1):
   if i==0 and j==0:continue
   best=INF; ways=[]
   if i>0:
    v=F[i-1][j]+1
    if v<best:best=v;ways=[(C1[i-1][j],C2[i-1][j])]
    elif v==best:ways.append((C1[i-1][j],C2[i-1][j]))
   if j>0:
    v=F[i][j-1]+1
    if v<best:best=v;ways=[(C1[i][j-1],C2[i][j-1])]
    elif v==best:ways.append((C1[i][j-1],C2[i][j-1]))
   if i>0 and j>0 and compatible(J[js[i-1]],Z[zs[j-1]]):
    v=F[i-1][j-1]
    if v<best:best=v;ways=[(C1[i-1][j-1],C2[i-1][j-1])]
    elif v==best:ways.append((C1[i-1][j-1],C2[i-1][j-1]))
   F[i][j]=best;C1[i][j]=sum(x for x,y in ways)%MOD1;C2[i][j]=sum(y for x,y in ways)%MOD2
 # backward
 B=[[INF]*(m+1) for _ in range(n+1)];D1=[[0]*(m+1) for _ in range(n+1)];D2=[[0]*(m+1) for _ in range(n+1)]
 B[n][m]=0;D1[n][m]=D2[n][m]=1
 for i in range(n,-1,-1):
  for j in range(m,-1,-1):
   if i==n and j==m:continue
   best=INF;ways=[]
   if i<n:
    v=B[i+1][j]+1
    if v<best:best=v;ways=[(D1[i+1][j],D2[i+1][j])]
    elif v==best:ways.append((D1[i+1][j],D2[i+1][j]))
   if j<m:
    v=B[i][j+1]+1
    if v<best:best=v;ways=[(D1[i][j+1],D2[i][j+1])]
    elif v==best:ways.append((D1[i][j+1],D2[i][j+1]))
   if i<n and j<m and compatible(J[js[i]],Z[zs[j]]):
    v=B[i+1][j+1]
    if v<best:best=v;ways=[(D1[i+1][j+1],D2[i+1][j+1])]
    elif v==best:ways.append((D1[i+1][j+1],D2[i+1][j+1]))
   B[i][j]=best;D1[i][j]=sum(x for x,y in ways)%MOD1;D2[i][j]=sum(y for x,y in ways)%MOD2
 total=F[n][m];tc1=C1[n][m];tc2=C2[n][m];forced=[];onopt=[]
 for i in range(n):
  for j in range(m):
   if not compatible(J[js[i]],Z[zs[j]]):continue
   if F[i][j]+B[i+1][j+1]!=total:continue
   w1=(C1[i][j]*D1[i+1][j+1])%MOD1;w2=(C2[i][j]*D2[i+1][j+1])%MOD2
   onopt.append((i,j))
   if w1==tc1 and w2==tc2:forced.append((i,j))
 return total,forced,onopt,(tc1,tc2)

def main():
 bs=list(csv.DictReader(open(BLOCKS,encoding='utf-8-sig'),delimiter='\t')); out=[];stats=collections.Counter(); cache={}
 for bi,b in enumerate(bs):
  nj,nz=int(b['jp_count']),int(b['zh_count'])
  if nj==nz or nj==0 or nz==0:continue
  sc=b['scene']
  if sc not in cache:cache[sc]=scene(ROOT,sc[4:])[:2]
  J,Z=cache[sc]
  js=list(range(int(b['jp_start']),int(b['jp_end'])+1));zs=list(range(int(b['zh_start']),int(b['zh_end'])+1))
  cost,forced,onopt,ways=align_forced(J,Z,js,zs);stats['blocks']+=1;stats['forced_raw']+=len(forced)
  for ii,jj in forced:
   ji,zi=js[ii],zs[jj];j,z=J[ji],Z[zi]; sim=block_sim(j['block'],z['block']); fp=j['fp']==z['fp']; k=kind(j['text']); spok=(k=='D')
   # Hard acceptance: exact fp, or strong block similarity. Dialogue also has learned-speaker compatibility by construction.
   accept=fp or sim>=0.86
   if accept:stats['accepted']+=1
   else:stats['rejected_low_control']+=1
   out.append({'scene':sc,'block_index':bi,'jp_event_index':ji,'zh_event_index':zi,'jp_count':nj,'zh_count':nz,'edit_cost':cost,'optimal_paths_mod1':ways[0],'optimal_paths_mod2':ways[1],'block_similarity':round(sim,5),'fp_exact':int(fp),'kind':k,'jp_speaker':speaker(j['text']),'zh_speaker':speaker(z['text']),'accepted':int(accept),'jp_text':j['text'],'zh_text':z['text']})
 with open(OUT,'w',encoding='utf-8-sig',newline='') as f:
  fields=list(out[0]);w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
 print(json.dumps(dict(stats),ensure_ascii=False,indent=2));print('out',OUT)
if __name__=='__main__':main()
