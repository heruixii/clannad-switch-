from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
ranges=[(0x179260,0x179fa0,'title_onstart'),(0x179fa0,0x17a900,'title_core'),(0x17a900,0x17b100,'title_more')]
out=[]
for a,z,n in ranges:
 print('\n###',n,hex(a),hex(z)); lines=[]
 for x in md.disasm(b[a:z],a):
  line=f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}'; print(line);lines.append(line)
 out.append((n,lines))
