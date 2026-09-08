from pathlib import Path
import hashlib,re,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
paths={'orig':R/'03_text/switch_work/script_probe/SCRIPT.PAK_unpacked/_KEYWORD','final':R/'05_build/script_package/SCRIPT.PAK_unpacked/_KEYWORD'}
for k,p in paths.items():
 b=p.read_bytes();print('\n##',k,len(b),hashlib.sha256(b).hexdigest().upper());print('HEAD',b[:96].hex(' '));
 for enc in ['utf-8','shift_jis','cp932','utf-16le']:
  try:s=b.decode(enc,errors='ignore')
  except:continue
  runs=[]
  cur=''
  for c in s:
   if c=='\x00' or ord(c)<0x20:
    if len(cur)>=4:runs.append(cur)
    cur=''
   else:cur+=c
  if len(cur)>=4:runs.append(cur)
  print(enc,'runs',len(runs))
  for x in runs[:12]:print(' ',repr(x[:200]))
print('EQUAL',paths['orig'].read_bytes()==paths['final'].read_bytes())
