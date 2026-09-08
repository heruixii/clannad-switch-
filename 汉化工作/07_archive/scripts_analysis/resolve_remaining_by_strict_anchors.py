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
rows=[]
for b in B:
    if int(b['jp_count'])==0 or int(b['zh_count'])==0:continue
    J,Z=get(b['scene']);js=list(range(int(b['jp_start']),int(b['jp_end'])+1));zs=list(range(int(b['zh_start']),int(b['zh_end'])+1));P,why=resolve_seq([J[i] for i in js],[Z[i] for i in zs])
    for a,bz in P:
        ji,zi=js[a],zs[bz];j,z=J[ji],Z[zi];rows.append({'scene':b['scene'],'block_id':b['block_id'],'jp_event_index':ji,'zh_event_index':zi,'reason':why[(a,bz)],'semantic':int(semantic(j,z)),'fp_pair_count':fpc[(j['fp'],z['fp'])],'jp_fp_total':fj[j['fp']],'jp_text':j['text'],'zh_text':z['text']})
fields=['scene','block_id','jp_event_index','zh_event_index','reason','semantic','fp_pair_count','jp_fp_total','jp_text','zh_text']
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
print('pairs',len(rows),'anchors',sum(r['reason']=='strict-anchor' for r in rows),'fills',sum(r['reason']!='strict-anchor' for r in rows),'blocks',len(set((r['scene'],r['block_id']) for r in rows)));print('trap1516',[(r['jp_event_index'],r['zh_event_index']) for r in rows if r['scene']=='SEEN1516' and r['jp_event_index'] in (152,153)]);print('trap6502',[(r['jp_event_index'],r['zh_event_index']) for r in rows if r['scene']=='SEEN6502' and r['jp_event_index'] in (75,76)]);print('out',OUT)
