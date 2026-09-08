from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');t=(D/'text.bin').read_bytes();r=(D/'rodata.bin').read_bytes();d=(D/'data.bin').read_bytes();img=bytearray(0x212000+len(d));img[:len(t)]=t;img[0x1A3000:0x1A3000+len(r)]=r;img[0x212000:0x212000+len(d)]=d
mod0=8;dyn=mod0+struct.unpack_from('<I',t,0x0c)[0];print('dyn',hex(dyn));tags={}
for i in range(80):
 tag,val=struct.unpack_from('<QQ',img,dyn+i*16);print(i,hex(tag),hex(val));tags.setdefault(tag,[]).append(val)
 if tag==0:break
print('tags', {hex(k):[hex(x) for x in v] for k,v in tags.items()})
