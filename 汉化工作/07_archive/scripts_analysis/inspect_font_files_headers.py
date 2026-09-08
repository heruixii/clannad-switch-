from pathlib import Path
import struct
F=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_work\paks\FONT.PAK_unpacked')
for p in sorted(F.iterdir()):
 if p.name.startswith('info'):continue
 b=p.read_bytes()[:32]
 sig=b[:4]
 if sig[:3] in (b'CZ0',b'CZ1',b'CZ2',b'CZ3',b'CZ4'):
  try:
   hl,w,h=struct.unpack_from('<IHH',b,4);bits=b[12]
   print(p.name,'sig',sig,'header',hl,'w',w,'h',h,'bits',bits,'len',p.stat().st_size)
  except Exception as e: print(p.name,e)
 else: print(p.name,'sig',sig.hex(),'len',p.stat().st_size)
