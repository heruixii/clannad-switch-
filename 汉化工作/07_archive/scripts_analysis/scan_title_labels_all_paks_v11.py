from pathlib import Path
import struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'02_romfs/merged-v1.0.7'
terms=['NEW GAME','AFTER STORY','CG MODE','MUSIC MODE','CONFIG','DANGOPEDIA','MANUAL','LOAD','NAME']
def parse_pak(p):
 b=p.read_bytes();
 if len(b)<36:return b,[]
 try:hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1]
 except:return b,[]
 if hl<=0 or hl>len(b) or bs<=0:return b,[]
 u=lambda o:struct.unpack_from('<I',b,o)[0]
 pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 if pos+8*fc>hl:return b,[]
 names=[]
 if flags&512:
  q=u(pos-4)
  for i in range(fc):
   z=b.find(b'\0',q,hl)
   if z<0:return b,[]
   names.append(b[q:z].decode('utf-8','replace'));q=z+1
 else:names=[str(i) for i in range(fc)]
 rows=[]
 for i,n in enumerate(names):
  bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((n,bo*bs,ln))
 return b,rows
for pak in sorted(D.glob('*.PAK')):
 b,rows=parse_pak(pak);hits=[]
 for term in terms:
  for enc in ['ascii','utf-16le','utf-8']:
   q=term.encode(enc);st=0
   while True:
    off=b.find(q,st)
    if off<0:break
    ent=next(((n,o,l) for n,o,l in rows if o<=off<o+l),None)
    hits.append((off,term,enc,ent));st=off+max(1,len(q))
 if hits:
  print('\n###',pak.name,'hits',len(hits))
  for h in hits[:300]:print(h)
