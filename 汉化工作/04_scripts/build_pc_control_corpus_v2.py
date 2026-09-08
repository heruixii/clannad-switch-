from pathlib import Path
import sys,csv,re,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
V1=ROOT/'03_text/matched/pc_control_parallel_v1'
OUT=ROOT/'03_text/matched/pc_control_parallel_v2'; OUT.mkdir(parents=True,exist_ok=True)

def trim(s): return s.strip(' \t"')
def kind(s): return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker(s):
    m=re.match(r'^【([^】]+)】',trim(s)); return m.group(1) if m else ''
def clean_zh(s):
    s=s.strip()
    while len(s)>=2 and s[0]=='"' and s[-1]=='"': s=s[1:-1]
    return s

base=list(csv.DictReader(open(V1/'all.tsv',encoding='utf-8-sig'),delimiter='\t'))
blocks=list(csv.DictReader(open(V1/'review_gap_candidates_v1.tsv',encoding='utf-8-sig'),delimiter='\t'))
# map current rows by scene/event index for replacement/upgrades
by_scene=collections.defaultdict(list)
for r in base: by_scene[r['scene']].append(r)
upgrades=[]
for b in blocks:
    if b['decision']!='unique-structural': continue
    sc=b['scene']; J,Z,A=scene(ROOT,sc[4:])
    js=list(range(int(b['jp_start']),int(b['jp_end'])+1)); zs=list(range(int(b['zh_start']),int(b['zh_end'])+1)); k=int(b['skip_local_index'])
    if b['skip_side']=='skip-zh': pairs=list(zip(js,[z for n,z in enumerate(zs) if n!=k]))
    else: pairs=list(zip([j for n,j in enumerate(js) if n!=k],zs))
    for ji,zi in pairs:
        jt=J[ji]['text']; zt=clean_zh(Z[zi]['text'])
        upgrades.append({'scene':sc,'segment':f"gap-{b['block_id']}",'jp_event_index':ji,'zh_event_index':zi,'status':'unique-gap','reason':f"{b['skip_side']}:{b['skip_event_index']}",
            'jp_text_id':J[ji]['text_id'],'zh_text_id':Z[zi]['text_id'],'jp_kidoku_id':J[ji]['kidoku_id'],'zh_kidoku_id':Z[zi]['kidoku_id'],'jp_offset':J[ji]['text_offset'],'zh_offset':Z[zi]['text_offset'],
            'jp_kind':kind(jt),'zh_kind':kind(zt),'jp_speaker':speaker(jt),'zh_speaker':speaker(zt),'jp_text':jt,'zh_text':zt})

# Replace only review rows addressed by upgrades; preserve all other base rows.
uj={(r['scene'],str(r['jp_event_index'])) for r in upgrades}; uz={(r['scene'],str(r['zh_event_index'])) for r in upgrades}
kept=[]
for r in base:
    jkey=(r['scene'],r['jp_event_index']); zkey=(r['scene'],r['zh_event_index'])
    if r['status'].startswith('review-') and ((r['jp_event_index'] and jkey in uj) or (r['zh_event_index'] and zkey in uz)):
        continue
    kept.append(r)
allrows=kept+upgrades
# stable sort using available event indices; JP-first, then ZH-only rows
allrows.sort(key=lambda r:(r['scene'], int(r['jp_event_index']) if str(r['jp_event_index'])!='' else 10**9+int(r['zh_event_index'])))
fields=['scene','segment','jp_event_index','zh_event_index','status','reason','jp_text_id','zh_text_id','jp_kidoku_id','zh_kidoku_id','jp_offset','zh_offset','jp_kind','zh_kind','jp_speaker','zh_speaker','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(allrows)
# per-scene and summary
summary=[]
for sc in sorted(set(r['scene'] for r in allrows)):
    rows=[r for r in allrows if r['scene']==sc]
    with open(OUT/f'{sc}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
    c=collections.Counter(r['status'] for r in rows); summary.append((sc,c))
with open(OUT/'summary.tsv','w',encoding='utf-8-sig',newline='') as f:
    statuses=sorted(set(k for _,c in summary for k in c)); w=csv.writer(f,delimiter='\t');w.writerow(['scene']+statuses)
    for sc,c in summary:w.writerow([sc]+[c[s] for s in statuses])
C=collections.Counter(r['status'] for r in allrows); safe=sum(C[s] for s in ('anchor','equal-segment','unique-gap'))
print('upgrades',len(upgrades));print('status',json.dumps(C,ensure_ascii=False,sort_keys=True));print('safe',safe,'safe_pct_jp',round(100*safe/98955,3));print('out',OUT)
