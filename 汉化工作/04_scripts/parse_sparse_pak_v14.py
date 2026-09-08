from pathlib import Path
import struct
for name in ['PARTS2.PAK','SYSCG2.PAK']:
 p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\ui_work')/name;b=p.read_bytes();hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);table_end=struct.unpack_from('<I',b,36)[0];pos=40
 print('\n###',name,'hl',hl,'fc',fc,'idstart',idstart,'bs',bs,'table_end',hex(table_end),'expected',hex(pos+fc*8))
 nz=[]
 for i in range(fc):
  off,ln=struct.unpack_from('<II',b,pos+i*8)
  if off or ln:nz.append((i,idstart+i,off*bs,ln))
 print('nonzero',len(nz))
 for r in nz:print(r)
