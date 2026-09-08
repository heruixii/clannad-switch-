from pathlib import Path
import struct
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
rb=(D/'rodata.bin').read_bytes(); db=(D/'data.bin').read_bytes(); tb=(D/'text.bin').read_bytes(); RB=0x1A3000; DB=0x212000
terms=['Master Volume','Text Speed','Cursor Control','Soft Filter','Color Adjustment','Blue Level','Green Level','Red Level','Font','Sound source','System sounds','Rumble feature','Quick Load','Voice output','Sample Voice','Defaults']
for t in terms:
 o=rb.find(t.encode())
 if o<0: continue
 a=RB+o; pat=struct.pack('<Q',a)
 print('\n###',t,'addr',hex(a))
 for name,b,base in [('rodata',rb,RB),('data',db,DB),('text',tb,0)]:
  pos=[]; st=0
  while True:
   x=b.find(pat,st)
   if x<0: break
   pos.append(base+x); st=x+1
  if pos: print(name,'qptr',','.join(hex(x) for x in pos[:40]))
