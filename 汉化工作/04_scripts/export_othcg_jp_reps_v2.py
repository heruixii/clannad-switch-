from pathlib import Path
import csv,re,subprocess,shutil
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); D=R/'03_text/ui_work/OTHCG.PAK_unpacked'; OUT=R/'05_build/othcg_jp_reps_png'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
OUT.mkdir(parents=True,exist_ok=True)
for q in OUT.glob('*'):q.unlink()
rows=list(csv.DictReader((R/'03_text/ui_work/othcg_groups_v1.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
ok=miss=0
for r in rows:
 en=r['representative']; jp=en.replace('_EN','',1); src=D/jp
 if not src.exists():
  # fallback exact group base without EN, choose largest matching frame
  base=r['group'].replace('_EN',''); cand=[x for x in D.iterdir() if x.is_file() and (x.name==base or re.sub(r'_\d+$','',x.name)==base)]
  if cand: src=max(cand,key=lambda x:x.stat().st_size)
 if src.exists():
  out=OUT/(r['group']+'.png'); z=subprocess.run([str(EXE),'export',str(src),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if z.returncode==0 and out.exists():ok+=1
  else:miss+=1
 else:miss+=1
print('JP_REPS',ok,'MISS',miss)
