from pathlib import Path
import re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();BASE=0x1A3000
# scan all NUL-terminated utf8 strings containing name/voice concepts
pos=0;hits=[]
while pos<len(rb):
 z=rb.find(b'\0',pos)
 if z<0:z=len(rb)
 raw=rb[pos:z]
 if 3<=len(raw)<=800:
  try:s=raw.decode('utf-8')
  except:s=''
  if s and any(k in s for k in ['朋也','主人公','名字','名称','姓名','語音','语音','ボイス','voice','Voice','岡崎','冈崎']):
   hits.append((BASE+pos,s))
 pos=z+1
for a,s in hits:
 print(hex(a),repr(s))
print('COUNT',len(hits))
