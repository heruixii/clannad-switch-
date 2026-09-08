from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,subprocess,shutil,numpy as np,cv2,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
SCAN=R/'05_build/ui_fullscan_english.tsv'
SY=R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'
PA=R/'05_build/ui_packages_v1/PARTS.PAK_unpacked'
PNG=R/'05_build/start_settings_fix_png'; PNG.mkdir(parents=True,exist_ok=True)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
rows=list(csv.DictReader(SCAN.open(encoding='utf-8-sig'),delimiter='\t'))

def fit(text,w,h):
    s=max(14,int(h*.80))
    while s>11:
        f=ImageFont.truetype(str(FONT),s)
        bb=f.getbbox(text)
        if bb[2]-bb[0] <= w*.95 and bb[3]-bb[1] <= h*.86:return f
        s-=1
    return ImageFont.truetype(str(FONT),11)

def clear_draw(im, box, text):
    x1,y1,x2,y2=[int(round(float(v))) for v in box]
    pad=max(3,int((y2-y1)*.12)); x1=max(0,x1-pad);y1=max(0,y1-pad);x2=min(im.width,x2+pad);y2=min(im.height,y2+pad)
    arr=np.array(im.convert('RGBA')); reg=arr[y1:y2,x1:x2]
    trans=float((reg[:,:,3]<48).mean()) if reg.size else 1.0
    if trans>.20:
        arr[y1:y2,x1:x2,3]=0
        # zero RGB under transparent area so old antialiasing cannot survive
        arr[y1:y2,x1:x2,:3]=0
    else:
        rgb=arr[:,:,:3].copy(); mask=np.zeros((im.height,im.width),np.uint8);mask[y1:y2,x1:x2]=255
        arr[:,:,:3]=cv2.inpaint(rgb,mask,4,cv2.INPAINT_TELEA)
    im=Image.fromarray(arr,'RGBA'); d=ImageDraw.Draw(im)
    if text:
        f=fit(text,x2-x1,y2-y1); bb=d.textbbox((0,0),text,font=f,stroke_width=1)
        tx=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0]; ty=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
        # Choose foreground by local luminance after cleanup.
        a=np.array(im)[y1:y2,x1:x2,:3]; lum=float(a.mean()) if a.size else 80
        fill=(24,24,24,255) if lum>145 else (255,255,255,255); stroke=(255,255,255,220) if lum>145 else (0,0,0,220)
        d.text((tx,ty),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke)
    return im

def patch_asset(root,name,repls):
    src=root/name; tmp=PNG/(name+'_src.png'); out=PNG/(name+'_chs.png')
    subprocess.run([str(EXE),'export',str(src),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    im=Image.open(tmp).convert('RGBA'); hit=0
    for r in [x for x in rows if x['asset']==name]:
        key=r['text'].strip()
        if key not in repls:continue
        im=clear_draw(im,(r['x1'],r['y1'],r['x2'],r['y2']),repls[key]);hit+=1
    im.save(out)
    subprocess.run([str(EXE),'import',str(src),str(out),str(src)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return hit

report=[]
# Start/title screen. Copyright stays untouched.
report.append(('TITLE',patch_asset(SY,'TITLE',{
 'NEW GAME':'新游戏','LOAD':'读取','AFTER STORY':'后日谈','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏',
 'CONFIG':'设置','NAME':'姓名','DANGOPEDIA':'团子百科','MANUAL':'使用说明'})))
# Plain-language branches that were never handled by the old *_EN-only pipeline.
report.append(('MN_EX_BG01',patch_asset(SY,'MN_EX_BG01',{'CG MODE':'CG鉴赏'})))
report.append(('MN_EX_BG03',patch_asset(SY,'MN_EX_BG03',{'MUSIC MODE':'音乐鉴赏'})))
report.append(('NAME',patch_asset(SY,'NAME',{'Language':'语言'})))
report.append(('CL_DP_TITLE',patch_asset(PA,'CL_DP_TITLE',{'DANGOPEDIA':'团子百科'})))
report.append(('PS_BUTTON_CHIP',patch_asset(PA,'PS_BUTTON_CHIP',{'START':'开始'})))
# Settings/system-menu insurance: the Chinese-patched EN branch is known-good. Mirror it to the base branch so either language path renders Chinese.
for base,en in [('CONFIG_BG','CONFIG_BG_EN'),('CONFIG_TAB','CONFIG_TAB_EN'),('SYSTEM_ICON','SYSTEM_ICON_EN')]:
    shutil.copy2(PA/en,PA/base); report.append((base,'copied_from_'+en))
# Also mirror already-translated extra page backgrounds to the base branch.
for base,en in [('MN_EX_BG01','MN_EX_BG01_EN'),('MN_EX_BG03','MN_EX_BG03_EN')]:
    if (SY/en).exists(): shutil.copy2(SY/en,SY/base); report.append((base,'copied_from_'+en))
(R/'05_build/start_settings_fix_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('REPORT')
for x in report:print(x)
