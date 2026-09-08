from pathlib import Path
import sys,csv,re,collections,random
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v3/all.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
R=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'))
cache={}
def get(sc):
    if sc not in cache: cache[sc]=scene(ROOT,sc[4:])[:2]
    return cache[sc]
def tr(s):return s.strip(' \t\"')
def kind(s):return 'dialogue' if tr(s).startswith('【') else 'narration'
def sp(s):
    m=re.match(r'^【([^】]+)】',tr(s));return m.group(1).strip(' \"') if m else ''
spc=collections.Counter();spp=collections.Counter();fpc=collections.Counter();fj=collections.Counter()
for r in R:
    if r['status'] not in SAFE:continue
    J,Z=get(r['scene']);ji=int(r['jp_event_index']);zi=int(r['zh_event_index']);a=sp(J[ji]['text']);b=sp(Z[zi]['text'])
    if a and b:spc[(a,b)]+=1;spp[a]+=1
    fpc[(J[ji]['fp'],Z[zi]['fp'])]+=1;fj[J[ji]['fp']]+=1

def sp_ok(j,z):
    a,b=sp(j['text']),sp(z['text'])
    if kind(j['text'])!=kind(z['text']):return False
    if kind(j['text'])!='dialogue':return True
    if not a or not b:return True
    return spc[(a,b)]>=3 and spc[(a,b)]/max(spp[a],1)>=.05

def strong(j,z):
    if not sp_ok(j,z):return False
    fc=fpc[(j['fp'],z['fp'])];fr=fc/max(fj[j['fp']],1);a,b=sp(j['text']),sp(z['text']);sc=spc[(a,b)] if a and b else 0;sr=sc/max(spp[a],1) if a else 0
    return (fc>=5 and fr>=.05) or (j['fp']==z['fp'] and fj[j['fp']]>=2) or (a and b and sc>=20 and sr>=.5 and fc>=2)

def lis(pairs):
    if not pairs:return []
    n=len(pairs);dp=[1]*n;pr=[-1]*n
    for i in range(n):
        for k in range(i):
            if pairs[k][1]<pairs[i][1] and dp[k]+1>dp[i]:dp[i]=dp[k]+1;pr[i]=k
    i=max(range(n),key=lambda x:dp[x]);o=[]
    while i>=0:o.append(pairs[i]);i=pr[i]
    return o[::-1]

def resolve(Js,Zs):
    raw=[]
    for i,j in enumerate(Js):
        cand=[k for k,z in enumerate(Zs) if strong(j,z)]
        if len(cand)==1:raw.append((i,cand[0]))
    zc=collections.Counter(z for _,z in raw);raw=[p for p in raw if zc[p[1]]==1]
    an=lis(sorted(raw));prop=set(an);aa=[(-1,-1)]+an+[(len(Js),len(Zs))]
    for (ia,za),(ib,zb) in zip(aa,aa[1:]):
        ii=list(range(ia+1,ib));zz=list(range(za+1,zb))
        if len(ii)==len(zz) and ii and all(sp_ok(Js[x],Zs[y]) for x,y in zip(ii,zz)):prop.update(zip(ii,zz))
    p=sorted(prop)
    if any(p[i][1]>=p[i+1][1] for i in range(len(p)-1)):return []
    return p
# Build consecutive safe truth runs
by=collections.defaultdict(list)
for r in R:
    if r['status'] in SAFE:by[r['scene']].append((int(r['jp_event_index']),int(r['zh_event_index'])))
runs=[]
for sc,pairs in by.items():
    pairs=sorted(pairs);cur=[]
    for p in pairs:
        if cur and not (p[0]==cur[-1][0]+1 and p[1]==cur[-1][1]+1):
            if len(cur)>=18:runs.append((sc,cur))
            cur=[]
        cur.append(p)
    if len(cur)>=18:runs.append((sc,cur))
print('truth_runs',len(runs),'maxrun',max(len(x[1]) for x in runs))
rng=random.Random(20260908);cases=3000;tot=ok=truthn=zero=clean=0;bad=[]
for c in range(cases):
    sc,run=rng.choice(runs);L=rng.randint(18,min(48,len(run)));st=rng.randint(0,len(run)-L);seg=run[st:st+L];J,Z=get(sc)
    Js=[J[j] for j,z in seg]; Zs=[Z[z] for j,z in seg]; truth=[(i,i) for i in range(L)]
    # perform two independent insertions, possibly on same side; update truth coordinates after each insertion
    for q in range(2):
        side=rng.choice(['j','z']);pos=rng.randint(0,len(Js) if side=='j' else len(Zs));dup=rng.random()<0.6
        if side=='z':
            extra=Zs[rng.randrange(len(Zs))] if dup else Z[rng.randrange(len(Z))]
            Zs=Zs[:pos]+[extra]+Zs[pos:]; truth=[(a,b if b<pos else b+1) for a,b in truth]
        else:
            extra=Js[rng.randrange(len(Js))] if dup else J[rng.randrange(len(J))]
            Js=Js[:pos]+[extra]+Js[pos:]; truth=[(a if a<pos else a+1,b) for a,b in truth]
    T=set(truth);P=set(resolve(Js,Zs));w=P-T;tot+=len(P);ok+=len(P&T);truthn+=len(T);zero+=int(not P);clean+=int(not w)
    if w and len(bad)<12:bad.append((sc,len(P),len(w),sorted(w)[:5]))
print('cases',cases,'proposed',tot,'correct',ok,'wrong',tot-ok,'precision',round(ok/max(tot,1),6),'recall',round(ok/truthn,6),'cases_no_wrong',round(clean/cases,6),'abstain',zero)
print('wrong_examples',bad)
