from pathlib import Path
import json,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
root=R/'05_build/script_package_fix6/SCRIPT.PAK_unpacked'
terms=[b'Tomoya',b'Okazaki']
for term in terms:
 print('\n##',term.decode())
 total=0
 for f in sorted(root.iterdir()):
  if not f.is_file():continue
  b=f.read_bytes();st=0
  while True:
   o=b.find(term,st)
   if o<0:break
   total+=1
   print(f.name,hex(o),b[max(0,o-80):o+100])
   st=o+1
 print('TOTAL',total)
# JSON/source references
for d in [R/'03_text/switch_work', R/'03_text/switch_json', R/'03_text/switch_decoded']:
 if not d.exists():continue
 print('\nDIR',d)
 for p in d.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in ('.json','.txt','.tsv'):continue
  try:s=p.read_text(encoding='utf-8',errors='ignore')
  except:continue
  if 'Tomoya' in s or 'Okazaki' in s:
   print(p)
   for m in re.finditer('Tomoya|Okazaki',s):print(s[max(0,m.start()-240):m.start()+360].replace('\n',' ')[:700])
