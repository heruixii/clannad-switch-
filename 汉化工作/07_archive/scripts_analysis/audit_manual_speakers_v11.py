from pathlib import Path
import csv,re,collections
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\translated\manual_batches_v11')
pairs=collections.Counter()
for n in range(1,25):
 with (D/f'source_{n:02d}.tsv').open('r',encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):
   if r['speaker_jp']:pairs[(r['speaker_jp'],r['speaker_zh'])]+=1
print('speaker_pairs',len(pairs))
for (j,z),n in pairs.most_common():
 if re.search(r'[ぁ-んァ-ヶ]',z): print('KANA',n,repr(j),'->',repr(z))
