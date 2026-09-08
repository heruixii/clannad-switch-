from pathlib import Path
import re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'05_build/script_package/SCRIPT.PAK_unpacked'
for name in ['_VARSTR','_SCR_LABEL','_KEYWORD','Z_TEST']:
 p=D/name; b=p.read_bytes(); print('\n###',name,'len',len(b),'head',b[:64].hex())
 for enc in ['utf-8','utf-16le','cp932','shift_jis','latin1']:
  try:s=b.decode(enc,errors='ignore')
  except:continue
  found=[]
  for line in re.split(r'[\x00\r\n]+',s):
   line=line.strip()
   if len(line)>=3 and (re.search(r'(?i)config|button|touch|text|sound|voice|save|load|title|manual|new game|after story|language|window|message|speed|auto|skip',line) or any('\u3040'<=c<='\u9fff' for c in line)):
    found.append(line[:220])
  if found:
   print('ENC',enc,'hits',len(found))
   for x in found[:100]: print(repr(x).encode('unicode_escape').decode())

