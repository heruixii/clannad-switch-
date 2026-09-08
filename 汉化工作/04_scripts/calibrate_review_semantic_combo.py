from pathlib import Path
import sys,csv,re,collections,math,json,difflib,random
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'03_text/matched/switch_pc_v10/safe_matches.tsv'; B=ROOT/'03_text/matched/pc_control_parallel_v4/current_review_blocks.tsv'
SUP=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
WORD=re.compile(r"[A-Za-z][A-Za-z'-]*|\d+"); HAN=re.compile(r'[\u3400-\u9fff]'); CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
STOP=set('the a an and or but to of in on at for with from by is are was were be been being i you he she it we they me my your his her our their this that these those do does did have has had not no yes just so as if then than what why how when where who which can could would should will shall may might must very really there here into out up down all any some one two'.split())
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def en_tokens(s):
 s=(s or '').replace('\\n',' ').replace('\\r',' ')
 if '@' in s and s.startswith('`'):s=s.split('@',1)[1]
 s=CTRL.sub(' ',s);return {w.lower() for w in WORD.findall(s) if w.lower() not in STOP and len(w)>1}
def zh_chars(s):return set(HAN.findall(s or ''))
def trim(s):return (s or '').strip(' \t\"')
def kind(s):return 'D' if trim(s).startswith('【') else 'N'
def sp(s):
 m=re.match(r'^【([^】]+)】',trim(s));return m.group(1).strip(' \"') if m else ''
# speaker map from trusted rows
mr=rd(M); spcnt=collections.defaultdict(collections.Counter)
for r in mr:
 a,b=sp(r['pc_jp_text']),sp(r['pc_zh_text'])
 if a and b:spcnt[a][b]+=1
spmap={a:{b for b,n in c.items() if n>=2 or n/sum(c.values())>=.05} for a,c in spcnt.items()}
def compat(j,z):
 if kind(j['text'])!=kind(z['text']):return False
 if kind(j['text'])=='N':return True
 a,b=sp(j['text']),sp(z['text']);return bool(a and b and b in spmap.get(a,{a}))
# lexicon
train=[r for r in mr if r['pc_zh_text'] and r['match_kind']!='nonverbal-preserved'][:90000];N=len(train);wc=collections.Counter();cc=collections.Counter();pairs=collections.defaultdict(collections.Counter)
for r in train:
 E=en_tokens(r['sw_en_text']);C=zh_chars(r['pc_zh_text'])
 for w in E:wc[w]+=1
 for c in C:cc[c]+=1
 for w in E:
  for c in C:pairs[w][c]+=1
assoc={}
for w,cnt in pairs.items():
 if wc[w]<3:continue
 vals=[]
 for c,n in cnt.items():
  if n<2:continue
  v=math.log((n+.5)*N/((wc[w]+1)*(cc[c]+1)))
  if v>0:vals.append((v,c))
 vals.sort(reverse=True);assoc[w]={c:v for v,c in vals[:80]}
def sem(en,zh):
 E=en_tokens(en);C=zh_chars(zh);vv=[]
 for w in E:
  a=assoc.get(w)
  if a:
   x=max((a.get(c,0) for c in C),default=0)
   if x>0:vv.append(x)
 return (sum(vv)/len(vv)+.04*len(vv)) if vv else 0
# english by pc key
ens=collections.defaultdict(list)
for r in mr:
 if (r.get('pc_event_index') or '').isdigit():ens[(r['pc_scene'],int(r['pc_event_index']))].append(r['sw_en_text'])
enmap={k:max(v,key=len) for k,v in ens.items()}
# original blocks lookup
blocks=rd(B); bl_by=collections.defaultdict(list)
for b in blocks:
 if b['jp_start']:bl_by[b['scene']].append((int(b['jp_start']),int(b['jp_end']),int(b['zh_start']) if b['zh_start'] else None,int(b['zh_end']) if b['zh_end'] else None))
def block_for(sc,ji):
 for x in bl_by.get(sc,[]):
  if x[0]<=ji<=x[1]:return x
 return None
# truth supplemental accepted
truth=[]
for p in SUP:
 for r in rd(p):
  if 'accepted' in r and r['accepted']!='1' and p.name!='review_signature_manual_accept.tsv':continue
  if not (r.get('jp_event_index') or '').isdigit() or not (r.get('zh_event_index') or '').isdigit():continue
  k=(r['scene'],int(r['jp_event_index']));en=enmap.get(k)
  if en:truth.append((r['scene'],int(r['jp_event_index']),int(r['zh_event_index']),en))
# unique truths
seen=set();truth=[x for x in truth if not ((x[0],x[1]) in seen or seen.add((x[0],x[1])))]
cache={}; cases=[]
for sc,ji,zi,en in truth:
 b=block_for(sc,ji)
 if not b or b[2] is None:continue
 if sc not in cache:cache[sc]=scene(ROOT,sc[4:])[:2]
 J,Z=cache[sc];js,je,zs,ze=b
 cands=[]
 for zidx in range(zs,ze+1):
  if not compat(J[ji],Z[zidx]):continue
  posj=(ji-js)/max(1,je-js);posz=(zidx-zs)/max(1,ze-zs)
  pos=1-abs(posj-posz)
  ctrl=difflib.SequenceMatcher(None,J[ji]['block'],Z[zidx]['block'],autojunk=False).ratio()
  se=sem(en,Z[zidx]['text'])
  cands.append((zidx,se,ctrl,pos))
 if len(cands)>=2 and any(z==zi for z,*_ in cands):cases.append((zi,cands))
print('cases',len(cases))
weights=[(1,.5,.5),(1,1,.5),(1,1,1),(1,1.5,.5),(1,2,.5),(1,2,1),(1.5,1,.5),(2,1,.5),(2,1,1),(2,2,1)]
res=[]
for ws,wc_,wp in weights:
 ok=0;marg_ok=collections.Counter();marg_bad=collections.Counter();margins=[]
 for true,cands in cases:
  ss=sorted([(ws*se+wc_*ctrl+wp*pos,z) for z,se,ctrl,pos in cands],reverse=True)
  correct=ss[0][1]==true;ok+=correct;margin=ss[0][0]-ss[1][0];margins.append((margin,correct))
 for th in (.25,.5,.75,1.0,1.5,2.0):
  sel=[c for m,c in margins if m>=th];marg_ok[th]=(sum(sel),len(sel),sum(sel)/len(sel) if sel else 0)
 res.append({'w':(ws,wc_,wp),'top1':ok/len(cases),'n':len(cases),'thresholds':{str(k):v for k,v in marg_ok.items()}})
print(json.dumps(res,ensure_ascii=False,indent=2))
