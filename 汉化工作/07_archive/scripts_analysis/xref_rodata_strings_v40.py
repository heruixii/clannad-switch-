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
print('TARGETS', {k:[hex(x) for x in v] for k,v in targets.items()})
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True
ins=list(md.disasm(text,0))
# map address -> index
byaddr={x.address:i for i,x in enumerate(ins)}
# collect ADRP+ADD refs within next 5 ins, allowing same register
refs=[]
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 reg=x.operands[0].reg; page=x.operands[1].imm
 # capstone imm should be absolute page relative to current pc
 for j in range(i+1,min(i+7,len(ins))):
  y=ins[j]
  # register overwritten before use
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[2].type==ARM64_OP_IMM and y.operands[0].reg==reg and y.operands[1].reg==reg:
   addr=page+y.operands[2].imm;refs.append((addr,x.address,y.address));break
  # ldr with base reg not handled yet
  if y.operands and y.operands[0].type==ARM64_OP_REG and y.operands[0].reg==reg and y.mnemonic not in ('ldr','ldrb','ldrh','str','strb','strh','cmp','cbz','cbnz','mov'):
   break
# exact target refs
out=[]
for term,addrs in targets.items():
 for ta in addrs:
  rr=[r for r in refs if r[0]==ta]
  for addr,adrp,add in rr:
   idx=byaddr[adrp]
   # approximate function start by previous ret boundary, bounded 1500 ins
   sidx=max(0,idx-1500)
   for k in range(idx-1,sidx-1,-1):
    if ins[k].mnemonic=='ret':sidx=k+1;break
   eidx=min(len(ins)-1,idx+1500)
   for k in range(idx+1,eidx+1):
    if ins[k].mnemonic=='ret':eidx=k;break
   # refs within function to rodata strings; resolve printable NUL strings at address
   funrefs=[]
   for a,aa,bb in refs:
    if ins[sidx].address<=aa<=ins[eidx].address and ROBASE<=a<ROBASE+len(ro):
     o=a-ROBASE;end=ro.find(b'\0',o,min(len(ro),o+180));
     if end<0:end=min(len(ro),o+180)
     raw=ro[o:end]
     try:ss=raw.decode('utf-8')
     except:ss=raw.decode('utf-8','ignore')
     if ss and all(ord(c)>=32 for c in ss):funrefs.append({'addr':hex(a),'text':ss[:160]})
   uniq=[];seen=set()
   for z in funrefs:
    key=(z['addr'],z['text'])
    if key not in seen:seen.add(key);uniq.append(z)
   ctx=[f"{z.address:08X}: {z.mnemonic} {z.op_str}" for z in ins[max(sidx,idx-15):min(eidx+1,idx+30)]]
   out.append({'term':term,'target':hex(ta),'xref_adrp':hex(adrp),'xref_add':hex(add),'function_start':hex(ins[sidx].address),'function_end':hex(ins[eidx].address),'function_rodata_refs':uniq,'context':ctx})
print(json.dumps(out,ensure_ascii=False,indent=2));(D/'xref_v40.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('XREFS',len(out),'ALL_REFS',len(refs))
