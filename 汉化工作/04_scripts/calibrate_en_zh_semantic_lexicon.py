from pathlib import Path
import csv,re,collections,math,random,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
M=ROOT/'03_text/matched/switch_pc_v10/safe_matches.tsv'
WORD=re.compile(r"[A-Za-z][A-Za-z'-]*|\d+")
HAN=re.compile(r'[\u3400-\u9fff]')
CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
STOP=set('the a an and or but to of in on at for with from by is are was were be been being i you he she it we they me my your his her our their this that these those do does did have has had not no yes just so as if then than what why how when where who which can could would should will shall may might must very really there here into out up down all any some one two'.split())
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def en_tokens(s):
 s=(s or '').replace('\\n',' ').replace('\\r',' ')
 if '@' in s and s.startswith('`'):s=s.split('@',1)[1]
 s=CTRL.sub(' ',s)
 return {w.lower() for w in WORD.findall(s) if w.lower() not in STOP and len(w)>1}
def zh_chars(s):return set(HAN.findall(s or ''))
rows=[r for r in rd(M) if r['pc_zh_text'] and r['match_kind']!='nonverbal-preserved']
random.seed(17);random.shuffle(rows)
train=rows[:85000];test=rows[85000:90000]
wc=collections.Counter(); cc=collections.Counter(); pair=collections.defaultdict(collections.Counter);N=len(train)
for r in train:
 E=en_tokens(r['sw_en_text']); C=zh_chars(r['pc_zh_text'])
 if not E or not C:continue
 for w in E:wc[w]+=1
 for c in C:cc[c]+=1
 for w in E:
  pw=pair[w]
  for c in C:pw[c]+=1
# compress each word to top 80 PMI-ish associations with min pair count 2
assoc={}
for w,cnt in pair.items():
 if wc[w]<3:continue
 vals=[]
 for c,n in cnt.items():
  if n<2:continue
  pmi=math.log((n+0.5)*N/((wc[w]+1)*(cc[c]+1)))
  if pmi>0:vals.append((pmi,c))
 vals.sort(reverse=True);assoc[w]={c:v for v,c in vals[:80]}
def score(en,zh):
 E=en_tokens(en); C=zh_chars(zh)
 if not E or not C:return -99
 vals=[]
 for w in E:
  a=assoc.get(w)
  if not a:continue
  best=max((a.get(c,0) for c in C),default=0)
  if best>0:vals.append(best)
 if not vals:return -20
 return sum(vals)/len(vals) + 0.04*len(vals)
# validate against nearby same-scene distractors
by=collections.defaultdict(list)
for r in rows:by[r['scene']].append(r)
for v in by.values():v.sort(key=lambda x:int(x['sw_code_index']))
idx={(r['scene'],r['sw_code_index']):i for sc,v in by.items() for i,r in enumerate(v)}
correct=0;tested=0;margins=[];bad=[]
for r in test:
 v=by[r['scene']];i=idx[(r['scene'],r['sw_code_index'])]
 cand=[r]
 for d in (-4,-3,-2,-1,1,2,3,4):
  j=i+d
  if 0<=j<len(v) and v[j]['pc_zh_text']:cand.append(v[j])
 # dedup chinese
 uniq=[];seen=set()
 for x in cand:
  z=x['pc_zh_text']
  if z not in seen:seen.add(z);uniq.append(x)
 if len(uniq)<2:continue
 ss=sorted([(score(r['sw_en_text'],x['pc_zh_text']),x is r,x['pc_zh_text']) for x in uniq],reverse=True,key=lambda t:t[0])
 tested+=1
 if ss[0][1]:correct+=1
 margin=next((s for s,isr,z in ss if isr),-99)-max((s for s,isr,z in ss if not isr),default=-99);margins.append(margin)
 if len(bad)<30 and not ss[0][1]:bad.append({'scene':r['scene'],'code':r['sw_code_index'],'en':r['sw_en_text'],'true':r['pc_zh_text'],'picked':ss[0][2],'true_score':next(s for s,isr,z in ss if isr),'picked_score':ss[0][0]})
print(json.dumps({'train':len(train),'test_attempted':tested,'top1':round(correct/tested,4) if tested else 0,'correct':correct,'assoc_words':len(assoc),'margin_ge_0_5_correct':sum(m>=.5 for m in margins),'margin_ge_1_correct':sum(m>=1 for m in margins),'bad_examples':bad[:10]},ensure_ascii=False,indent=2))
