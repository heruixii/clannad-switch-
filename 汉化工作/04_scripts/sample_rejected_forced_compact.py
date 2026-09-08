from pathlib import Path
import csv,random
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\pc_control_parallel_v4\review_signature_forced.tsv')
with p.open('r',encoding='utf-8-sig',newline='') as f:r=[x for x in csv.DictReader(f,delimiter='\t') if x['accepted']=='0']
random.seed(31)
for x in sorted(random.sample(r,min(80,len(r))),key=lambda z:(z['scene'],int(z['jp_event_index']))):
 print(f"{x['scene']} J{x['jp_event_index']} Z{x['zh_event_index']} sim={x['block_similarity']} {x['jp_text']} ||| {x['zh_text']}")
