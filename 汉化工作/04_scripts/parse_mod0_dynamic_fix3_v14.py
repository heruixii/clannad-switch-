from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
text=(D/'text.bin').read_bytes();ro=(D/'rodata.bin').read_bytes();data=(D/'data.bin').read_bytes();print('lens',hex(len(text)),hex(len(ro)),hex(len(data)))
img=bytearray(max(0x212000+len(data),0x1A3000+len(ro),len(text)))
img[:len(text)]=text;img[0x1A3000:0x1A3000+len(ro)]=ro;img[0x212000:0x212000+len(data)]=data
dyn=struct.unpack_from('<I',text,0x0c)[0];print('dyn',hex(dyn))
for i in range(80):
 tag,val=struct.unpack_from('<QQ',img,dyn+i*16)
 print(i,hex(tag),hex(val))
 if tag==0:break
