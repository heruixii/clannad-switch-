from pathlib import Path
import struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
items=[('SYSCG',R/'03_text/ui_work/SYSCG.PAK',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked',R/'05_build/ui_packages_v1/SYSCG.PAK.out'),('PARTS',R/'03_text/ui_work/PARTS.PAK',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked',R/'05_build/ui_packages_v1/PARTS.PAK.out')]

def repack(label,orig,work,out):
 b=orig.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 if pos+8*fc>hl:raise RuntimeError(label+' bad offset table')
 names=[]
 if flags&512:
  q=u(pos-4)
  for i in range(fc):
   z=b.find(b'\0',q,hl)
   if z<0:raise RuntimeError(label+' bad name')
   names.append(b[q:z].decode('utf-8'));q=z+1
 else:names=[str(i) for i in range(fc)]
 head=bytearray(b[:hl]);data=bytearray(head);off=hl;missing=[]
 for i,n in enumerate(names):
  f=work/n
  if not f.exists():missing.append(n);continue
  if off%bs:off=((off+bs-1)//bs)*bs
  if len(data)<off:data.extend(b'\0'*(off-len(data)))
  d=f.read_bytes();struct.pack_into('<II',head,pos+i*8,off//bs,len(d));data.extend(d);off+=len(d)
 if missing:raise RuntimeError(label+' missing '+repr(missing[:10]))
 if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
 data[:hl]=head;out.write_bytes(data);rb=out.read_bytes();bad=[]
 for i,n in enumerate(names):
  bo,ln=struct.unpack_from('<II',rb,pos+i*8);got=rb[bo*bs:bo*bs+ln];exp=(work/n).read_bytes()
  if got!=exp:bad.append(n)
 sha=hashlib.sha256(rb).hexdigest().upper();print(label,'entries',fc,'size',len(rb),'bad',len(bad),'sha',sha)
 if bad:raise RuntimeError(label+' verify bad')
 return {'entries':fc,'size':len(rb),'sha256':sha,'bad':bad}
rep={label:repack(label,o,w,out) for label,o,w,out in items}
(R/'05_build/ui_final_repack_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
