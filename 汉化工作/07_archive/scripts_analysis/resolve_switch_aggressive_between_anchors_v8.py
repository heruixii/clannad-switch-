from pathlib import Path
import csv,collections,re,json,bisect,unicodedata
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; M=ROOT/'03_text/matched/switch_pc_v8/safe_matches.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v8/aggressive_between_anchors.tsv'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
SUPS=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s);return CTRL.sub('',s)
def aggr(s):
 s=unicodedata.normalize('NFKC',base(s));return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
pc=rd(PC);trusted={};jp={}
for r in pc:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  k=(r['scene'],int(r['jp_event_index']));jp[k]=r['jp_text']
  if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for p in SUPS:
 for r in rd(p):
  if 'accepted' in r and r['accepted'] not in ('1',''):continue
  k=(r['scene'],int(r['jp_event_index']));
  if r.get('zh_text'):trusted.setdefault(k,(r['zh_text'],r.get('status','supp')))
idx=collections.defaultdict(lambda:collections.defaultdict(list))
for k in trusted:
 t=aggr(jp[k]);
 if t:idx[k[0]][t].append(k[1])
for sc in idx:
 for t in idx[sc]:idx[sc][t].sort()
sw=rd(SW);matches=rd(M);sb=collections.defaultdict(list);mb=collections.defaultdict(dict)
for r in sw:sb[r['scene']].append(r)
for v in sb.values():v.sort(key=lambda r:int(r['code_index']))
for r in matches:mb[r['scene']][int(r['sw_code_index'])]=(r['pc_scene'],int(r['pc_event_index']))
out=[];stats=collections.Counter()
for sc,srows in sb.items():
 mother=ALIASES.get(sc,sc); anchors=[]
 for pos,r in enumerate(srows):
  c=int(r['code_index']);a=mb.get(sc,{}).get(c)
  if a and a[0]==mother:anchors.append((pos,a[1]))
 apos=[a for a,b in anchors];used={b for a,b in anchors}
 for pos,r in enumerate(srows):
  c=int(r['code_index'])
  if c in mb.get(sc,{}):continue
  t=aggr(r['jp_text'])
  if not t:continue
  q=bisect.bisect_left(apos,pos)
  if q==0 or q==len(anchors):continue
  lp=anchors[q-1][1];rp=anchors[q][1]
  if lp>=rp:continue
  cand=[e for e in idx.get(mother,{}).get(t,[]) if lp<e<rp and e not in used]
  stats['examined']+=1
  if len(cand)==1:
   e=cand[0];used.add(e);zh,st=trusted[(mother,e)]
   out.append({'scene':sc,'sw_code_index':c,'sw_jp_text':r['jp_text'],'sw_en_text':r['en_text'],'pc_scene':mother,'pc_event_index':e,'pc_status':st,'pc_jp_text':jp[(mother,e)],'pc_zh_text':zh,'match_kind':'aggressive-between-anchors','left_anchor_pc':lp,'right_anchor_pc':rp});stats['resolved']+=1
  elif len(cand)>1:stats['multi']+=1
  else:stats['none']+=1
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 fields=list(out[0]) if out else [];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps(dict(stats),indent=2));print('rows',len(out));print(OUT)
