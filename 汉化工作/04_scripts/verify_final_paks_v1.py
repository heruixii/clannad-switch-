from pathlib import Path
import struct,json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
items=[
 ('SCRIPT',R/'05_build/script_package/SCRIPT.PAK.out',R/'05_build/script_package/SCRIPT.PAK_unpacked'),
 ('FONT',R/'05_build/font_package/FONT.PAK.out',R/'05_build/font_package/FONT.PAK_unpacked'),
 ('SYSCG',R/'05_build/ui_packages_v1/SYSCG.PAK.out',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'),
 ('PARTS',R/'05_build/ui_packages_v1/PARTS.PAK.out',R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'),
 ('MANUAL',R/'05_build/ui_packages_v1/MANUAL.PAK.out',R/'05_build/ui_packages_v1/MANUAL.PAK_unpacked'),
 ('OTHCG',R/'05_build/OTHCG.PAK.out',R/'05_build/othcg_chs_unpacked'),
]
def parse(p):
 b=p.read_bytes(); u=lambda o:struct.unpack_from('<I',b,o)[0]
 hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0); flags=rest[-1]; pos=32; marker=hl//bs
 while pos+4<=hl and u(pos)!=marker: pos+=4
 if pos+8*fc>hl: raise ValueError('offset table')
 named=bool(flags&512); names=[]
 if named:
  q=u(pos-4)
  for i in range(fc):
   z=b.find(b'\0',q,hl); names.append(b[q:z].decode('utf-8')); q=z+1
 else:names=[str(i) for i in range(fc)]
 rows=[]
 for i,n in enumerate(names):
  bo,ln=struct.unpack_from('<II',b,pos+i*8); off=bo*bs
  rows.append((n,off,ln))
 return b,hl,fc,bs,rows
report={}; total_bad=0
for label,p,d in items:
 b,hl,fc,bs,rows=parse(p); bad=[]; missing=[]; overlap=[]; prev=hl
 for n,off,ln in rows:
  if off%bs: bad.append([n,'unaligned',off])
  if off<prev: overlap.append([n,off,prev])
  prev=max(prev,off+ln)
  q=d/n
  if not q.exists(): missing.append(n); continue
  if b[off:off+ln]!=q.read_bytes(): bad.append([n,'content'])
 total_bad+=len(bad)+len(missing)+len(overlap)
 report[label]={'entries':fc,'block':bs,'size':len(b),'bad':bad,'missing':missing,'overlap':overlap,'sha256':hashlib.sha256(b).hexdigest().upper()}
 print(label,'entries',fc,'size',len(b),'bad',len(bad),'missing',len(missing),'overlap',len(overlap))
(R/'05_build/final_pak_verify.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL_BAD',total_bad)
raise SystemExit(1 if total_bad else 0)
