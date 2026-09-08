import csv,pathlib,sys,re,collections
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from align_by_control_anchors import scene
root=pathlib.Path(__file__).resolve().parents[1]
R=list(csv.DictReader(open(root/'03_text/matched/pc_control_parallel_v3/all.tsv',encoding='utf-8-sig'),delimiter='\t'))
S={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
cache={}
def get(sc):
    if sc not in cache: cache[sc]=scene(root,sc[4:])[:2]
    return cache[sc]
fpc=collections.Counter();fj=collections.Counter()
for r in R:
    if r['status'] not in S:continue
    J,Z=get(r['scene']);j=J[int(r['jp_event_index'])];z=Z[int(r['zh_event_index'])];fpc[(j['fp'],z['fp'])]+=1;fj[j['fp']]+=1
for sc,ji,zi in [('SEEN1516',152,152),('SEEN6502',75,77)]:
    J,Z=get(sc);j=J[ji];z=Z[zi];c=fpc[(j['fp'],z['fp'])];print(sc,ji,zi,'jfp',j['fp'],'zfp',z['fp'],'pair',c,'jtotal',fj[j['fp']],'ratio',c/max(fj[j['fp']],1));print(j['text']);print(z['text'])
