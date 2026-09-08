from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();BASE=0x1A3000
addrs=[0x1e542d,0x1e488a,0x1de5a5,0x1dc8af,0x1dc9a9,0x1e6c94,0x1e1507,0x1de0b8,0x1e1af3,0x1dbcb4,0x1e0046,0x1dc9b9]
for a in addrs:
 o=a-BASE
 if 0<=o<len(rb):
  z=rb.find(b'\0',o);print(hex(a),repr(rb[o:z].decode('utf-8',errors='replace')))
