from pathlib import Path
import csv
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\switch_pc_v10\safe_matches.tsv')
with p.open('r',encoding='utf-8-sig',newline='') as f:
 r=csv.DictReader(f,delimiter='\t')
 n=0
 for x in r:
  if x['sw_jp_text'].startswith('`') and x['pc_zh_text']:
   print(x['scene'],x['sw_code_index'],'SW',repr(x['sw_jp_text']),'ZH',repr(x['pc_zh_text']))
   n+=1
   if n>=30:break
