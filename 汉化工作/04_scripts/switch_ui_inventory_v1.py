from pathlib import Path
import struct,csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
dirs=[R/'03_text/ui_work/SYSCG.PAK_unpacked',R/'03_text/ui_work/SYSCG2.PAK_unpacked',R/'03_text/ui_work/PARTS.PAK_unpacked',R/'03_text/switch_work/paks/MANUAL.PAK_unpacked']
out=[]
for d in dirs:
 if not d.exists():continue
 for p in sorted(d.iterdir()):
  if not p.is_file():continue
  b=p.read_bytes()
  if len(b)>=15 and b[:2]==b'CZ':
   w,h=struct.unpack_from('<HH',b,8); typ=b[:3].decode('ascii','replace')
  else:w=h=None;typ='OTHER'
  out.append((d.name,p.name,typ,w,h,p.stat().st_size))
with (R/'03_text/ui_work/switch_ui_inventory.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['pakdir','name','type','width','height','size']);w.writerows(out)
for r in out:
 if r[0] in ('SYSCG.PAK_unpacked','PARTS.PAK_unpacked'):
  print('\t'.join(map(str,r)))
