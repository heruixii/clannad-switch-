from pathlib import Path
import csv
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\pc_control_parallel_v4\review_signature_forced.tsv')
with p.open('r',encoding='utf-8-sig',newline='') as f:r=[x for x in csv.DictReader(f,delimiter='\t') if x['accepted']=='0']
r.sort(key=lambda z:(z['scene'],int(z['jp_event_index'])))
out=p.parent/'review_signature_rejected_compact.txt'
with out.open('w',encoding='utf-8') as f:
 for i,x in enumerate(r):f.write(f"{i:03d}\t{x['scene']}\tJ{x['jp_event_index']}\tZ{x['zh_event_index']}\t{x['block_similarity']}\t{x['jp_text']} ||| {x['zh_text']}\n")
print(out);print('rows',len(r))
