from pathlib import Path
from capstone import *
from capstone.arm64 import *
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def cstr(a):
 if not(RB<=a<RB+len(rb)):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+1000))
 if e<0:return None
 try:s=rb[o:e].decode('utf-8')
 except:return None
 if not s or any(ord(c)<9 for c in s):return None
 return s
stores=[]
lo,hi=0x150000,0x157000
for i,x in enumerate(ins):
 if not(lo<=x.address<hi):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 addi=None;addr=None
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   addr=pg+y.operands[2].imm;addi=j;break
 if addi is None:continue
 s=cstr(addr)
 if not s:continue
 for k in range(addi+1,min(addi+15,len(ins))):
  z=ins[k]
  if z.mnemonic=='str' and len(z.operands)>1 and z.operands[0].type==ARM64_OP_REG and z.operands[0].reg==r and z.operands[1].type==ARM64_OP_MEM and z.operands[1].mem.base==ARM64_REG_SP:
   stores.append({'adrp':x.address,'add':ins[addi].address,'store':z.address,'off':z.operands[1].mem.disp,'addr':addr,'s':s});break
  # stop if same reg overwritten
  if k>addi+1 and z.operands and z.operands[0].type==ARM64_OP_REG and z.operands[0].reg==r and z.mnemonic not in ('str','cmp','cbz','cbnz','tbnz','tbz'):
   break
# pair nearest JP/CJK and ASCII EN at off/+8 within 0x100 bytes of code
def has_cjk(s):return any('\u3000'<=c<='\u9fff' for c in s)
def is_en(s):return all(ord(c)<128 or c in '❝❞“”' for c in s) and any(c.isalpha() for c in s)
pairs=[];used=set()
for a in stores:
 if not has_cjk(a['s']):continue
 cand=[b for b in stores if b['off']==a['off']+8 and 0<b['adrp']-a['adrp']<0x120 and is_en(b['s'])]
 if cand:
  b=min(cand,key=lambda x:x['adrp']-a['adrp']);pairs.append((a,b))
print('STORES',len(stores),'PAIRS',len(pairs))
for n,(a,b) in enumerate(pairs):
 print(f"{n:03d}\t{a['adrp']:08X}\t{b['adrp']:08X}\tSP+{a['off']:X}\tJP={a['s']!r}\tEN={b['s']!r}")
