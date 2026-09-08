from pathlib import Path
import sys,csv,re,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
V2=ROOT/'03_text/matched/pc_control_parallel_v2'
GAPS=ROOT/'03_text/matched/pc_control_parallel_v1/review_gap_candidates_v1.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v3'; OUT.mkdir(parents=True,exist_ok=True)

APPROVED_FULL={
 ('SEEN0428','4'),('SEEN0429','0'),('SEEN1511','7'),('SEEN2426','0'),
 ('SEEN2506','0'),('SEEN2510','0'),('SEEN2514','4'),('SEEN5421','0'),
 ('SEEN6419','0'),('SEEN6729','4'),('SEEN6800','0'),('SEEN7100','4'),('SEEN7500','1'),
}
# Human-confirmed safe tails/heads from two blocks whose core contains a merge/omission.
APPROVED_PARTIAL={
 ('SEEN1516','0'):[(151,151),(154,153),(155,154),(156,155)],
 ('SEEN6502','1'):[(72,74),(73,75),(74,76),(77,78)],
}

def trim(s): return s.strip(' \t\"')
def kind(s): return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker(s):
    m=re.match(r'^【([^】]+)】',trim(s)); return m.group(1) if m else ''
def clean_zh(s):
    s=s.strip()
    while len(s)>=2 and s[0]=='\"' and s[-1]=='\"': s=s[1:-1]
    return s

def mkrow(sc,block,ji,zi,reason):
    J,Z,A=scene(ROOT,sc[4:]); jt=J[ji]['text']; zt=clean_zh(Z[zi]['text'])
    return {'scene':sc,'segment':f'confirmed-gap-{block}','jp_event_index':ji,'zh_event_index':zi,
      'status':'confirmed-gap','reason':reason,
      'jp_text_id':J[ji]['text_id'],'zh_text_id':Z[zi]['text_id'],
      'jp_kidoku_id':J[ji]['kidoku_id'],'zh_kidoku_id':Z[zi]['kidoku_id'],
      'jp_offset':J[ji]['text_offset'],'zh_offset':Z[zi]['text_offset'],
      'jp_kind':kind(jt),'zh_kind':kind(zt),'jp_speaker':speaker(jt),'zh_speaker':speaker(zt),
      'jp_text':jt,'zh_text':zt}

base=list(csv.DictReader(open(V2/'all.tsv',encoding='utf-8-sig'),delimiter='\t'))
gaps=list(csv.DictReader(open(GAPS,encoding='utf-8-sig'),delimiter='\t'))
new=[]
for g in gaps:
    key=(g['scene'],g['block_id'])
    if key in APPROVED_FULL:
        J,Z,A=scene(ROOT,g['scene'][4:])
        js=list(range(int(g['jp_start']),int(g['jp_end'])+1)); zs=list(range(int(g['zh_start']),int(g['zh_end'])+1)); k=int(g['skip_local_index'])
        if g['skip_side']=='skip-zh': pairs=list(zip(js,[z for n,z in enumerate(zs) if n!=k]))
        elif g['skip_side']=='skip-jp': pairs=list(zip([j for n,j in enumerate(js) if n!=k],zs))
        else: raise RuntimeError(key)
        for ji,zi in pairs:new.append(mkrow(g['scene'],g['block_id'],ji,zi,f"human-confirmed-{g['skip_side']}:{g['skip_event_index']}"))
    if key in APPROVED_PARTIAL:
        for ji,zi in APPROVED_PARTIAL[key]: new.append(mkrow(g['scene'],g['block_id'],ji,zi,'human-confirmed-partial'))

nj={(r['scene'],str(r['jp_event_index'])) for r in new}; nz={(r['scene'],str(r['zh_event_index'])) for r in new}
kept=[]
for r in base:
    jkey=(r['scene'],r['jp_event_index']); zkey=(r['scene'],r['zh_event_index'])
    if r['status'].startswith('review-') and ((r['jp_event_index'] and jkey in nj) or (r['zh_event_index'] and zkey in nz)):
        continue
    kept.append(r)
allrows=kept+new
allrows.sort(key=lambda r:(r['scene'], int(r['jp_event_index']) if str(r['jp_event_index'])!='' else 10**9+int(r['zh_event_index'])))
fields=['scene','segment','jp_event_index','zh_event_index','status','reason','jp_text_id','zh_text_id','jp_kidoku_id','zh_kidoku_id','jp_offset','zh_offset','jp_kind','zh_kind','jp_speaker','zh_speaker','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(allrows)
for sc in sorted(set(r['scene'] for r in allrows)):
    rows=[r for r in allrows if r['scene']==sc]
    with open(OUT/f'{sc}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
C=collections.Counter(r['status'] for r in allrows)
safe_status={'anchor','equal-segment','name-event','unique-gap','confirmed-gap'}
safe=sum(C[s] for s in safe_status)
print('new_confirmed',len(new));print('status',json.dumps(C,ensure_ascii=False,sort_keys=True));print('safe',safe,'safe_pct_jp',round(100*safe/98955,3));print('out',OUT)
