from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; ZH=ROOT/'03_text/translated/message_targets_complete_v12.tsv'; OUT=ROOT/'03_text/translated/message_control_issues_v12.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
# ruby is intentionally allowed to disappear in Chinese; these are execution/display controls that must remain
CTRL=re.compile(r'\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|\\n|[＊％][Ａ-ＺA-Z]')
sw=rd(SW); zh=rd(ZH); zm={(r['scene'],r['code_index']):r for r in zh}; issues=[];stats=collections.Counter()
for s in sw:
 z=zm[(s['scene'],s['code_index'])]['zh_text']; a=CTRL.findall(s['jp_text']);b=CTRL.findall(z);miss=[]
 for x in set(a):
  if b.count(x)<a.count(x):miss.append(x)
 if miss:
  issues.append({'scene':s['scene'],'code_index':s['code_index'],'missing':'|'.join(miss),'jp_text':s['jp_text'],'zh_text':z,'source':zm[(s['scene'],s['code_index'])]['source']});stats[zm[(s['scene'],s['code_index'])]['source'].split(':')[0]]+=1
if issues:
 with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(issues[0]),delimiter='\t');w.writeheader();w.writerows(issues)
print(json.dumps({'rows':len(sw),'issues':len(issues),'by_source':dict(stats)},ensure_ascii=False,indent=2));print(OUT)
