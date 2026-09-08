from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');M=ROOT/'03_text/matched/switch_pc_v10/safe_matches.tsv';OUT=ROOT/'03_text/translated/message_targets_v10.tsv'
CTRL=re.compile(r'\$\[[^\]]*\]|\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def clean(s):return (s or '').replace('"','').replace('\r','').strip('\ufeff')
def parse_pc(s):
 s=clean(s);m=re.match(r'^【([^】]+)】(.*)$',s,re.S)
 return (m.group(1),m.group(2)) if m else ('',s)
def swsp(s):
 return s[1:s.find('@')] if s.startswith('`') and '@' in s else ''
rows=rd(M);spcnt=collections.defaultdict(collections.Counter)
for r in rows:
 a=swsp(r['sw_jp_text']);b,_=parse_pc(r['pc_zh_text'])
 if a and b:spcnt[a][b]+=1
spmap={a:c.most_common(1)[0][0] for a,c in spcnt.items()}
out=[];stats=collections.Counter();bad=[]
for r in rows:
 sw=r['sw_jp_text'];zhsp,body=parse_pc(r['pc_zh_text']);jpsp=swsp(sw)
 if jpsp:
  sp=zhsp or spmap.get(jpsp,jpsp)
  if not body and r['pc_zh_text']:bad.append((r['scene'],r['sw_code_index'],'empty-body',sw,r['pc_zh_text']))
  target='`'+sp+'@'+body
  if zhsp:stats['dialogue-pc-speaker']+=1
  else:stats['dialogue-fallback-speaker']+=1
 else:
  target=body;stats['narration']+=1
 controls=CTRL.findall(sw)
 out.append({'scene':r['scene'],'code_index':r['sw_code_index'],'source':'pc-safe','jp_text':sw,'en_text':r['sw_en_text'],'zh_text':target,'original_controls':'|'.join(controls),'pc_status':r['pc_status'],'match_kind':r['match_kind']})
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'rows':len(out),'stats':dict(stats),'speaker_keys':len(spmap),'bad':bad[:20]},ensure_ascii=False,indent=2));print('TOP SPEAKERS')
for a,c in sorted(spcnt.items(),key=lambda kv:-sum(kv[1].values()))[:70]:print(repr(a),'->',repr(c.most_common(5)))
print(OUT)
