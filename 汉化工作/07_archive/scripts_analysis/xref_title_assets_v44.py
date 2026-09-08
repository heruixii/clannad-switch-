from pathlib import Path
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from capstone.arm64 import ARM64_OP_REG,ARM64_OP_IMM
import json,re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');text=(D/'text.bin').read_bytes();ro=(D/'rodata.bin').read_bytes();RB=0x1A3000
# enumerate title-ish strings in rodata
runs=[]
for m in re.finditer(rb'[\x20-\x7e]{3,}',ro):
 s=m.group().decode('ascii','ignore')
 if 'TITLE' in s.upper() or 'Title' in s or 'TITLE_' in s:
  runs.append((s,RB+m.start()))
print('STRINGS',[(s,hex(a)) for s,a in runs[:200]])
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(text,0));idx={x.address:i for i,x in enumerate(ins)}
refs=[]
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 reg=x.operands[0].reg;page=x.operands[1].imm
 for y in ins[i+1:min(i+9,len(ins))]:
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[2].type==ARM64_OP_IMM and y.operands[0].reg==reg and y.operands[1].reg==reg:
   refs.append((page+y.operands[2].imm,x.address,y.address));break
out=[]
for s,a in runs:
 for _,xr,add in [r for r in refs if r[0]==a]:
  i=idx[xr];lo=max(0,i-80);hi=min(len(ins),i+120)
  out.append({'string':s,'addr':hex(a),'xref':hex(xr),'asm':[f'{z.address:08X}: {z.mnemonic} {z.op_str}' for z in ins[lo:hi]]})
print('XREF_COUNT',len(out));print(json.dumps(out,ensure_ascii=False,indent=2));(D/'title_asset_xrefs_v44.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
