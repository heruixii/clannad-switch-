from pathlib import Path
import sys,csv,random
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'03_text/matched/pc_control_parallel_v4/equal_review_block_analysis.tsv'; B=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv'
a=list(csv.DictReader(open(A,encoding='utf-8-sig'),delimiter='\t'));b=list(csv.DictReader(open(B,encoding='utf-8-sig'),delimiter='\t'))
strict=[x for x in a if x['strict']=='1'];random.seed(11);sel=random.sample(strict,min(18,len(strict)))
for x in sorted(sel,key=lambda q:(q['scene'],int(q['jp_start']))):
 bi=int(x['block_index']);bb=b[bi];J,Z,_=scene(ROOT,x['scene'][4:]);print('\n###',x['scene'],'n',x['n'],'min',x['min_sim'],'fp',x['fp_exact'],'dialogues',x['dialogues'])
 for ji,zi in zip(range(int(bb['jp_start']),int(bb['jp_end'])+1),range(int(bb['zh_start']),int(bb['zh_end'])+1)):
  print(ji,'=>',zi,J[ji]['text'],'|||',Z[zi]['text'])
