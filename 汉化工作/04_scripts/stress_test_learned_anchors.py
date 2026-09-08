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
            if len(cur)>=8:runs.append((sc,cur))
            cur=[]
        cur.append(p)
    if len(cur)>=8:runs.append((sc,cur))
print('truth_runs',len(runs),'maxrun',max(map(lambda x:len(x[1]),runs)))
rng=random.Random(20260907);cases=4000;tot_prop=tot_correct=tot_truth=exact_cases=0;wrong_examples=[];abstain=0
for c in range(cases):
    sc,run=rng.choice(runs);L=rng.randint(8,min(24,len(run)));start=rng.randint(0,len(run)-L);seg=run[start:start+L];J,Z=get(sc);Js=[J[j] for j,z in seg];Zs=[Z[z] for j,z in seg]
    truth={(i,i) for i in range(L)}
    mode=rng.choice(['extra-z-random','extra-j-random','extra-z-duplicate','extra-j-duplicate'])
    pos=rng.randint(0,L)
    if mode.startswith('extra-z'):
        if mode.endswith('duplicate'):
            src=rng.randrange(L);extra=Zs[src]
        else:
            extra=Z[rng.randrange(len(Z))]
        Zs=Zs[:pos]+[extra]+Zs[pos:]
        truth={(i, i if i<pos else i+1) for i in range(L)}
    else:
        if mode.endswith('duplicate'):
            src=rng.randrange(L);extra=Js[src]
        else:extra=J[rng.randrange(len(J))]
        Js=Js[:pos]+[extra]+Js[pos:]
        truth={(i if i<pos else i+1,i) for i in range(L)}
    prop=set(resolve(Js,Zs));correct=len(prop & truth);wrong=len(prop-truth)
    tot_prop+=len(prop);tot_correct+=correct;tot_truth+=len(truth);exact_cases+=int(wrong==0);abstain+=int(not prop)
    if wrong and len(wrong_examples)<15:wrong_examples.append((sc,mode,pos,len(prop),wrong,sorted(prop-truth)[:5]))
print('cases',cases,'proposed',tot_prop,'correct',tot_correct,'wrong',tot_prop-tot_correct,'precision',round(tot_correct/max(tot_prop,1),6),'recall',round(tot_correct/tot_truth,6),'cases_no_wrong',round(exact_cases/cases,6),'abstain_cases',abstain)
print('wrong_examples',wrong_examples)
