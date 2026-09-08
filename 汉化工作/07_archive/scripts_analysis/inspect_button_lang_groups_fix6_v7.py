from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
# dump strings around short button terms
terms=['Yes','No','Next','Back','Close','Cancel','Delete','Latest','Continue','Return','Save','Load']
for t in terms:
 print('\n##',t)
 st=0
 while True:
  o=rb.find(t.encode()+b'\0',st)
  if o<0:break
  a=RB+o
  print('ADDR',hex(a))
  lo=max(0,o-180);hi=min(len(rb),o+260);chunk=rb[lo:hi]
  # print null-separated utf8 candidates around
  base=RB+lo;pos=0
  while pos<len(chunk):
   z=chunk.find(b'\0',pos)
   if z<0:break
   raw=chunk[pos:z]
   if raw:
    try:s=raw.decode('utf-8')
    except:s=''
    if s and all((ord(c)>=32 or c in '\t\r\n') for c in s):print(hex(base+pos),repr(s[:160]))
   pos=z+1
  st=o+1
# disasm localization init around short buttons
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
for x in md.disasm(tb[0x1b00:0x1d20],0x1b00):print(f'{x.address:08X}: {x.mnemonic:8s} {x.op_str}')
