from pathlib import Path
import ast,re
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_config_chs_ips_fix3_v29.py')
mod=ast.parse(p.read_text(encoding='utf-8-sig'))
T=None
for n in mod.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='T' for t in n.targets):
        T=ast.literal_eval(n.value);break
assert T
bad=[]
for en,zh in T.items():
    ec=len(en.encode('utf-8'))+1;zc=len(zh.encode('utf-8'))+1
    if zc>ec: bad.append((zc-ec,ec,zc,en,zh))
print('OVERFLOW_COUNT',len(bad))
for d,ec,zc,en,zh in sorted(bad,reverse=True): print(f'diff={d:3d} cap={ec:3d} need={zc:3d} EN={en!r} -> ZH={zh!r}')

