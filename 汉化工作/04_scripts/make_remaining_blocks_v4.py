from pathlib import Path
import sys,csv,collections
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v4/remaining_blocks.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap','highconf-anchor'}
R=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'));by=collections.defaultdict(list)
for r in R:
    if r['status'] in SAFE:by[r['scene']].append((int(r['jp_event_index']),int(r['zh_event_index'])))
blocks=[]
for sc in sorted({r['scene'] for r in R}):
    J,Z,_=scene(ROOT,sc[4:]);aa=[(-1,-1)]+sorted(by[sc])+[(len(J),len(Z))];bid=0
    for (ja,za),(jb,zb) in zip(aa,aa[1:]):
        js=list(range(ja+1,jb));zs=list(range(za+1,zb))
        if not js and not zs:continue
        blocks.append({'scene':sc,'block_id':bid,'jp_count':len(js),'zh_count':len(zs),'jp_start':js[0] if js else '','jp_end':js[-1] if js else '','zh_start':zs[0] if zs else '','zh_end':zs[-1] if zs else ''});bid+=1
fields=list(blocks[0].keys())
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(blocks)
C=collections.Counter((int(b['jp_count']),int(b['zh_count'])) for b in blocks)
print('blocks',len(blocks),'scenes',len(set(b['scene'] for b in blocks)),'jp',sum(int(b['jp_count']) for b in blocks),'zh',sum(int(b['zh_count']) for b in blocks));print('top',C.most_common(40));print('small_diff1',sum(abs(int(b['jp_count'])-int(b['zh_count']))==1 and max(int(b['jp_count']),int(b['zh_count']))<=12 for b in blocks));print('small_equal',sum(int(b['jp_count'])==int(b['zh_count']) and 0<int(b['jp_count'])<=8 for b in blocks));print('out',OUT)
