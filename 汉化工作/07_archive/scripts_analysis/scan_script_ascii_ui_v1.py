from pathlib import Path
import re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/script_package/SCRIPT.PAK_unpacked'
terms=re.compile(r'(?i)(config|configuration|button|touch|text|sound|voice|auto|skip|window|font|speed|volume|language|save|load|title|manual|new game|after story|dangopedia|display|message|opacity|vibration)')
for p in sorted(D.iterdir()):
 if not p.is_file():continue
 b=p.read_bytes()
 ss=[]
 for m in re.finditer(rb'[ -~]{4,}',b):
  try:s=m.group().decode('ascii')
  except:continue
  if terms.search(s): ss.append((m.start(),s[:180]))
 if ss:
  print('\n###',p.name,len(b))
  for off,s in ss[:120]: print(off,repr(s))
