from pathlib import Path
from capstone import *
from capstone.arm64 import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(b,0))
# approximate function starts by previous RET/UDF alignment within 0x400 bytes
def fstart(i):
 j=i
 while j>0 and i-j<300:
  if ins[j-1].mnemonic=='ret': return ins[j].address
  if ins[j-1].mnemonic=='udf' and (j>=2 and ins[j-2].mnemonic=='udf'): return ins[j].address
  j-=1
 return ins[max(0,j)].address
hits=[]
for i,x in enumerate(ins):
 if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==0x247000:
  r=x.operands[0].reg
  for j in range(i+1,min(i+4,len(ins))):
   y=ins[j]
   if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==r and y.operands[1].mem.disp==0xaa8:
    obj=y.operands[0].reg
    for k in range(j+1,min(j+16,len(ins))):
     z=ins[k]
     if z.mnemonic in ('ldr','ldrsw') and len(z.operands)>1 and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==obj and z.operands[1].mem.disp==0x8c:
      hits.append((x.address,z.address,fstart(i)));break
    break
print('COUNT',len(hits))
from collections import Counter,defaultdict
d=defaultdict(list)
for a,l,f in hits:d[f].append((a,l))
for f,hs in sorted(d.items()):
 print(hex(f),'n',len(hs),'reads',','.join(hex(x[1]) for x in hs))
