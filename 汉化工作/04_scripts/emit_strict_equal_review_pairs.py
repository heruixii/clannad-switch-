from pathlib import Path
import sys,csv,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'03_text/matched/pc_control_parallel_v4/equal_review_block_analysis.tsv';B=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv';O=ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv'
a=list(csv.DictReader(open(A,encoding='utf-8-sig'),delimiter='\t'));bs=list(csv.DictReader(open(B,encoding='utf-8-sig'),delimiter='\t'));cache={};out=[]
for x in a:
 if x['strict']!='1':continue
 b=bs[int(x['block_index'])];sc=x['scene']
 if sc not in cache:cache[sc]=scene(ROOT,sc[4:])[:2]
 J,Z=cache[sc]
 for ji,zi in zip(range(int(b['jp_start']),int(b['jp_end'])+1),range(int(b['zh_start']),int(b['zh_end'])+1)):
  out.append({'scene':sc,'block_index':x['block_index'],'jp_event_index':ji,'zh_event_index':zi,'status':'review-equal-strict','block_min_sim':x['min_sim'],'block_fp_exact':x['fp_exact'],'jp_text':J[ji]['text'],'zh_text':Z[zi]['text']})
with open(O,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'pairs':len(out),'unique_jp':len(set((r['scene'],r['jp_event_index']) for r in out)),'unique_zh':len(set((r['scene'],r['zh_event_index']) for r in out))},indent=2));print(O)
