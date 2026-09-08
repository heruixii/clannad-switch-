from pathlib import Path
import re,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');b=p.read_bytes()
patterns=[r'new.{0,3}game',r'load.{0,5}game',r'after.{0,5}story',r'cg.{0,5}mode',r'music.{0,5}mode',r'config(?:uration)?',r'\bname\b',r'dango.{0,8}pedia',r'manual',r'continue',r'extra',r'gallery']
# collect printable ASCII runs with file offsets
runs=[]
for m in re.finditer(rb'[\x20-\x7e]{3,}',b):
 s=m.group().decode('ascii','ignore')
 for pat in patterns:
  if re.search(pat,s,re.I):
   runs.append({'offset':m.start(),'text':s,'pattern':pat})
   break
# prioritize title neighborhood
runs.sort(key=lambda r:(0 if 1135000<=r['offset']<=1165000 else 1,r['offset']))
print(json.dumps(runs[:600],ensure_ascii=False,indent=2));(p.parent/'title_label_variants_v31.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',len(runs),'NEAR',sum(1135000<=r['offset']<=1165000 for r in runs))
