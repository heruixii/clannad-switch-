import json
from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\fix3_exefs\config_chs_v1_report.json')
d=json.loads(p.read_text(encoding='utf-8'))
print(d.keys())
for k,v in d.items():
 if k!='placements': print(k, v if not isinstance(v,(dict,list)) else (list(v)[:20] if isinstance(v,dict) else v[:5]))
# summarize moved placement blocks sorted
m=[(s,int(v['new'],16),len(v.get('zh','').encode('utf-8')) if 'zh' in v else None,v) for s,v in d['placements'].items() if v.get('moved')]
for x in sorted(m,key=lambda x:x[1])[-20:]: print(x[0],hex(x[1]),x[2],x[3])
