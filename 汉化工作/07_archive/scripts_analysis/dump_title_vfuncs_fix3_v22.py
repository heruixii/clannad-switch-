from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
funcs=[0x179270,0x17a2b0,0x17a620,0x17a710,0x17ba20,0x17bdb0,0x17be60,0x17bf20,0x17bfd0,0x17bda0,0x17ea80,0x17f540]
for st in funcs:
 print('\n### FUNC',hex(st))
 data=b[st:min(len(b),st+0x1800)]
 cnt=0
 for x in md.disasm(data,st):
  print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
  cnt+=1
  if x.mnemonic=='ret' and cnt>3:break
