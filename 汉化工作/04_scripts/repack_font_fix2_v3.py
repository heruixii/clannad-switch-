from pathlib import Path
import struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); ORIG=R/'03_text/switch_work/paks/FONT.PAK'; WORK=R/'05_build/font_package_fix2/FONT.PAK_unpacked'; OUT=R/'05_build/font_package_fix2/FONT.PAK.out'
b=ORIG.read_bytes(); u=lambda o:struct.unpack_from('<I',b,o)[0]
hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0); flags=rest[-1]; pos=32; marker=hl//bs
while pos+4<=hl and u(pos)!=marker: pos+=4
if pos+8*fc>hl: raise SystemExit('bad offset table')
names=[]
if flags&512:
 q=u(pos-4)
 for i in range(fc):
  z=b.find(b'\0',q,hl)
  if z<0: raise SystemExit(f'bad name {i}')
  names.append(b[q:z].decode('utf-8')); q=z+1
else:names=[str(i) for i in range(fc)]
head=bytearray(b[:hl]); data=bytearray(head); off=hl
for i,name in enumerate(names):
 if off%bs: off=((off+bs-1)//bs)*bs
 if len(data)<off:data.extend(b'\0'*(off-len(data)))
 d=(WORK/name).read_bytes(); struct.pack_into('<II',head,pos+i*8,off//bs,len(d)); data.extend(d); off+=len(d)
if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
data[:hl]=head; OUT.write_bytes(data)
rb=OUT.read_bytes(); bad=[]
for i,name in enumerate(names):
 bo,ln=struct.unpack_from('<II',rb,pos+i*8); got=rb[bo*bs:bo*bs+ln]; exp=(WORK/name).read_bytes()
 if got!=exp:bad.append(name)
rep={'entries':fc,'block':bs,'size':len(rb),'bad':bad,'sha256':hashlib.sha256(rb).hexdigest().upper()}; (R/'05_build/font_package_fix2/font_repack_verify.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8'); print(rep); raise SystemExit(1 if bad else 0)

