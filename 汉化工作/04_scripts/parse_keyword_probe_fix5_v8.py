from pathlib import Path
import struct,json
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_work\script_probe\SCRIPT.PAK_unpacked\_KEYWORD').read_bytes()
print('header',struct.unpack_from('<4H',b,0))
# inspect around first expected record end
for off in range(0x2c0,0x310,2):
 v=struct.unpack_from('<H',b,off)[0]
 ch=chr(v) if 32<=v<127 else ''
 print(f'{off:04X} {v:5d} {v:04X} {ch!r}')
# heuristic parser: header 4H, then per record maybe id/flags + 4 length-prefixed strings.
def getstr(off):
 n=struct.unpack_from('<H',b,off)[0];off+=2
 raw=b[off:off+n*2]
 s=raw.decode('utf-16le')
 z=struct.unpack_from('<H',b,off+n*2)[0]
 if z!=0: raise ValueError(('nonzero terminator',hex(off),n,z))
 return s,off+(n+1)*2
for start_extra in range(0,8):
 off=8
 ok=True; rec=[]
 try:
  for i in range(5):
   vals=[]
   for k in range(start_extra): vals.append(struct.unpack_from('<H',b,off+k*2)[0])
   off+=start_extra*2
   ss=[]
   for _ in range(4):s,off=getstr(off);ss.append(s)
   rec.append((vals,ss,off))
 except Exception as e:ok=False
 if ok:
  print('candidate extra',start_extra,'off after5',hex(off))
  for r in rec[:2]:print(r[0],[x[:60] for x in r[1]],hex(r[2]))
