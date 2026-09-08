from pathlib import Path
import csv
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
rows=list(csv.DictReader((R/'05_build/ui_fullscan_english.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
print(rows[0].keys())
for a in ['SKIP_ICON_00','SKIP_ICON_01','PS_BUTTON_CHIP']:
 print('\n##',a)
 for r in rows:
  if r['pak']=='PARTS' and r['asset']==a:
   print({k:r.get(k) for k in r.keys()})
