from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
for lo,hi in [(0x17a430,0x17a630),(0x17bcf0,0x17bdb0)]:
 print('\nRANGE',hex(lo),hex(hi))
 for x in md.disasm(b[lo:hi],lo):print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
# callers to prologue-ish addresses in ranges
candidates=[]
for i,x in enumerate(ins):
 if x.address in range(0x17a430,0x17a630,4) and x.mnemonic in ('stp','str') and 'sp, #-' in x.op_str:candidates.append(x.address)
 if x.address in range(0x17bcf0,0x17bdb0,4) and x.mnemonic in ('stp','str') and 'sp, #-' in x.op_str:candidates.append(x.address)
print('CAND',list(map(hex,candidates)))
for t in candidates:
 refs=[x.address for x in ins if x.mnemonic=='bl' and x.operands and x.operands[0].type==ARM64_OP_IMM and x.operands[0].imm==t]
 if refs:print('CALLERS',hex(t),list(map(hex,refs)))
