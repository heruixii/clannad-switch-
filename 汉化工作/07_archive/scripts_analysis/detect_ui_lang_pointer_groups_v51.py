from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from capstone.arm64 import ARM64_OP_REG,ARM64_OP_IMM,ARM64_OP_MEM,ARM64_REG_SP
import json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0));
def ptr_load(i):
 x=ins[i]
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:return None
 r=x.operands[0].reg; page=x.operands[1].imm
 for j in range(i+1,min(i+4,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[2].type==ARM64_OP_IMM and y.operands[0].reg==r and y.operands[1].reg==r:
   return r,page+y.operands[2].imm,j
 return None
loads={i:ptr_load(i) for i in range(len(ins))};loads={i:v for i,v in loads.items() if v}
# helper get UTF8 NUL string
def s_at(a):
 if not(RB<=a<RB+len(rb)):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+1000));e=e if e>=0 else min(len(rb),o+1000)
 try:return rb[o:e].decode('utf-8')
 except:return None
# strict template: x0 adrp+add; then within 28 ins, x0 appears in stp to [sp,#8], and a pointer register stored to [sp,#0x18].
g=[]
for i,(r,en,jadd) in loads.items():
 if md.reg_name(r)!='x0':continue
 en_s=s_at(en)
 if not en_s or not en_s.strip():continue
 found_en_store=False; zhs=None; zht=None; fr=None; jp=None
 # track pointer loads by reg in window
 recent={}
 for k in range(max(0,i-8),min(len(ins),i+35)):
  if k in loads:
   rr,aa,jj=loads[k]; recent[rr]=(aa,k,jj)
  y=ins[k]
  # stp regs to sp offset
  if y.mnemonic=='stp' and len(y.operands)>=3 and y.operands[2].type==ARM64_OP_MEM and y.operands[2].mem.base==ARM64_REG_SP:
   off=y.operands[2].mem.disp
   r1=y.operands[0].reg if y.operands[0].type==ARM64_OP_REG else None; r2=y.operands[1].reg if y.operands[1].type==ARM64_OP_REG else None
   if off==8 and r1==r: found_en_store=True; fr=recent.get(r2,(None,None,None))[0]
  if y.mnemonic=='str' and len(y.operands)>=2 and y.operands[1].type==ARM64_OP_MEM and y.operands[1].mem.base==ARM64_REG_SP:
   off=y.operands[1].mem.disp; rr=y.operands[0].reg if y.operands[0].type==ARM64_OP_REG else None
   if off==0: jp=recent.get(rr,(None,None,None))[0]
   elif off==0x18: zhs=recent.get(rr,(None,None,None))[0]
   elif off==0x20: zht=recent.get(rr,(None,None,None))[0]
 if found_en_store and zhs and s_at(zhs):
  g.append({'adrp_off':ins[i].address,'add_off':ins[jadd].address,'en_addr':en,'zh_addr':zhs,'jp_addr':jp,'fr_addr':fr,'zht_addr':zht,'en':en_s,'zh':s_at(zhs),'jp':s_at(jp) if jp else None,'fr':s_at(fr) if fr else None,'zht':s_at(zht) if zht else None})
# dedup by instruction
ded={x['adrp_off']:x for x in g};g=[ded[k] for k in sorted(ded)]
print('GROUPS',len(g))
for x in g:
 print(f"{x['adrp_off']:08X} EN={x['en']!r} -> ZH={x['zh']!r} JP={x['jp']!r} FR={x['fr']!r} ZHT={x['zht']!r}")
(D/'ui_lang_pointer_groups_v51.json').write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
