from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();BASE=0x1A3000
for a in [0x1dde6a,0x1e371a,0x1dcdbd,0x1df180,0x1e4c99,0x1e18b4,0x1dfe91,0x1e2b34,0x1e0b1a]:
 o=a-BASE;z=rb.find(b'\0',o);print(hex(a),repr(rb[o:z].decode('utf-8',errors='replace')))
