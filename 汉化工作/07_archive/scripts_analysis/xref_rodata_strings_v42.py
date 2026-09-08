from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from capstone.arm64 import ARM64_OP_REG,ARM64_OP_IMM
import json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');text=(D/'text.bin').read_bytes();ro=(D/'rodata.bin').read_bytes();ROBASE=0x1A3000
terms=['task::TitleMenu','Game Start','Dangopedia','MANUAL','task::ConfigWin','Basic operation','Quick Load','Settings','Select Language','Continue','task::NameEdit','task::Manual','task::CGMode','task::MusicMode']
targets={}
for t in terms:
 q=t.encode();st=0
 while True:
  o=ro.find(q,st)
  if o<0:break
  targets.setdefault(t,[]).append(ROBASE+o);st=o+1
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
ins=list(md.disasm(text,0)); byaddr={x.address:i for i,x in enumerate(ins)}
refs=[]
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 reg=x.operands[0].reg; page=x.operands[1].imm
 for j in range(i+1,min(i+9,len(ins))):
  y=ins[j]
  if y.mnemonic=='.byte':continue
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[2].type==ARM64_OP_IMM and y.operands[0].reg==reg and y.operands[1].reg==reg:
   refs.append((page+y.operands[2].imm,x.address,y.address));break
  if y.operands and y.operands[0].type==ARM64_OP_REG and y.operands[0].reg==reg and y.mnemonic not in ('ldr','ldrb','ldrh','str','strb','strh','cmp','cbz','cbnz','mov'):
   break
out=[]
for term,addrs in targets.items():
 for ta in addrs:
  for addr,adrp,add in [r for r in refs if r[0]==ta]:
   idx=byaddr[adrp]
   # use nearest stp x29,x30-ish or ret boundary. just +/- 300 instructions for refs
   lo=max(0,idx-300);hi=min(len(ins)-1,idx+500)
   # trim at ret
   for k in range(idx-1,lo-1,-1):
    if ins[k].mnemonic=='ret':lo=k+1;break
   for k in range(idx+1,hi+1):
    if ins[k].mnemonic=='ret':hi=k;break
   funrefs=[]
   for a,aa,bb in refs:
    if ins[lo].address<=aa<=ins[hi].address and ROBASE<=a<ROBASE+len(ro):
     o=a-ROBASE;end=ro.find(b'\0',o,min(len(ro),o+180));end=end if end>=0 else min(len(ro),o+180);raw=ro[o:end]
     try:ss=raw.decode('utf-8')
     except:ss=raw.decode('utf-8','ignore')
     if ss and all(ord(c)>=32 for c in ss):funrefs.append((hex(a),ss[:160]))
   uniq=[];seen=set()
   for z in funrefs:
    if z not in seen:seen.add(z);uniq.append({'addr':z[0],'text':z[1]})
   out.append({'term':term,'target':hex(ta),'xref':hex(adrp),'function_range':[hex(ins[lo].address),hex(ins[hi].address)],'rodata_refs':uniq,'asm':[f'{z.address:08X}: {z.mnemonic} {z.op_str}' for z in ins[max(lo,idx-12):min(hi+1,idx+24)]]})
print('INS',len(ins),'ADRP',sum(x.mnemonic=='adrp' for x in ins),'REFS',len(refs),'XREFS',len(out));print(json.dumps(out,ensure_ascii=False,indent=2));(D/'xref_v42.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
