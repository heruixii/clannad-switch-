from pathlib import Path
import csv,collections,re,unicodedata,bisect,json,difflib
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; M=ROOT/'03_text/matched/switch_pc_v9/safe_matches.tsv'; U=ROOT/'03_text/matched/switch_pc_v9/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v9/fuzzy_between_anchors.tsv'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'};SUPS=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s);return CTRL.sub('',s)
def norm(s):
 s=unicodedata.normalize('NFKC',base(s));return ''.join(ch for ch in s if not ch.isspace())
def bare(s):
 s=norm(s);return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
def sig(s):
 s=base(s).strip();
 if s.startswith('【') and '】' in s:return ('D',s[1:s.index('】')])
 return ('N','')
def sim(a,b):
 a,b=bare(a),bare(b)
 if not a or not b:return 0.0
 return difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
pc=rd(PC);trusted={};jp={}
for r in pc:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  k=(r['scene'],int(r['jp_event_index']));jp[k]=r['jp_text']
  if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for p in SUPS:
 for r in rd(p):
  if 'accepted' in r and r['accepted'] not in ('1',''):continue
  k=(r['scene'],int(r['jp_event_index']))
  if r.get('zh_text'):trusted.setdefault(k,(r['zh_text'],r.get('status','supp')))
sw=rd(SW);matches=rd(M);un=rd(U);unkeys={(r['scene'],r['code_index']) for r in un};sb=collections.defaultdict(list);mb=collections.defaultdict(dict)
for r in sw:sb[r['scene']].append(r)
for v in sb.values():v.sort(key=lambda r:int(r['code_index']))
for r in matches:mb[r['scene']][int(r['sw_code_index'])]=(r['pc_scene'],int(r['pc_event_index']))
pseq=collections.defaultdict(list)
for (sc,e) in jp:pseq[sc].append(e)
for v in pseq.values():v.sort()
out=[];stats=collections.Counter()
for sc,srows in sb.items():
 mother=ALIASES.get(sc,sc);anchors=[]
 for pos,r in enumerate(srows):
  q=mb.get(sc,{}).get(int(r['code_index']))
  if q and q[0]==mother:anchors.append((pos,q[1]))
 apos=[x[0] for x in anchors];used={x[1] for x in anchors}
 for pos,r in enumerate(srows):
  if (sc,r['code_index']) not in unkeys or not bare(r['jp_text']):continue
  q=bisect.bisect_left(apos,pos)
  if q==0 or q==len(anchors):continue
  lp,rp=anchors[q-1][1],anchors[q][1]
  if lp>=rp:continue
  ss=sig(r['jp_text']); cand=[]
  for e in pseq.get(mother,[]):
   if not (lp<e<rp) or e in used or (mother,e) not in trusted:continue
   if sig(jp[(mother,e)])[0]!=ss[0]:continue
   if ss[0]=='D' and sig(jp[(mother,e)])[1]!=ss[1]:continue
   v=sim(r['jp_text'],jp[(mother,e)])
   if v>=0.55:cand.append((v,e))
  cand.sort(reverse=True);stats['examined']+=1
  if not cand:continue
  best,e=cand[0];second=cand[1][0] if len(cand)>1 else 0; margin=best-second
  accept=(best>=0.93) or (best>=0.84 and margin>=0.12) or (best>=0.78 and margin>=0.25)
  if accept:
   zh,st=trusted[(mother,e)];used.add(e);out.append({'scene':sc,'sw_code_index':r['code_index'],'sw_jp_text':r['jp_text'],'sw_en_text':r['en_text'],'pc_scene':mother,'pc_event_index':e,'pc_status':st,'pc_jp_text':jp[(mother,e)],'pc_zh_text':zh,'match_kind':'fuzzy-between-anchors','similarity':round(best,5),'margin':round(margin,5),'left_anchor_pc':lp,'right_anchor_pc':rp});stats['accepted']+=1
   if best>=.93:stats['high']+=1
  else:stats['rejected']+=1
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 fields=list(out[0]) if out else [];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps(dict(stats),indent=2));print('rows',len(out));print(OUT)
