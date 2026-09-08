from pathlib import Path
import re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
roots=[R/'05_build/script_package/SCRIPT.PAK_unpacked',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked',R/'03_text/ui_work/SYSCG2.PAK_unpacked',R/'03_text/ui_work/PARTS2.PAK_unpacked']
terms=re.compile(r'(?i)(config|configuration|basic|button|touch|text|sound|voice|message|speed|window|opacity|auto|skip|volume|language|vibration|font|display|bgm|se |character|read |unread|controller|cursor|save|load|title|manual|new game|after story|dangopedia)')
pat=re.compile(rb'(?:[\x20-\x7e]\x00){3,}')
for root in roots:
 if not root.exists(): continue
 for p in sorted(x for x in root.iterdir() if x.is_file()):
  b=p.read_bytes(); hits=[]
  for m in pat.finditer(b):
   try:t=m.group().decode('utf-16le').strip()
   except:continue
   if terms.search(t):hits.append((m.start(),t))
  if hits:
   print(f'### {root.name}/{p.name} len={len(b)} hits={len(hits)}')
   for off,t in hits[:200]: print(off,repr(t))
