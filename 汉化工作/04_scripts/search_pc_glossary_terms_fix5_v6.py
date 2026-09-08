from pathlib import Path
root=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\pc_zh')
terms=['芥川','便当','紅豆','红豆','豆沙','面包','麵包']
exts={'.tsv','.txt','.json','.csv','.md'}
h=0
for p in root.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in exts: continue
    b=p.read_bytes()
    s=None
    for enc in ['utf-8-sig','gb18030','utf-16le']:
        try:
            s=b.decode(enc);break
        except: pass
    if s is None: continue
    for i,line in enumerate(s.splitlines(),1):
        if any(t in line for t in terms):
            print(p.relative_to(root),i,line[:500]);h+=1
            if h>=300:raise SystemExit
print('HITS',h)
