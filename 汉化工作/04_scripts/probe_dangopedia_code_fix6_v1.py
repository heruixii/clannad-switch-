from pathlib import Path
from capstone import *
from capstone.arm64 import *
import re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
for pat in [b'Dangopedia',b'Keyword',b'keyword',b'CL_DP',b'_KEYWORD']:
 print('\nPAT',pat)
 st=0
 while True:
  o=rb.find(pat,st)
  if o<0:break
  a=RB+o
  print(hex(a),rb[o:o+120].split(b'\0')[0])
  st=o+1
