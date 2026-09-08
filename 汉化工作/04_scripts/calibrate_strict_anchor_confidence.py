from pathlib import Path
import sys,csv,re,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v3/all.tsv'
BLOCKS=ROOT/'03_text/matched/pc_control_parallel_v3/remaining_blocks.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v3/strict_anchor_candidates.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
R=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'));B=list(csv.DictReader(open(BLOCKS,encoding='utf-8-sig'),delimiter='\t'))
cache={}
def get(sc):
    if sc not in cache: cache[sc]=scene(ROOT,sc[4:])[:2]
    return cache[sc]
def tr(s):return s.strip(' \t\"')
def body(s):
    s=tr(s);s=re.sub(r'^【[^】]+】','',s);return s.strip(' \t\"「」（）()')
def kind(s):return 'dialogue' if tr(s).startswith('【') else 'narration'
def sp(s):
    m=re.match(r'^【([^】]+)】',tr(s));return m.group(1).strip(' \"') if m else ''
def hans(s):return {c for c in body(s) if '\u3400'<=c<='\u9fff'}
def vars_(s):return set(re.findall(r'[＊%％][Ａ-ＺA-Z]|\d+',body(s)))
def semantic(j,z):
    a,b=body(j['text']),body(z['text']); ha,hb=hans(a),hans(b);sh=len(ha&hb)
    if vars_(a)&vars_(b):return True
    if sh>=2:return True
    if sh>=1 and min(len(ha),len(hb))<=2 and max(len(a),len(b))<=24:return True
    # identical non-CJK token/onomatopoeia fragments of at least 3 chars
    aa=''.join(c for c in a if c.isascii() and (c.isalnum() or c in '!?-_/')).lower();bb=''.join(c for c in b if c.isascii() and (c.isalnum() or c in '!?-_/')).lower()
    return len(aa)>=3 and aa==bb
spc=collections.Counter();spp=collections.Counter();fpc=collections.Counter();fj=collections.Counter()
for r in R:
    if r['status'] not in SAFE:continue
    J,Z=get(r['scene']);j=J[int(r['jp_event_index'])];z=Z[int(r['zh_event_index'])];a,b=sp(j['text']),sp(z['text'])
    if a and b:spc[(a,b)]+=1;spp[a]+=1
    fpc[(j['fp'],z['fp'])]+=1;fj[j['fp']]+=1

def sp_ok(j,z):
    if kind(j['text'])!=kind(z['text']):return False
    if kind(j['text'])!='dialogue':return True
    a,b=sp(j['text']),sp(z['text'])
    if not a or not b:return True
    return spc[(a,b)]>=3 and spc[(a,b)]/max(spp[a],1)>=.05

def strong(j,z):
    if not sp_ok(j,z):return False
    fc=fpc[(j['fp'],z['fp'])];jt=fj[j['fp']];fr=fc/max(jt,1);a,b=sp(j['text']),sp(z['text']);sc=spc[(a,b)] if a and b else 0;sr=sc/max(spp[a],1) if a else 0
    rare=(jt<=500 and fc>=3 and fr>=.2)
    sem=semantic(j,z)
    semstruct=sem and ((fc>=2 and fr>=.01) or (a and b and sc>=20 and sr>=.5))
    return rare or semstruct

def lis(pairs):
    if not pairs:return []
    n=len(pairs);dp=[1]*n;pr=[-1]*n
    for i in range(n):
        for k in range(i):
            if pairs[k][1]<pairs[i][1] and dp[k]+1>dp[i]:dp[i]=dp[k]+1;pr[i]=k
    i=max(range(n),key=lambda x:dp[x]);o=[]
    while i>=0:o.append(pairs[i]);i=pr[i]
    return o[::-1]
def resolve_seq(Js,Zs):
    raw=[]
    for i,j in enumerate(Js):
        cand=[k for k,z in enumerate(Zs) if strong(j,z)]
        if len(cand)==1:raw.append((i,cand[0]))
    zc=collections.Counter(z for _,z in raw);raw=[p for p in raw if zc[p[1]]==1];an=lis(sorted(raw));prop=set(an);reason={p:'strict-anchor' for p in an}
    # fill only short equal gaps bounded by two real anchors
    for (ia,za),(ib,zb) in zip(an,an[1:]):
        ii=list(range(ia+1,ib));zz=list(range(za+1,zb))
        if ii and len(ii)==len(zz) and len(ii)<=6 and all(sp_ok(Js[x],Zs[y]) for x,y in zip(ii,zz)):
            for p in zip(ii,zz):prop.add(p);reason[p]='short-equal-between-strict-anchors'
    p=sorted(prop)
    if any(p[i][1]>=p[i+1][1] for i in range(len(p)-1)):return [],{}
    return p,reason
import random
# extra feature helpers
def feat(j,z):
    ha,hb=hans(body(j['text'])),hans(body(z['text'])); sh=len(ha&hb); vm=int(bool(vars_(body(j['text'])) & vars_(body(z['text'])))); fc=fpc[(j['fp'],z['fp'])];jt=fj[j['fp']];fr=fc/max(jt,1);a,b=sp(j['text']),sp(z['text']);sc=spc[(a,b)] if a and b else 0;sr=sc/max(spp[a],1) if a else 0
    return sh,vm,fc,jt,fr,sc,sr
by=collections.defaultdict(list)
for r in R:
    if r['status'] in SAFE:by[r['scene']].append((int(r['jp_event_index']),int(r['zh_event_index'])))
runs=[]
for sc,pairs in by.items():
    cur=[]
    for p in sorted(pairs):
        if cur and not(p[0]==cur[-1][0]+1 and p[1]==cur[-1][1]+1):
            if len(cur)>=12:runs.append((sc,cur))
            cur=[]
        cur.append(p)
    if len(cur)>=12:runs.append((sc,cur))
rng=random.Random(20260912); obs=[]
for c in range(5000):
    sc,run=rng.choice(runs);L=rng.randint(12,min(45,len(run)));st=rng.randint(0,len(run)-L);seg=run[st:st+L];J,Z=get(sc);Js=[J[j] for j,z in seg];Zs=[Z[z] for j,z in seg];truth=[(i,i) for i in range(L)]
    for q in range(rng.choice([1,1,2])):
        side=rng.choice('jz');pos=rng.randint(0,len(Js) if side=='j' else len(Zs));dup=rng.random()<.55
        if side=='z':
            extra=Zs[rng.randrange(len(Zs))] if dup else Z[rng.randrange(len(Z))];Zs=Zs[:pos]+[extra]+Zs[pos:];truth=[(a,b if b<pos else b+1) for a,b in truth]
        else:
            extra=Js[rng.randrange(len(Js))] if dup else J[rng.randrange(len(J))];Js=Js[:pos]+[extra]+Js[pos:];truth=[(a if a<pos else a+1,b) for a,b in truth]
    P,why=resolve_seq(Js,Zs);T=set(truth)
    for a,b in P:
        sh,vm,fc,jt,fr,scount,sr=feat(Js[a],Zs[b]);obs.append((int((a,b) in T),why[(a,b)],sh,vm,fc,jt,fr,scount,sr))
print('obs',len(obs),'wrong',sum(1-x[0] for x in obs))
def test(name,pred):
    x=[o for o in obs if pred(o)];w=sum(1-o[0] for o in x);print(name,'n',len(x),'wrong',w,'precision',round((len(x)-w)/max(len(x),1),6))
# o: correct,reason,sh,vm,fc,jt,fr,scount,sr
test('anchor_only',lambda o:o[1]=='strict-anchor')
test('anchor_sh>=1',lambda o:o[1]=='strict-anchor' and o[2]>=1)
test('anchor_sh>=2',lambda o:o[1]=='strict-anchor' and o[2]>=2)
test('anchor_sh>=3',lambda o:o[1]=='strict-anchor' and o[2]>=3)
test('anchor_sh>=4',lambda o:o[1]=='strict-anchor' and o[2]>=4)
test('anchor_var',lambda o:o[1]=='strict-anchor' and o[3])
test('rare500_fr50',lambda o:o[1]=='strict-anchor' and o[5]<=500 and o[6]>=.5 and o[4]>=3)
test('rare100_fr70',lambda o:o[1]=='strict-anchor' and o[5]<=100 and o[6]>=.7 and o[4]>=3)
test('generic_sem3',lambda o:o[1]=='strict-anchor' and o[2]>=3 and o[4]>=2)
test('combo1',lambda o:o[1]=='strict-anchor' and ((o[3]) or (o[2]>=3) or (o[5]<=100 and o[6]>=.7 and o[4]>=3)))
test('combo2',lambda o:o[1]=='strict-anchor' and ((o[3]) or (o[2]>=4) or (o[5]<=100 and o[6]>=.8 and o[4]>=5)))
test('combo3',lambda o:o[1]=='strict-anchor' and ((o[3] and o[4]>=2) or (o[2]>=4) or (o[5]<=50 and o[6]>=.8 and o[4]>=5)))
# bins
for sh in range(0,7):test('sh='+str(sh),lambda o,sh=sh:o[1]=='strict-anchor' and o[2]==sh)
