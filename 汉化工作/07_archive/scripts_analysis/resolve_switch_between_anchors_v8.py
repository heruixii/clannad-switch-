from pathlib import Path
import csv,collections,re,json,bisect
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; M=ROOT/'03_text/matched/switch_pc_v8_base/safe_matches.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; SUP1=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv'; SUP2=ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv'; SUP3=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v8_base/between_anchor_exact.tsv'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');STYLE=re.compile(r'\$S(?:U)?\d{3}')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sn(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 return STYLE.sub('',RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)).replace('$W','')
def pn(s):return (s or '').replace('\r','')
# trusted pc dictionary
pcrows=rd(PC); trusted={}; jptext={}
for r in pcrows:
 if not (r.get('jp_event_index') or '').isdigit() or not r.get('jp_text'):continue
 k=(r['scene'],int(r['jp_event_index']));jptext[k]=r['jp_text']
 if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for r in rd(SUP1):
 if r.get('accepted')=='1':trusted.setdefault((r['scene'],int(r['jp_event_index'])),(r['zh_text'],'review-forced'))
for r in rd(SUP2):trusted.setdefault((r['scene'],int(r['jp_event_index'])),(r['zh_text'],'review-equal-strict'))
for r in rd(SUP3):trusted.setdefault((r['scene'],int(r['jp_event_index'])),(r['zh_text'],'review-forced-manual'))
# safe PC text index
idx=collections.defaultdict(lambda:collections.defaultdict(list))
for (sc,ei),(zh,st) in trusted.items():idx[sc][pn(jptext[(sc,ei)])].append(ei)
for sc in idx:
 for t in idx[sc]:idx[sc][t].sort()
sw=rd(SW);matches=rd(M); sw_by=collections.defaultdict(list);m_by=collections.defaultdict(dict)
for r in sw:sw_by[r['scene']].append(r)
for sc,v in sw_by.items():v.sort(key=lambda x:int(x['code_index']))
for r in matches:m_by[r['scene']][int(r['sw_code_index'])]=(r['pc_scene'],int(r['pc_event_index']))
out=[];stats=collections.Counter()
for sc,srows in sw_by.items():
 mother=ALIASES.get(sc,sc); anchors=m_by.get(sc,{})
 codes=[int(r['code_index']) for r in srows]; anchor_positions=[]
 for pos,r in enumerate(srows):
  c=int(r['code_index'])
  if c in anchors and anchors[c][0]==mother:anchor_positions.append((pos,anchors[c][1]))
 apos=[x[0] for x in anchor_positions]
 used={p for _,p in anchor_positions}
 for pos,r in enumerate(srows):
  c=int(r['code_index'])
  if c in anchors:continue
  q=bisect.bisect_left(apos,pos)
  if q==0 or q==len(apos):continue
  lpos,lpc=anchor_positions[q-1];rpos,rpc=anchor_positions[q]
  if not (lpc<rpc):continue
  t=sn(r['jp_text']); candidates=[e for e in idx.get(mother,{}).get(t,[]) if lpc<e<rpc and e not in used]
  stats['examined_between']+=1
  if len(candidates)==1:
   e=candidates[0];zh,st=trusted[(mother,e)];used.add(e)
   out.append({'scene':sc,'sw_code_index':c,'sw_jp_text':r['jp_text'],'sw_en_text':r['en_text'],'pc_scene':mother,'pc_event_index':e,'pc_status':st,'pc_jp_text':jptext[(mother,e)],'pc_zh_text':zh,'match_kind':'between-anchors-unique-exact','left_anchor_pc':lpc,'right_anchor_pc':rpc})
   stats['resolved']+=1
  elif len(candidates)>1:stats['multi_candidate']+=1
  else:stats['no_candidate']+=1
OUT.parent.mkdir(parents=True,exist_ok=True)
fields=list(out[0]) if out else []
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps(dict(stats),indent=2));print('rows',len(out),'unique_sw',len(set((r['scene'],r['sw_code_index']) for r in out)),'unique_pc_per_scene',len(set((r['scene'],r['pc_event_index']) for r in out)));print(OUT)

