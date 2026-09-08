from pathlib import Path
import sys,csv,re,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/'03_text/matched/pc_control_parallel_v3'
OUT=ROOT/'03_text/matched/pc_control_parallel_v4'; OUT.mkdir(parents=True,exist_ok=True)
BASE_SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
R=list(csv.DictReader(open(IN/'all.tsv',encoding='utf-8-sig'),delimiter='\t'))
cache={}
def get(sc):
    if sc not in cache: cache[sc]=scene(ROOT,sc[4:])[:2]
    return cache[sc]
def tr(s):return s.strip(' \t\"')
def body(s):s=tr(s);s=re.sub(r'^【[^】]+】','',s);return s.strip(' \t\"「」（）()')
def kind(s):return 'dialogue' if tr(s).startswith('【') else 'narration'
def sp(s):
    m=re.match(r'^【([^】]+)】',tr(s));return m.group(1).strip(' \"') if m else ''
def hans(s):return {c for c in body(s) if '\u3400'<=c<='\u9fff'}
def vars_(s):return set(re.findall(r'[＊%％][Ａ-ＺA-Z]|\d+',body(s)))
def clean_zh(s):
    s=s.strip()
    while len(s)>=2 and s[0]=='"' and s[-1]=='"':s=s[1:-1]
    return s
# Freeze all learned statistics at v3 baseline only.
spc=collections.Counter();spp=collections.Counter();fpc=collections.Counter();fj=collections.Counter()
for r in R:
    if r['status'] not in BASE_SAFE:continue
    J,Z=get(r['scene']);j=J[int(r['jp_event_index'])];z=Z[int(r['zh_event_index'])];a,b=sp(j['text']),sp(z['text'])
    if a and b:spc[(a,b)]+=1;spp[a]+=1
    fpc[(j['fp'],z['fp'])]+=1;fj[j['fp']]+=1

def sp_ok(j,z):
    if kind(j['text'])!=kind(z['text']):return False
    if kind(j['text'])!='dialogue':return True
    a,b=sp(j['text']),sp(z['text'])
    if not a or not b:return True
    return spc[(a,b)]>=3 and spc[(a,b)]/max(spp[a],1)>=.05

def strict_raw(j,z):
    if not sp_ok(j,z):return False
    fc=fpc[(j['fp'],z['fp'])];jt=fj[j['fp']];fr=fc/max(jt,1);a,b=sp(j['text']),sp(z['text']);sc=spc[(a,b)] if a and b else 0;sr=sc/max(spp[a],1) if a else 0
    ha,hb=hans(j['text']),hans(z['text']);sh=len(ha&hb);vm=bool(vars_(j['text'])&vars_(z['text']))
    sem=vm or sh>=2 or (sh>=1 and min(len(ha),len(hb))<=2 and max(len(body(j['text'])),len(body(z['text'])))<=24)
    rare=(jt<=500 and fc>=3 and fr>=.2)
    semstruct=sem and ((fc>=2 and fr>=.01) or (a and b and sc>=20 and sr>=.5))
    return rare or semstruct

def highconf(j,z):
    fc=fpc[(j['fp'],z['fp'])];jt=fj[j['fp']];fr=fc/max(jt,1);sh=len(hans(j['text'])&hans(z['text']));vm=bool(vars_(j['text'])&vars_(z['text']))
    return vm or (jt<=500 and fc>=3 and fr>=.5) or sh>=6

def lis(pairs):
    if not pairs:return []
    n=len(pairs);dp=[1]*n;pr=[-1]*n
    for i in range(n):
        for k in range(i):
            if pairs[k][1]<pairs[i][1] and dp[k]+1>dp[i]:dp[i]=dp[k]+1;pr[i]=k
    i=max(range(n),key=lambda x:dp[x]);o=[]
    while i>=0:o.append(pairs[i]);i=pr[i]
    return o[::-1]
def row_for(sc,ji,zi,it):
    J,Z=get(sc);j,z=J[ji],Z[zi];zt=clean_zh(z['text']);fc=fpc[(j['fp'],z['fp'])];jt=fj[j['fp']];sh=len(hans(j['text'])&hans(z['text']));vm=bool(vars_(j['text'])&vars_(z['text']))
    reason='var' if vm else ('rare-fp' if jt<=500 and fc>=3 and fc/max(jt,1)>=.5 else 'shared-han>=6')
    return {'scene':sc,'segment':f'highconf-i{it}','jp_event_index':ji,'zh_event_index':zi,'status':'highconf-anchor','reason':f'{reason};iter={it};fp={fc}/{jt};sh={sh}',
      'jp_text_id':j['text_id'],'zh_text_id':z['text_id'],'jp_kidoku_id':j['kidoku_id'],'zh_kidoku_id':z['kidoku_id'],'jp_offset':j['text_offset'],'zh_offset':z['text_offset'],
      'jp_kind':kind(j['text']),'zh_kind':kind(zt),'jp_speaker':sp(j['text']),'zh_speaker':sp(zt),'jp_text':j['text'],'zh_text':zt}
# Start with all v3 safe pairs as immutable anchors; review rows stay in R until consumed.
current={(r['scene'],int(r['jp_event_index']),int(r['zh_event_index'])) for r in R if r['status'] in BASE_SAFE}
adds=[]
for it in range(1,21):
    proposed=[]
    by=collections.defaultdict(list)
    for sc,ji,zi in current:by[sc].append((ji,zi))
    for sc in sorted({r['scene'] for r in R}):
        J,Z=get(sc); aa=[(-1,-1)]+sorted(by[sc])+[(len(J),len(Z))]
        for (ja,za),(jb,zb) in zip(aa,aa[1:]):
            js=list(range(ja+1,jb));zs=list(range(za+1,zb))
            if not js or not zs:continue
            raw=[]
            for ji in js:
                cand=[zi for zi in zs if strict_raw(J[ji],Z[zi])]
                if len(cand)==1 and highconf(J[ji],Z[cand[0]]):raw.append((ji,cand[0]))
            zc=collections.Counter(z for _,z in raw);raw=[p for p in raw if zc[p[1]]==1]
            for ji,zi in lis(sorted(raw)):proposed.append((sc,ji,zi))
    proposed=[p for p in proposed if p not in current]
    # global uniqueness / monotonicity is inherent by interval; verify anyway
    if not proposed:
        print('iteration',it,'added',0,'converged');break
    assert len({(s,j) for s,j,z in proposed})==len(proposed)
    assert len({(s,z) for s,j,z in proposed})==len(proposed)
    for p in proposed:current.add(p);adds.append(row_for(*p,it))
    print('iteration',it,'added',len(proposed),'cumulative',len(adds))
else:print('WARNING max iterations reached')
# Merge: remove only review rows whose endpoint was consumed by a new pair.
aj={(r['scene'],str(r['jp_event_index'])) for r in adds};az={(r['scene'],str(r['zh_event_index'])) for r in adds}
kept=[]
for r in R:
    if r['status'].startswith('review-') and ((r['jp_event_index'] and (r['scene'],r['jp_event_index']) in aj) or (r['zh_event_index'] and (r['scene'],r['zh_event_index']) in az)):continue
    kept.append(r)
allrows=kept+adds
allrows.sort(key=lambda r:(r['scene'],int(r['jp_event_index']) if str(r['jp_event_index']) else 10**9+int(r['zh_event_index'])))
fields=['scene','segment','jp_event_index','zh_event_index','status','reason','jp_text_id','zh_text_id','jp_kidoku_id','zh_kidoku_id','jp_offset','zh_offset','jp_kind','zh_kind','jp_speaker','zh_speaker','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(allrows)
for sc in sorted(set(r['scene'] for r in allrows)):
    rr=[r for r in allrows if r['scene']==sc]
    with open(OUT/f'{sc}.tsv','w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rr)
C=collections.Counter(r['status'] for r in allrows);safe_status=BASE_SAFE|{'highconf-anchor'};safe=sum(C[s] for s in safe_status)
# monotonic QA
bad=[]
for sc in sorted(set(r['scene'] for r in allrows)):
    pp=sorted((int(r['jp_event_index']),int(r['zh_event_index'])) for r in allrows if r['scene']==sc and r['status'] in safe_status)
    if any(pp[i][1]>=pp[i+1][1] for i in range(len(pp)-1)):bad.append(sc)
print('added_total',len(adds),'safe',safe,'safe_pct',round(100*safe/98955,3),'review_jp',C['review-jp'],'review_zh',C['review-zh'],'type_review',C['review-type-mismatch'],'bad_monotonic',bad)
print('out',OUT)
