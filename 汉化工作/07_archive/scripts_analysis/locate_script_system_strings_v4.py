from pathlib import Path
import struct,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); P=R/'02_romfs/merged-v1.0.7/SCRIPT.PAK'; U=R/'05_build/script_package/SCRIPT.PAK_unpacked'
b=P.read_bytes(); u=lambda o:struct.unpack_from('<I',b,o)[0]; hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
while u(pos)!=marker:pos+=4
names=[];q=u(pos-4)
for i in range(fc):z=b.find(b'\0',q,hl);names.append(b[q:z].decode('utf-8'));q=z+1
rows=[]
for i,n in enumerate(names):bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((n,bo*bs,ln))
terms=['Basic','Touch','Window','Configuration','Button','Text','Sound','Voice','Language','Auto','Skip','Volume','Message','Speed','Vibration','Display','Font']
for term in terms:
 q=term.encode('utf-16le'); start=0
 while True:
  off=b.find(q,start)
  if off<0:break
  hit=next(((n,o,l) for n,o,l in rows if o<=off<o+l),None)
  print(term,off,hit)
  if hit:
   n,o,l=hit; d=(U/n).read_bytes(); rel=off-o; lo=max(0,rel-400);hi=min(len(d),rel+800); seg=d[lo:hi]
   # emit readable utf16 ascii sequences in nearby area
   seq=[]
   for m in re.finditer(rb'(?:[\x20-\x7e]\x00){2,}',seg):
    try:t=m.group().decode('utf-16le')
    except:continue
    seq.append((lo+m.start(),t))
   for rr,t in seq[:80]: print('   ',rr,repr(t))
  start=off+2

