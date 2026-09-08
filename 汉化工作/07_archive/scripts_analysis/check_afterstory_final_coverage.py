from pathlib import Path
import re
q=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\script_package_fix7\SCRIPT.PAK_unpacked')
files=sorted([f for f in q.iterdir() if f.is_file() and re.match(r'SEEN\d+',f.name)])
rows=[]
for f in files:
    n=int(re.search(r'\d+',f.name).group())
    if n>=2000:
        b=f.read_bytes()
        # rough UTF-8 CJK byte sequence count
        try:s=b.decode('utf-8','ignore')
        except:s=''
        c=sum('\u4e00'<=ch<='\u9fff' for ch in s)
        rows.append((n,f.name,c,len(b)))
print('high_scene_count',len(rows),'with_cjk',sum(c>0 for _,_,c,_ in rows))
print('samples_first',rows[:20])
print('samples_last',rows[-20:])
