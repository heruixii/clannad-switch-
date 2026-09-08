from pathlib import Path
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');tb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/text.bin').read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
# Find references to name-table offsets as immediates/displacements in all code.
targets={0x932,0x934,0x954,0x956,0x976,0x978,0x998,0x99a,0x2b98,0x2b9a,0x2bba,0x2bbc,0x2bdc,0x2bde,0x2bfe,0x2c00}
for t in sorted(targets):
 hits=[]
 for x in ins:
  if hex(t)[2:] in x.op_str.lower():
   # stricter textual immediate token
   toks=x.op_str.lower().replace('[',' ').replace(']',' ').replace(',',' ').split()
   if f'#0x{t:x}' in toks or f'0x{t:x}' in toks:
    hits.append((x.address,x.mnemonic,x.op_str))
 if hits:
  print('\n##',hex(t),'count',len(hits))
  for h in hits[:80]:print(hex(h[0]),h[1],h[2])
