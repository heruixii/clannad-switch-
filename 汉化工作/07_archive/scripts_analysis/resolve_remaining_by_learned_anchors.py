from pathlib import Path
import sys,csv,re,collections,math,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v3/all.tsv'
BLOCKS=ROOT/'03_text/matched/pc_control_parallel_v3/remaining_blocks.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v3/learned_anchor_candidates.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
R=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'))
B=list(csv.DictReader(open(BLOCKS,encoding='utf-8-sig'),delimiter='\t'))
cache={}
def get(sc):
    if sc not in cache: cache[sc]=scene(ROOT,sc[4:])[:2]
    return cache[sc]
def tr(s): return s.strip(' \t\"')
def kind(s): return 'dialogue' if tr(s).startswith('【') else 'narration'
def sp(s):
    m=re.match(r'^【([^】]+)】',tr(s)); return m.group(1).strip(' \"') if m else ''
# learn speaker and fp pair mappings from safe set
spc=collections.Counter(); spp=collections.Counter(); fpc=collections.Counter(); fj=collections.Counter()
for r in R:
    if r['status'] not in SAFE: continue
    J,Z=get(r['scene']); ji=int(r['jp_event_index']);zi=int(r['zh_event_index']); a=sp(J[ji]['text']);b=sp(Z[zi]['text'])
    if a and b: spc[(a,b)]+=1;spp[a]+=1
    fpc[(J[ji]['fp'],Z[zi]['fp'])]+=1;fj[J[ji]['fp']]+=1

def sp_ok(j,z):
    a,b=sp(j['text']),sp(z['text'])
    if kind(j['text'])!=kind(z['text']): return False
    if kind(j['text'])!='dialogue': return True
    if not a or not b:return True
    c=spc[(a,b)]; total=spp[a]
    return c>=3 and c/max(total,1)>=0.05

def strong_pair(j,z):
    if not sp_ok(j,z): return False
    fc=fpc[(j['fp'],z['fp'])]; fr=fc/max(fj[j['fp']],1)
    a,b=sp(j['text']),sp(z['text'])
    sc=spc[(a,b)] if a and b else 0
    sr=sc/max(spp[a],1) if a else 0
    # exact/learned control relation, or a highly stable speaker identity plus a non-generic fp relation
    return (fc>=5 and fr>=0.05) or (j['fp']==z['fp'] and fj[j['fp']]>=2) or (a and b and sc>=20 and sr>=0.5 and fc>=2)

def lis(pairs):
    # longest increasing on z; pairs already sorted by j, unique endpoints
    if not pairs:return []
    n=len(pairs);dp=[1]*n;prev=[-1]*n
    for i in range(n):
        for k in range(i):
            if pairs[k][1]<pairs[i][1] and dp[k]+1>dp[i]:dp[i]=dp[k]+1;prev[i]=k
    i=max(range(n),key=lambda x:dp[x]); out=[]
    while i>=0:out.append(pairs[i]);i=prev[i]
    return out[::-1]
rows=[]; stats=collections.Counter(); total_pairs=0
for b in B:
    nj,nz=int(b['jp_count']),int(b['zh_count'])
    if nj==0 or nz==0: continue
    J,Z=get(b['scene']); js=list(range(int(b['jp_start']),int(b['jp_end'])+1));zs=list(range(int(b['zh_start']),int(b['zh_end'])+1))
    raw=[]
    for ji in js:
        cand=[zi for zi in zs if strong_pair(J[ji],Z[zi])]
        if len(cand)==1: raw.append((ji,cand[0]))
    # reciprocal uniqueness
    zcount=collections.Counter(z for _,z in raw); raw=[p for p in raw if zcount[p[1]]==1]
    anchors=lis(sorted(raw))
    # include virtual boundaries; only map equal-count gaps with compatible rowwise identity
    proposed=[]; reason={}
    aa=[(js[0]-1,zs[0]-1)]+anchors+[(js[-1]+1,zs[-1]+1)]
    for ji,zi in anchors: proposed.append((ji,zi));reason[(ji,zi)]='learned-anchor'
    for (ja,za),(jb,zb) in zip(aa,aa[1:]):
        jj=list(range(ja+1,jb)); zz=list(range(za+1,zb))
        if len(jj)==len(zz) and jj:
            if all(sp_ok(J[x],Z[y]) for x,y in zip(jj,zz)):
                for x,y in zip(jj,zz): proposed.append((x,y));reason[(x,y)]='equal-between-learned-anchors'
    # unique and monotonic
    proposed=sorted(set(proposed));
    if any(proposed[i][1]>=proposed[i+1][1] for i in range(len(proposed)-1)): proposed=[]
    for ji,zi in proposed:
        rows.append({'scene':b['scene'],'block_id':b['block_id'],'jp_event_index':ji,'zh_event_index':zi,'reason':reason[(ji,zi)],'jp_text':J[ji]['text'],'zh_text':Z[zi]['text'],'jp_speaker':sp(J[ji]['text']),'zh_speaker':sp(Z[zi]['text']),'jp_fp':J[ji]['fp'],'zh_fp':Z[zi]['fp'],'fp_pair_count':fpc[(J[ji]['fp'],Z[zi]['fp'])]})
    stats['blocks_with_pairs']+=bool(proposed);stats['anchors']+=sum(reason[p]=='learned-anchor' for p in proposed);stats['equal_fill']+=sum(reason[p]=='equal-between-learned-anchors' for p in proposed);total_pairs+=len(proposed)
fields=['scene','block_id','jp_event_index','zh_event_index','reason','jp_speaker','zh_speaker','jp_fp','zh_fp','fp_pair_count','jp_text','zh_text']
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
print('pairs',total_pairs,'blocks_with_pairs',stats['blocks_with_pairs'],'anchors',stats['anchors'],'equal_fill',stats['equal_fill'],'unique_jp',len({(r['scene'],r['jp_event_index']) for r in rows}),'unique_zh',len({(r['scene'],r['zh_event_index']) for r in rows}));print('out',OUT)
