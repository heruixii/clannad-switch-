from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));by={x.address:i for i,x in enumerate(ins)}
target=0x143860
callers=[]
for x in ins:
 if x.mnemonic=='bl' and len(x.operands)==1 and x.operands[0].type==ARM64_OP_IMM and x.operands[0].imm==target:callers.append(x.address)
print('CALLERS',len(callers),[hex(x) for x in callers])
for a in callers:
 i=by[a];print('\n### caller',hex(a))
 for z in ins[max(0,i-18):min(len(ins),i+18)]:print(f'{z.address:08X} {z.mnemonic:<8} {z.op_str}')
# callers to name-default checker d2e0 too
for target in [0xd2e0,0x144f0]:
 hs=[]
 for x in ins:
  if x.mnemonic=='bl' and len(x.operands)==1 and x.operands[0].type==ARM64_OP_IMM and x.operands[0].imm==target:hs.append(x.address)
 print('\nTARGET',hex(target),'CALLERS',len(hs),[hex(x) for x in hs[:100]])
