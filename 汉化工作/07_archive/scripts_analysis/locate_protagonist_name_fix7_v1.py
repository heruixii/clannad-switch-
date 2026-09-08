from pathlib import Path
import re,struct,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
terms=[b'Tomoya',b'Okazaki',b'TOMOYA',b'OKAZAKI', '朋也'.encode('utf-8'), '冈崎'.encode('utf-8'), '岡崎'.encode('utf-8')]
# ExeFS rodata/data utf8 search
D=R/'05_build/exefs_fix2/update_exefs/main_decompressed'
for fn,base in [('text.bin',0),('rodata.bin',0x1A3000),('data.bin',0x212000)]:
 b=(D/fn).read_bytes(); print('\n##',fn)
 for t in terms:
  st=0
  while True:
   o=b.find(t,st)
   if o<0: break
   print(t,hex(base+o),b[max(0,o-48):o+96])
   st=o+1
# script entries search utf8/utf16le
roots=[R/'05_build/script_package_fix6/SCRIPT.PAK_unpacked',R/'05_build/ui_packages_fix5/PARTS.PAK_unpacked',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked']
for root in roots:
 print('\nROOT',root)
 hits=0
 for f in root.iterdir():
  if not f.is_file(): continue
  b=f.read_bytes()
  for s in ['Tomoya','Okazaki','TOMOYA','OKAZAKI','朋也','冈崎','岡崎']:
   for enc in ['utf-8','utf-16le','cp932']:
    try: pat=s.encode(enc)
    except: continue
    o=b.find(pat)
    if o>=0:
     print(f.name,s,enc,hex(o),b[max(0,o-48):o+128]); hits+=1; break
 print('hits',hits)
