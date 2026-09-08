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
 return s or None
# collect all adrp+add string refs once
from collections import defaultdict
refs=defaultdict(list)
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm
   if cstr(a) is not None:refs[a].append((x.address,y.address))
   break
# config english addresses
cfg={}
for a,rr in refs.items():
 s=cstr(a)
 if not s:continue
 if any(0x150000<=x<0x157000 for x,y in rr):
  al=sum(('a'<=ch.lower()<='z') for ch in s);na=sum(ord(ch)>127 for ch in s)
  if al>=2 and al>=na and len(s)<=500:cfg[a]=s
safe=[]
for a,s in cfg.items():
 allr=refs[a]; outside=[r for r in allr if not (0x150000<=r[0]<0x157000)]
 if not outside and len(s.encode())>=20:safe.append((a,len(s.encode())+1,s,len(allr)))
print('CONFIG_STRINGS',len(cfg),'SAFE_HOSTS>=20',len(safe),'CAPACITY',sum(n for _,n,_,_ in safe))
for a,n,s,k in sorted(safe,key=lambda x:x[1],reverse=True): print(hex(a),n,k,repr(s[:100]))
