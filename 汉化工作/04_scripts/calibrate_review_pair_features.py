from pathlib import Path
import sys,csv,collections,difflib,statistics,random,re,json,time
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
CORP=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}

def trim(s):return s.strip(' \t\"')
def kind_text(s):return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker_text(s):
 m=re.match(r'^【([^】]+)】',trim(s));return m.group(1) if m else ''
def sim(a,b):return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
rows=list(csv.DictReader(open(CORP,encoding='utf-8-sig'),delimiter='\t'))
by=collections.defaultdict(list)
for r in rows:
 if r['status'] in SAFE and r.get('jp_event_index','').isdigit() and r.get('zh_event_index','').isdigit():by[r['scene']].append(r)
random.seed(7)
scenes=list(by)
# sample across scenes proportionally but cap 40 each
pos=[];neg=[];fp_eq=0;sp_same=0;kind_same=0
for sc in scenes:
 J,Z,_=scene(ROOT,sc[4:])
 rs=by[sc]
 if len(rs)>40:rs=random.sample(rs,40)
 for r in rs:
  ji=int(r['jp_event_index']);zi=int(r['zh_event_index'])
  if ji>=len(J) or zi>=len(Z):continue
  j,z=J[ji],Z[zi]
  v=sim(j['block'],z['block']);pos.append(v)
  fp_eq+=j['fp']==z['fp'];kind_same+=kind_text(j['text'])==kind_text(z['text'])
  # nearby wrong same-kind candidates
  cand=[]
  for dz in (-5,-4,-3,-2,-1,1,2,3,4,5):
   zz=zi+dz
   if 0<=zz<len(Z) and kind_text(J[ji]['text'])==kind_text(Z[zz]['text']):cand.append(zz)
  if cand:
   zz=random.choice(cand);neg.append(sim(j['block'],Z[zz]['block']))

def qs(x):
 if not x:return {}
 y=sorted(x);n=len(y)
 def q(p):return y[min(n-1,int(p*(n-1)))]
 return {'n':n,'mean':round(statistics.mean(y),4),'p05':round(q(.05),4),'p10':round(q(.1),4),'p25':round(q(.25),4),'p50':round(q(.5),4),'p75':round(q(.75),4),'p90':round(q(.9),4),'p95':round(q(.95),4)}
print(json.dumps({'positive':qs(pos),'near_wrong_same_kind':qs(neg),'fp_exact_positive':fp_eq,'kind_same_positive':kind_same},indent=2))
