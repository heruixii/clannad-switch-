import json
from pathlib import Path
rows=json.loads(Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\keyword_fix5\keyword_en.json').read_text(encoding='utf-8'))
for r in rows[:30]:
 body=r['body1'];desc=body.split('$d',1)[1] if '$d' in body else body
 print(f"{r['index']:02d}\t{r['title']}\t{desc}")
