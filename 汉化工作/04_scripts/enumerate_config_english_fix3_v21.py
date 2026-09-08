from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def cstr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+1200))
 if e<0:return None
 try:s=rb[o:e].decode('utf-8')
 except:return None
 if not s:return None
 return s
rows=[]
for i,x in enumerate(ins):
 if not (0x150000<=x.address<0x157000):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=cstr(a)
   if s is not None:
    ascii_letters=sum(('a'<=ch.lower()<='z') for ch in s); nonascii=sum(ord(ch)>127 for ch in s)
    rows.append((x.address,y.address,a,s,ascii_letters,nonascii))
   break
# unique English-like strings, keep code refs
from collections import defaultdict
u=defaultdict(list)
for a,b,c,s,al,na in rows:
 if al>=2 and al>=na and len(s)<=500:u[s].append((a,b,c))
print('UNIQUE_ENGLISH',len(u))
for k,(s,refs) in enumerate(sorted(u.items(),key=lambda kv:min(x[0] for x in kv[1]))):
 print(f'{k:03d}\t{min(x[0] for x in refs):08X}\t{refs[0][2]:08X}\t{len(s.encode())}\t{s!r}')
