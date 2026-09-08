from pathlib import Path
from PIL import Image
import subprocess,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); SRC=R/'03_text/ui_work/OTHCG.PAK_unpacked'; WORK=R/'05_build/othcg_chs_unpacked'; PNG=R/'05_build/othcg_chs_png'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; PC=R/'05_build/pc_ui_zh_png/SR_YAKYU_01.png'
im=Image.open(PC).convert('RGBA'); assert im.size==(800,2400),im.size
pages=[im.crop((0,0,800,1200)),im.crop((0,1200,800,2400))]; rep=[]
for idx,name in enumerate(['YAKYU_01_EN','YAKYU_02_EN']):
 p=SRC/name; tmp=PNG/(name+'_canvas.png'); subprocess.run([str(EXE),'export',str(p),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with Image.open(tmp) as c:
  pg=pages[idx]; ratio=min(c.width/pg.width,c.height/pg.height); nw=max(1,round(pg.width*ratio)); nh=max(1,round(pg.height*ratio)); rs=pg.resize((nw,nh),Image.Resampling.LANCZOS); can=Image.new('RGBA',(c.width,c.height),(0,0,0,0)); can.alpha_composite(rs,((c.width-nw)//2,(c.height-nh)//2)); out=PNG/(name+'_chs.png'); can.save(out)
 subprocess.run([str(EXE),'import',str(p),str(out),str(WORK/name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); rep.append(name)
(R/'05_build/yakyu_pc_chs_report.json').write_text(json.dumps({'source':PC.name,'patched':rep},ensure_ascii=False,indent=2),encoding='utf-8'); print('PATCHED',rep)
