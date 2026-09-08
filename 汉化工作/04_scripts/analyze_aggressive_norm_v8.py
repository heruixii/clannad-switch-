from pathlib import Path
import csv,re,collections,unicodedata,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
U=ROOT/'03_text/matched/switch_pc_v8/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; M=ROOT/'03_text/matched/switch_pc_v8/safe_matches.tsv'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
# add supplements trusted
SUPS=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]')
CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)
 s=CTRL.sub('',s)
 return s
def aggr(s):
 s=unicodedata.normalize('NFKC',base(s))
 # preserve letters/numbers/kana/han/speaker label contents, drop spacing and punctuation
 return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
pc0=rd(PC); trusted={};jp={}
for r in pc0:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  k=(r['scene'],int(r['jp_event_index']));jp[k]=r['jp_text']
  if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for p in SUPS:
 for r in rd(p):
  if 'accepted' in r and r['accepted'] not in ('1',''):continue
  k=(r['scene'],int(r['jp_event_index']))
  if r.get('zh_text'):trusted.setdefault(k,(r['zh_text'],r.get('status','supplement')))
idx=collections.defaultdict(lambda:collections.defaultdict(list))
for k,v in trusted.items():idx[k[0]][aggr(jp[k])].append(k[1])
u=rd(U);counts=collections.Counter();examples=[]
for r in u:
 mother=ALIASES.get(r['scene'],r['scene']);t=aggr(r['jp_text']); cand=idx.get(mother,{}).get(t,[]) if t else []
 if not t:cat='empty-after-norm'
 elif len(cand)==1:cat='same-mother-unique-aggr'
 elif len(cand)>1:cat='same-mother-multi-aggr'
 else:cat='no-aggr-match'
 counts[cat]+=1
 if cat=='same-mother-unique-aggr' and len(examples)<50:examples.append({'scene':r['scene'],'code':r['code_index'],'jp':r['jp_text'],'pc_event':cand[0],'pc_jp':jp[(mother,cand[0])],'zh':trusted[(mother,cand[0])][0]})
print(json.dumps({'remaining':len(u),'counts':dict(counts),'examples':examples},ensure_ascii=False,indent=2))
