from pathlib import Path
import sys,csv,collections,re,difflib,json,statistics
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; B=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
def trim(s):return (s or '').strip(' \t\"')
def kind(s):return 'D' if trim(s).startswith('【') else 'N'
def sp(s):
 m=re.match(r'^【([^】]+)】',trim(s));return m.group(1).strip(' \"') if m else ''
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'));mp=collections.defaultdict(collections.Counter)
for r in rows:
 if r['status'] in SAFE:
  a,b=sp(r['jp_text']),sp(r['zh_text'])
  if a and b:mp[a][b]+=1
spmap={a:{b for b,n in c.items() if n>=2 or sum(c.values())<5 or n/sum(c.values())>=.05} for a,c in mp.items()}
def compat(j,z):
 if kind(j['text'])!=kind(z['text']):return False
 if kind(j['text'])=='N':return True
 a,b=sp(j['text']),sp(z['text'])
 return bool(a and b and (b in spmap.get(a,{a})))
def sim(a,b):return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
blocks=list(csv.DictReader(open(B,encoding='utf-8-sig'),delimiter='\t'));cache={}; out=[];cnt=collections.Counter()
for bi,b in enumerate(blocks):
 n=int(b['jp_count']);m=int(b['zh_count'])
 if n!=m or n==0:continue
 sc=b['scene'];
 if sc not in cache:cache[sc]=scene(ROOT,sc[4:])[:2]
 J,Z=cache[sc];js=range(int(b['jp_start']),int(b['jp_end'])+1);zs=range(int(b['zh_start']),int(b['zh_end'])+1)
 pairs=[];allc=True
 for ji,zi in zip(js,zs):
  j,z=J[ji],Z[zi];c=compat(j,z);s=sim(j['block'],z['block']);pairs.append((ji,zi,c,s,j['fp']==z['fp'],j,z));allc &= c
 mins=min(x[3] for x in pairs);avg=sum(x[3] for x in pairs)/n;fpeq=sum(x[4] for x in pairs); dialogs=sum(kind(x[5]['text'])=='D' for x in pairs)
 # text-id delta consistency
 dd=[]
 for x,y in zip(pairs,pairs[1:]):dd.append(abs((y[5]['text_id']-x[5]['text_id'])-(y[6]['text_id']-x[6]['text_id'])))
 maxdd=max(dd) if dd else 0
 strict=allc and mins>=.86 and (fpeq>0 or dialogs>0 or n>=2)
 cnt['blocks']+=1;cnt['rows']+=n;cnt['strict_blocks']+=strict;cnt['strict_rows']+=n if strict else 0
 out.append({'block_index':bi,'scene':sc,'n':n,'all_compatible':int(allc),'min_sim':round(mins,5),'avg_sim':round(avg,5),'fp_exact':fpeq,'dialogues':dialogs,'max_textid_delta_diff':maxdd,'strict':int(strict),'jp_start':b['jp_start'],'zh_start':b['zh_start']})
O=ROOT/'03_text/matched/pc_control_parallel_v4/equal_review_block_analysis.tsv'
with open(O,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps(dict(cnt),indent=2));print('out',O)
print('strict_by_size',collections.Counter(x['n'] for x in out if x['strict']).most_common(30))
