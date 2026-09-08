from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
tb=(D/'text.bin').read_bytes(); rb=(D/'rodata.bin').read_bytes(); RB=0x1A3000
terms=['NEW GAME','New Game','Game Start','LOAD','Load','AFTER STORY','After Story','CG MODE','CG Mode','MUSIC MODE','Music Mode','CONFIG','Config','Settings','NAME','Name','DANGOPEDIA','Dangopedia','MANUAL','Manual']
# exact nul strings / starts
strings=[]
for t in terms:
 q=t.encode('utf-8')+b'\0';st=0
 while True:
  o=rb.find(q,st)
  if o<0: break
  strings.append((t,RB+o));st=o+1
print('STRINGS')
for t,a in strings: print(t,hex(a))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
print('\nXREFS TITLE REGION')
for t,a in strings:
 page=a&~0xfff;off=a&0xfff;hits=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==page:
   r=x.operands[0].reg
   for j in range(i+1,min(i+5,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==off:
     hits.append((x.address,y.address));break
 for h in hits:
  if 0x176000<=h[0]<0x181000:
   print(t,hex(a),'xref',hex(h[0]),hex(h[1]))
   idx=next(k for k,z in enumerate(ins) if z.address==h[0])
   for z in ins[max(0,idx-12):min(len(ins),idx+26)]:print(f'{z.address:08X}: {z.mnemonic:<8} {z.op_str}')
