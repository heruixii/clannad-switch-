from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');rb=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();RB=0x1A3000
addrs=[0x1e1cf3,0x1dc084,0x1de857,0x1e693e,0x1e09fd,0x1dcc54,0x1dc671,0x1db64c,0x1e4b8b,0x1de974,0x1e63ca,0x1e4276,0x1de3cb,0x1dc7ce,0x1e3bb7,0x1df12a,0x1dd1a2,0x1e237b,0x1de99c,0x1e5712]
for a in addrs:
 o=a-RB
 if not 0<=o<len(rb):print(hex(a),'OUT');continue
 z=rb.find(b'\0',o,min(len(rb),o+300));raw=rb[o:z]
 try:s=raw.decode('utf-8')
 except:s=raw.decode('utf-8','replace')
 print(hex(a),repr(s))
