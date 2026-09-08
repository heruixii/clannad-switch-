from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();RB=0x1A3000
# enumerate UTF-8 null strings containing 下一/返回/是/否 and <=12 chars
for needle in ['下一','返回','是','否']:
 print('\n##',needle)
 pos=0
 while True:
  o=rb.find(needle.encode('utf-8'),pos)
  if o<0:break
  # find string start after previous null within 120 bytes
  st=rb.rfind(b'\0',max(0,o-120),o)+1;z=rb.find(b'\0',o,min(len(rb),o+160))
  if z>o:
   try:s=rb[st:z].decode('utf-8')
   except:s=''
   if s and len(s)<=30:print(hex(RB+st),repr(s))
  pos=o+1
