from pathlib import Path
import csv,collections,re,unicodedata,bisect,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; M=ROOT/'03_text/matched/switch_pc_v9/safe_matches.tsv'; U=ROOT/'03_text/matched/switch_pc_v9/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}; SUPS=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s);return CTRL.sub('',s)
def a(s):
 s=unicodedata.normalize('NFKC',base(s));return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
# trusted pc
pc=rd(PC);jp={};trusted={}
for r in pc:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  k=(r['scene'],int(r['jp_event_index']));jp[k]=r['jp_text']
  if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for p in SUPS:
 for r in rd(p):
  if 'accepted' in r and r['accepted'] not in ('1',''):continue
  k=(r['scene'],int(r['jp_event_index']))
  if r.get('zh_text'):trusted.setdefault(k,(r['zh_text'],r.get('status','supp')))
sw=rd(SW);matches=rd(M);un=rd(U);sb=collections.defaultdict(list); mb=collections.defaultdict(dict); unkeys={(r['scene'],r['code_index']) for r in un}
for r in sw:sb[r['scene']].append(r)
for v in sb.values():v.sort(key=lambda r:int(r['code_index']))
for r in matches:mb[r['scene']][int(r['sw_code_index'])]=(r['pc_scene'],int(r['pc_event_index']))
# pc events per scene
pseq=collections.defaultdict(list)
for (sc,e),txt in jp.items():pseq[sc].append(e)
for sc in pseq:pseq[sc].sort()
one2=[];two1=[]
for sc,srows in sb.items():
 mother=ALIASES.get(sc,sc); anchors=[]
 for pos,r in enumerate(srows):
  c=int(r['code_index']);q=mb.get(sc,{}).get(c)
  if q and q[0]==mother:anchors.append((pos,q[1]))
 apos=[x[0] for x in anchors]
 for pos,r in enumerate(srows):
  if (sc,r['code_index']) not in unkeys or not a(r['jp_text']):continue
  q=bisect.bisect_left(apos,pos)
  if q==0 or q==len(anchors):continue
  lp,rp=anchors[q-1][1],anchors[q][1]
  # 1 switch = 2 adjacent PC, both trusted
  events=[e for e in pseq.get(mother,[]) if lp<e<rp]
  found=[]
  for e1,e2 in zip(events,events[1:]):
   if e2!=e1+1 or (mother,e1) not in trusted or (mother,e2) not in trusted:continue
   if a(jp[(mother,e1)])+a(jp[(mother,e2)])==a(r['jp_text']):found.append((e1,e2))
  if len(found)==1:
   e1,e2=found[0];one2.append({'scene':sc,'sw_code_index':r['code_index'],'sw_jp':r['jp_text'],'pc_scene':mother,'pc_e1':e1,'pc_e2':e2,'pc_jp1':jp[(mother,e1)],'pc_jp2':jp[(mother,e2)],'zh1':trusted[(mother,e1)][0],'zh2':trusted[(mother,e2)][0]})
 # 2 adjacent unmatched switch = 1 pc
 for pos in range(len(srows)-1):
  r1,r2=srows[pos],srows[pos+1]
  if (sc,r1['code_index']) not in unkeys or (sc,r2['code_index']) not in unkeys:continue
  t=a(r1['jp_text'])+a(r2['jp_text'])
  if not t:continue
  q=bisect.bisect_left(apos,pos)
  if q==0 or q==len(anchors):continue
  lp,rp=anchors[q-1][1],anchors[q][1];cand=[e for e in pseq.get(mother,[]) if lp<e<rp and (mother,e) in trusted and a(jp[(mother,e)])==t]
  if len(cand)==1:
   e=cand[0];two1.append({'scene':sc,'sw_code1':r1['code_index'],'sw_code2':r2['code_index'],'sw_jp1':r1['jp_text'],'sw_jp2':r2['jp_text'],'pc_scene':mother,'pc_event':e,'pc_jp':jp[(mother,e)],'zh':trusted[(mother,e)][0]})
O=ROOT/'03_text/matched/switch_pc_v9'
for name,rows in [('one_switch_two_pc.tsv',one2),('two_switch_one_pc.tsv',two1)]:
 with (O/name).open('w',encoding='utf-8-sig',newline='') as f:
  fields=list(rows[0]) if rows else [];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
print(json.dumps({'one_switch_two_pc':len(one2),'two_switch_one_pc':len(two1)},indent=2))
