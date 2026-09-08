from pathlib import Path
import struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');info=(R/'05_build/font_package_fix2/FONT.PAK_unpacked/info24').read_bytes();fs,bs,cn=struct.unpack_from('<HHH',info,0);off=6
if cn==100:cn=struct.unpack_from('<H',info,6)[0];off=8
off+=cn*3;ui=struct.unpack_from('<65536H',info,off)
for group in ['岡岗山','Young永','浜濱松','契绮琦琪','盐渍腌','身腰臀','野鸡雉','明太鱼鳕狭']:
 print(group,[(c,ui[ord(c)]!=0,ui[ord(c)]) for c in group])
