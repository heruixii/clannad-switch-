from pathlib import Path
import struct
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\font_probe\gothic24.cz2')
b=p.read_bytes();hl,w,h=struct.unpack_from('<IHH',b,4);bits=b[12];pos=hl+256*4;fc=struct.unpack_from('<I',b,pos)[0];pos+=4;sizes=[]
for i in range(fc):cs,rs=struct.unpack_from('<II',b,pos);pos+=8;sizes.append((cs,rs))
def dec(codes):
 d={i:bytes([i&255]) for i in range(514)}
 wv=d[codes[0]];out=bytearray(wv);nextid=514
 for k in codes[1:]:
  if k in d:e=d[k]
  elif k==nextid:e=wv+wv[:1]
  else:raise ValueError((k,nextid,len(out)))
  out.extend(e)
  ne=wv+e[:1];d[nextid]=ne;d[nextid+1]=ne;nextid+=2;wv=e
 return bytes(out)
tot=0
for i,(cs,rs) in enumerate(sizes):
 codes=list(struct.unpack_from('<'+'H'*(cs//2),b,pos));pos+=cs
 x=dec(codes);print(i,'codes',len(codes),'declared_raw',rs,'decoded',len(x),'match',len(x)==rs,'maxcode',max(codes));tot+=len(x)
print('TOTAL',tot,'pixels',w*h,'match',tot==w*h)
