from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed'); tb=(D/'text.bin').read_bytes(); rb=(D/'rodata.bin').read_bytes(); RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def s_at(a):
 if not(RB<=a<RB+len(rb)):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+1000));e=e if e>=0 else min(len(rb),o+1000)
 try:return rb[o:e].decode('utf-8')
 except:return None
# detect groups centered on adrp x0 + add x0 string pointer, within init 0x1800-0x3090
rows=[]
for i,x in enumerate(ins):
 if not(0x1800<=x.address<0x3090):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or md.reg_name(x.operands[0].reg)!='x0' or x.operands[1].type!=ARM64_OP_IMM:continue
 page=x.operands[1].imm
 en=None;jadd=None
 for j in range(i+1,min(i+4,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and md.reg_name(y.operands[0].reg)=='x0' and md.reg_name(y.operands[1].reg)=='x0' and y.operands[2].type==ARM64_OP_IMM:
   en=page+y.operands[2].imm;jadd=j;break
 if not en or not s_at(en): continue
 # nearest prior got ldr within 8 ins, page 0x247000/0x248000/0x249000
 slot=None
 for k in range(i-1,max(-1,i-10),-1):
  y=ins[k]
  if y.mnemonic=='ldr' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_MEM:
   base=y.operands[1].mem.base;disp=y.operands[1].mem.disp
   # find adrp setting base within 2 prior
   for h in range(k-1,max(-1,k-4),-1):
    z=ins[h]
    if z.mnemonic=='adrp' and z.operands[0].reg==base and z.operands[1].type==ARM64_OP_IMM:
     slot=z.operands[1].imm+disp
     break
   if slot:break
 if not slot: continue
 # infer other language ptrs by examining stack setup around i +/- 20 with adrp/add registers tracked
 ptr_by_reg={}
 lang={}
 for k in range(max(0,i-18),min(len(ins),i+22)):
  y=ins[k]
  if y.mnemonic=='adrp' and len(y.operands)>1 and y.operands[1].type==ARM64_OP_IMM:
   r=y.operands[0].reg;pg=y.operands[1].imm
   for h in range(k+1,min(k+4,len(ins))):
    z=ins[h]
    if z.mnemonic=='add' and len(z.operands)>=3 and z.operands[0].type==ARM64_OP_REG and z.operands[1].type==ARM64_OP_REG and z.operands[0].reg==r and z.operands[1].reg==r and z.operands[2].type==ARM64_OP_IMM:
     ptr_by_reg[r]=pg+z.operands[2].imm;break
  if y.mnemonic=='str' and len(y.operands)>=2 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==ARM64_REG_SP:
   off=y.operands[1].mem.disp;a=ptr_by_reg.get(y.operands[0].reg)
   if a and s_at(a) is not None:
    if off==0:lang['jp']=a
    elif off==0x18:lang['zh']=a
    elif off==0x20:lang['zht']=a
  if y.mnemonic=='stp' and len(y.operands)>=3 and y.operands[2].type==ARM64_OP_MEM and y.operands[2].mem.base==ARM64_REG_SP:
   off=y.operands[2].mem.disp
   if off in (0,8,0x30):
    for pos,rname in [(0,y.operands[0].reg),(1,y.operands[1].reg)]:
     a=ptr_by_reg.get(rname)
     if not a or s_at(a) is None:continue
     if off==8 and pos==0:lang['en']=a
     elif off==8 and pos==1:lang['fr']=a
     elif off==0 and pos==0:lang.setdefault('jp',a)
     elif off==0x30 and pos==0:lang.setdefault('jp',a)
 # force en
 lang['en']=en
 row={'slot':slot,'code':x.address,**{k:s_at(v) for k,v in lang.items()}}
 rows.append(row)
# dedup by slot/code
seen=set();out=[]
for r in rows:
 key=(r['slot'],r['code'])
 if key in seen:continue
 seen.add(key);out.append(r)
for r in out:
 print(hex(r['slot']),hex(r['code']),'EN=',repr(r.get('en')),'ZH=',repr(r.get('zh')),'JP=',repr(r.get('jp')),'FR=',repr(r.get('fr')),'ZHT=',repr(r.get('zht')))
(D/'ui_groups_slots_v69.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('COUNT',len(out))
