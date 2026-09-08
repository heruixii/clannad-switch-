from pathlib import Path
import struct,sys

def parse(path):
 p=Path(path); b=p.read_bytes(); u=lambda o:struct.unpack_from('<I',b,o)[0]
 hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0); flags=rest[-1]
 pos=32; marker=hl//bs
 while pos+4<=hl and u(pos)!=marker: pos+=4
 if pos+8*fc>hl: raise ValueError((hl,fc,bs,pos,marker))
 named=bool(flags&512); names=[]
 if named:
  no=u(pos-4); q=no
  for i in range(fc):
   z=b.find(b'\0',q,hl)
   if z<0: raise ValueError(('name',i,q))
   names.append(b[q:z].decode('utf-8')); q=z+1
 else:names=[str(i) for i in range(fc)]
 rows=[]
 for i in range(fc):
  off,len_=struct.unpack_from('<II',b,pos+i*8); rows.append((i,idstart+i,names[i],off*bs,len_))
 print('header',hl,'count',fc,'idstart',idstart,'block',bs,'flags',hex(flags),'offsetpos',pos,'named',named,'nameoff',u(pos-4) if named else None)
 return b,rows
if __name__=='__main__':
 b,rows=parse(sys.argv[1]);
 for r in rows[:20]:print(*r,sep='\t')
 print('last');
 for r in rows[-10:]:print(*r,sep='\t')
