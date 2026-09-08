from pathlib import Path
import csv,collections,json,re,sys
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
V3=ROOT/'03_text/matched/pc_control_parallel_v3'
CAND=ROOT/'03_text/matched/pc_control_parallel_v1/recursive_control_candidates.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v4';OUT.mkdir(parents=True,exist_ok=True)
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap'}

def trim(s):return s.strip(' \t\"')
def kind(s):return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker(s):
    m=re.match(r'^【([^】]+)】',trim(s));return m.group(1) if m else ''
def clean_zh(s):
    s=s.strip()
    while len(s)>=2 and s[0]=='\"' and s[-1]=='\"':s=s[1:-1]
    return s

base=list(csv.DictReader(open(V3/'all.tsv',encoding='utf-8-sig'),delimiter='\t'))
cand=list(csv.DictReader(open(CAND,encoding='utf-8-sig'),delimiter='\t'))
jp_used={(r['scene'],r['jp_event_index']) for r in base if r['status'] in SAFE}
zh_used={(r['scene'],r['zh_event_index']) for r in base if r['status'] in SAFE}
new=[]
for r in cand:
    if (r['scene'],r['jp_event_index']) in jp_used or (r['scene'],r['zh_event_index']) in zh_used:continue
    if r['jp_fp']!=r['zh_fp'] or r['jp_event_index']!=r['zh_event_index']:continue
    if r['jp_speaker'] and r['zh_speaker'] and r['jp_speaker']!=r['zh_speaker']:continue
    sc=r['scene'];ji=int(r['jp_event_index']);zi=int(r['zh_event_index']);J,Z,_=scene(ROOT,sc[4:]);jt=J[ji]['text'];zt=clean_zh(Z[zi]['text'])
    new.append({'scene':sc,'segment':'recursive-hard','jp_event_index':ji,'zh_event_index':zi,'status':'recursive-hard','reason':'local-anchor+same-fp+same-index',
      'jp_text_id':J[ji]['text_id'],'zh_text_id':Z[zi]['text_id'],'jp_kidoku_id':J[ji]['kidoku_id'],'zh_kidoku_id':Z[zi]['kidoku_id'],
      'jp_offset':J[ji]['text_offset'],'zh_offset':Z[zi]['text_offset'],'jp_kind':kind(jt),'zh_kind':kind(zt),'jp_speaker':speaker(jt),'zh_speaker':speaker(zt),'jp_text':jt,'zh_text':zt})
nj={(r['scene'],str(r['jp_event_index'])) for r in new};nz={(r['scene'],str(r['zh_event_index'])) for r in new}
kept=[]
for r in base:
    if r['status'].startswith('review-') and ((r['jp_event_index'] and (r['scene'],r['jp_event_index']) in nj) or (r['zh_event_index'] and (r['scene'],r['zh_event_index']) in nz)):continue
    kept.append(r)
allrows=kept+new
allrows.sort(key=lambda r:(r['scene'],int(r['jp_event_index']) if r['jp_event_index']!='' else 10**9+int(r['zh_event_index'])))
fields=['scene','segment','jp_event_index','zh_event_index','status','reason','jp_text_id','zh_text_id','jp_kidoku_id','zh_kidoku_id','jp_offset','zh_offset','jp_kind','zh_kind','jp_speaker','zh_speaker','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(allrows)
for sc in sorted(set(r['scene'] for r in allrows)):
    rows=[r for r in allrows if r['scene']==sc]
    with open(OUT/f'{sc}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
C=collections.Counter(r['status'] for r in allrows);safe=sum(C[s] for s in SAFE|{'recursive-hard'})
print('new',len(new));print('safe',safe,'pct',round(100*safe/98955,3));print(json.dumps(C,ensure_ascii=False,sort_keys=True))
