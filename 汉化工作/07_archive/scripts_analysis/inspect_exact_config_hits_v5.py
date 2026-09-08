from pathlib import Path
import struct,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); P=R/'02_romfs/merged-v1.0.7/SCRIPT.PAK'; b=P.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0]
hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);pos=32;marker=hl//bs
while u(pos)!=marker:pos+=4
q=u(pos-4);names=[]
for i in range(fc):z=b.find(b'\0',q,hl);names.append(b[q:z].decode());q=z+1
rows=[]
for i,n in enumerate(names):bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((n,bo*bs,ln))
terms=['Basic','Touch','Window','Configuration','Button','Text','Sound','Voice','Language','Auto','Skip','Volume','Message','Speed','Vibration','Display','Font']
pat=re.compile(rb'(?:[\x20-\x7e]\x00){2,}')
for term in terms:
 q=term.encode('utf-16le');start=0
 while True:
  off=b.find(q,start)
  if off<0:break
  n,o,l=next((x for x in rows if x[1]<=off<x[1]+x[2])); d=b[o:o+l]; rel=off-o
  print('\nTERM',term,'entry',n,'rel',rel,'abs',off)
  lo=max(0,rel-800);hi=min(len(d),rel+1200)
  for m in pat.finditer(d[lo:hi]):
   t=m.group().decode('utf-16le','ignore')
   rr=lo+m.start()
   if abs(rr-rel)<1000: print(rr,repr(t))
  start=off+len(q)
