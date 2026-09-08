from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();BASE=0x1A3000
for lo,hi,name in [(0x1e0d80,0x1e1000,'JP name cluster'),(0x1e3000,0x1e3300,'JP reset cluster'),(0x1e4c80,0x1e5a80,'EN name cluster')]:
 print('\n##',name)
 a=lo-BASE;b=hi-BASE;seg=rb[a:b]
 pos=0
 while pos<len(seg):
  z=seg.find(b'\0',pos)
  if z<0:z=len(seg)
  raw=seg[pos:z]
  if len(raw)>=3:
   try:s=raw.decode('utf-8')
   except:s=''
   if s and (any(ord(c)>127 for c in s) or any(c.isalpha() for c in s)):
    print(hex(lo+pos),repr(s))
  pos=z+1
