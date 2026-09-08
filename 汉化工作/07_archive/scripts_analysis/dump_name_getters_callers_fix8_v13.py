from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0)); by={x.address:i for i,x in enumerate(ins)}
# detailed ranges
for lo,hi,name in [(0x5dca0,0x5de30,'JP defaults/helper'),(0x5ed20,0x5f080,'current-name helpers')]:
 print('\n###',name)
 for x in md.disasm(tb[lo:hi],lo): print(f'{x.address:08X} {x.mnemonic:<8} {x.op_str}')
# direct BL callers to likely starts around this region
starts=[0x5dc70,0x5dd68,0x5ed30,0x5ed78,0x5ee2c,0x5eee0,0x5f04c]
print('\n### CALLERS')
for target in starts:
 hs=[]
 for x in ins:
  if x.mnemonic=='bl' and len(x.operands)==1 and x.operands[0].type==ARM64_OP_IMM and x.operands[0].imm==target:hs.append(x.address)
 print(hex(target),[hex(a) for a in hs])
