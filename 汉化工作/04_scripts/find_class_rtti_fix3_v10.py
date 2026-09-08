from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');rb=(D/'rodata.bin').read_bytes();base=0x1A3000
for key in [b'cTitleMenu',b'TitleMenu',b'cConfigWin']:
 print('\nKEY',key.decode())
 st=0
 while True:
  o=rb.find(key,st)
  if o<0:break
  s=rb.rfind(b'\0',max(0,o-120),o)+1;e=rb.find(b'\0',o,min(len(rb),o+300));e=e if e>=0 else o+150
  raw=rb[s:e]
  try:t=raw.decode('utf-8')
  except:t=raw.decode('utf-8','replace')
  print(hex(base+o),repr(t));st=o+1
