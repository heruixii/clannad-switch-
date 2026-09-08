from pathlib import Path
from capstone import *
from capstone.arm64 import *
import struct,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
# inspect VARSTR and all script entries for surname in multiple encodings
root=R/'05_build/script_package_fix6/SCRIPT.PAK_unpacked'
for s in ['岡崎','冈崎','おかざき','オカザキ','Okazaki','朋也','Tomoya']:
 print('\n##',s)
 for enc in ['utf-8','utf-16le','cp932']:
  try:pat=s.encode(enc)
  except:continue
  hits=[]
  for f in root.iterdir():
   if not f.is_file():continue
   b=f.read_bytes();st=0
   while True:
    o=b.find(pat,st)
    if o<0:break
    hits.append((f.name,o));st=o+1
  if hits:print(enc,[(n,hex(o)) for n,o in hits[:30]],'count',len(hits))
# rodata xrefs for full-name English prompts and Japanese prompt strings
D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
for s in ['Changing the protagonist\'s name \nfrom "Okazaki Tomoya"','Change the protagonist\'s name to the default setting “Okazaki Tomoya”','名前を「岡崎朋也」以外に変更すると','主人公の\n名前を「岡崎朋也」へ戻す必要があります。']:
 pat=s.encode('utf-8');o=rb.find(pat);print('\nSTRING',repr(s),hex(RB+o) if o>=0 else None)
 if o<0:continue
 a=RB+o;pg=a&~0xfff;lo=a&0xfff
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     print('xref',hex(x.address),hex(y.address));break
