from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
for a,z,n in [(0x179fa0,0x17a650,'label_setup'),(0x17b100,0x17bda0,'title_tail'),(0x17ec30,0x17f500,'labelselect_methods')]:
 print('\n###',n,hex(a),hex(z))
 for x in md.disasm(b[a:z],a): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
