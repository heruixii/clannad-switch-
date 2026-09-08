from pathlib import Path
import sys,csv,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
by=collections.defaultdict(list);scenes=sorted(set(r['scene'] for r in rows))
for r in rows:
 if r['status'] in SAFE and r.get('jp_event_index','').isdigit() and r.get('zh_event_index','').isdigit():by[r['scene']].append((int(r['jp_event_index']),int(r['zh_event_index'])))
blocks=[]; shapes=collections.Counter()
for sc in scenes:
 J,Z,_=scene(ROOT,sc[4:]); A=[(-1,-1)]+sorted(set(by[sc]))+[(len(J),len(Z))]
 for (ja,za),(jb,zb) in zip(A,A[1:]):
  nj=jb-ja-1;nz=zb-za-1
  if nj or nz:
   blocks.append((sc,ja+1,jb-1,za+1,zb-1,nj,nz));shapes[(nj,nz)]+=1
print('blocks',len(blocks),'jp',sum(x[5] for x in blocks),'zh',sum(x[6] for x in blocks),'equal_blocks',sum(x[5]==x[6] for x in blocks),'equal_jp',sum(x[5] for x in blocks if x[5]==x[6]),'unequal_jp',sum(x[5] for x in blocks if x[5]!=x[6]))
print('top_shapes',shapes.most_common(40))
# write
out=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv'
with open(out,'w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['scene','jp_start','jp_end','zh_start','zh_end','jp_count','zh_count']);w.writerows(blocks)
print(out)
