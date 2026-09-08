from pathlib import Path
import re,csv,subprocess,shutil
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'03_text/ui_work/OTHCG.PAK_unpacked'; OUT=R/'05_build/othcg_reps_png'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; OUT.mkdir(parents=True,exist_ok=True)
if OUT.exists():
    for p in OUT.glob('*'): p.unlink()
fs=[p for p in D.iterdir() if p.is_file() and '_EN' in p.name.upper()]
groups={}
for p in fs:
    root=re.sub(r'_EN(?:_\d+)?$','_EN',p.name,flags=re.I)
    groups.setdefault(root,[]).append(p)
rows=[]
for i,(root,items) in enumerate(sorted(groups.items()),1):
    rep=max(items,key=lambda p:p.stat().st_size)
    png=OUT/(root+'.png')
    subprocess.run([str(EXE),'export',str(rep),str(png)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    rows.append([root,rep.name,len(items),rep.stat().st_size,png.name])
    if i%20==0:print('EXPORTED',i,'/',len(groups),flush=True)
with (R/'03_text/ui_work/othcg_groups_v1.tsv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,delimiter='\t');w.writerow(['group','representative','frame_count','rep_size','png']);w.writerows(rows)
print('GROUPS',len(groups),'ANIM',sum(1 for v in groups.values() if len(v)>1),'STATIC',sum(1 for v in groups.values() if len(v)==1),'PNGS',len(list(OUT.glob('*.png'))))
