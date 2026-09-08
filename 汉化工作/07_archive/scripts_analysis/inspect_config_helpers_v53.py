from pathlib import Path
from capstone import *
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.skipdata=True
for a,z,n in [(0xfda80,0xfdd50,'fdb80'),(0xfe180,0xfe450,'fe290'),(0xffdd0,0x100080,'ffec0'),(0x65800,0x65a20,'65890'),(0x72a00,0x72b20,'72a')]:
 print('\n###',n,hex(a),hex(z))
 for x in md.disasm(b[a:z],a): print(f'{x.address:08X}: {x.mnemonic:<8} {x.op_str}')
