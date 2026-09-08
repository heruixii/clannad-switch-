from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0));addr={x.address:i for i,x in enumerate(ins)}
# all writes to immediate displacement 0x8c on any base, plus stp spanning 0x8c
hits=[]
for i,x in enumerate(ins):
 if x.mnemonic in ('str','stur','strb','strh') and len(x.operands)>1 and x.operands[1].type==ARM64_OP_MEM and x.operands[1].mem.disp==0x8c:
  hits.append(i)
 elif x.mnemonic=='stp' and len(x.operands)>2 and x.operands[2].type==ARM64_OP_MEM and x.operands[2].mem.disp==0x8c:
  hits.append(i)
print('WRITE_COUNT',len(hits))
for i in hits:
 x=ins[i];print('\nWRITE',hex(x.address),x.mnemonic,x.op_str)
 for q in ins[max(0,i-10):min(len(ins),i+14)]:print(f'{q.address:08X}: {q.mnemonic:<8} {q.op_str}')
