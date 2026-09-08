from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed'); b=(D/'rodata.bin').read_bytes();B=0x1A3000
for a in [0x1e1301,0x1e75c0,0x1dfed7,0x1e6538,0x1dd81c,0x1db810,0x1e5ded,0x1e2475,0x1e5df9]:
 o=a-B;e=b.find(b'\0',o);raw=b[o:e]
 print(hex(a),raw,raw.decode('utf-8','replace'))
