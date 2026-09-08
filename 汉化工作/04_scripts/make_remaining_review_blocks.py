from pathlib import Path
import sys,csv,collections,json
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v3/all.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v3/remaining_blocks.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
R=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'))
by=collections.defaultdict(list)
for r in R:
    if r['status'] in SAFE: by[r['scene']].append((int(r['jp_event_index']),int(r['zh_event_index'])))
blocks=[]
for sc in sorted({r['scene'] for r in R}):
    J,Z,A=scene(ROOT,sc[4:]); anchors=[(-1,-1)]+sorted(by[sc])+[(len(J),len(Z))]
    bid=0
    for (ja,za),(jb,zb) in zip(anchors,anchors[1:]):
        js=list(range(ja+1,jb)); zs=list(range(za+1,zb))
        if not js and not zs: continue
        blocks.append({'scene':sc,'block_id':bid,'jp_count':len(js),'zh_count':len(zs),'jp_start':js[0] if js else '','jp_end':js[-1] if js else '','zh_start':zs[0] if zs else '','zh_end':zs[-1] if zs else ''})
        bid+=1
fields=['scene','block_id','jp_count','zh_count','jp_start','jp_end','zh_start','zh_end']
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(blocks)
C=collections.Counter((int(b['jp_count']),int(b['zh_count'])) for b in blocks);print('blocks',len(blocks),'scenes',len(set(b['scene'] for b in blocks)),'jp_unpaired',sum(int(b['jp_count']) for b in blocks),'zh_unpaired',sum(int(b['zh_count']) for b in blocks));print('top_shapes',C.most_common(30));print('max',max((max(int(b['jp_count']),int(b['zh_count'])) for b in blocks),default=0));print('out',OUT)
