from pathlib import Path
import json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\keyword_fix5\keyword_zh_full.json')
rows=json.loads(p.read_text(encoding='utf-8'))
for r in rows:
 t=r['title']
 if len(t)>4:
  print(f"{r['index']:02d}\t{len(t)}\t{t}")
print('GT4',sum(len(r['title'])>4 for r in rows),'GT6',sum(len(r['title'])>6 for r in rows),'MAX',max(len(r['title']) for r in rows))
