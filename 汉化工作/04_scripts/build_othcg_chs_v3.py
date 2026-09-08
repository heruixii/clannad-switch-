from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,re,shutil,subprocess,struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=R/'03_text/ui_work/OTHCG.PAK_unpacked'; WORK=R/'05_build/othcg_chs_unpacked'; PNG=R/'05_build/othcg_chs_png'; EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'; PC=R/'05_build/pc_ui_zh_png'; ORIGPAK=R/'03_text/ui_work/OTHCG.PAK'; OUTPAK=R/'05_build/OTHCG.PAK.out'
for d in [WORK,PNG]:
    if d.exists(): shutil.rmtree(d)
    d.mkdir(parents=True)
shutil.copytree(SRC,WORK,dirs_exist_ok=True)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())

def fit(text,w,h):
    s=max(12,int(h*.72))
    while s>10:
        f=ImageFont.truetype(str(FONT),s)
        b=f.getbbox(text)
        if b[2]-b[0]<=w*.92 and b[3]-b[1]<=h*.88:return f
        s-=1
    return ImageFont.truetype(str(FONT),10)

def redraw_text(srcpng,outpng,text):
    im=Image.open(srcpng).convert('RGBA')
    # preserve background; cover central text band with transparent/nearby fill conservatively
    arr=im.copy(); d=ImageDraw.Draw(arr)
    bbox=arr.getbbox() or (0,0,arr.width,arr.height)
    # estimate background from corners
    pix=arr.load(); pts=[pix[0,0],pix[arr.width-1,0],pix[0,arr.height-1],pix[arr.width-1,arr.height-1]]
    bg=tuple(sum(x[i] for x in pts)//4 for i in range(4))
    d.rectangle((0,0,arr.width,arr.height),fill=bg)
    f=fit(text,arr.width,arr.height)
    bb=d.textbbox((0,0),text,font=f,stroke_width=1)
    x=(arr.width-(bb[2]-bb[0]))//2; y=(arr.height-(bb[3]-bb[1]))//2-bb[1]
    lum=sum(bg[:3])/3; fill=(20,20,20,255) if lum>145 else (255,255,255,255); stroke=(255,255,255,255) if lum>145 else (0,0,0,255)
    d.text((x,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke)
    arr.save(outpng)

groups=list(csv.DictReader((R/'03_text/ui_work/othcg_groups_v1.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
static_pc={}
for g in groups:
    base=g['group'][:-3] if g['group'].upper().endswith('_EN') else g['group']
    q=PC/(base+'.png')
    if q.exists() and int(g['frame_count'])==1: static_pc[g['group']]=q
# exact static groups only
use_static={k:v for k,v in static_pc.items() if k.startswith('KTC') or k.startswith('SPDATA') or k.startswith('SZZD')}
manual_text={
 'SPDATA00BTN_EN':('是','否'),
 'SFUSM00_00_EN':'已掌握“让风子用鼻子喝果汁”技能！',
 'SFUSM00_01_EN':'已掌握“随机把风子放到某处”技能！',
 'SFUSM00_02_EN':'已掌握“切换风子说话对象”技能！',
 'SFUSM00_03_EN':'已掌握“切换风子手中雕刻物”技能！',
 'SFUSM00_04_EN':'你成为了“风子使”！',
 'SFUSM00_05_EN':'已掌握“捏住风子的鼻子”技能！',
 'SFUSM00_06_EN':'你的职业变成了“风子大师”！',
}
report={'pc_static':[],'manual_text':[],'jp_fallback':[],'missing_jp':[],'errors':[]}
# first fallback every EN file to corresponding JP raw file
for p in sorted(SRC.iterdir()):
    if not p.is_file() or '_EN' not in p.name.upper(): continue
    jp=SRC/p.name.replace('_EN','',1)
    if jp.exists():
        shutil.copy2(jp,WORK/p.name); report['jp_fallback'].append(p.name)
    else: report['missing_jp'].append(p.name)
# then overwrite static exact matches via PNG import
for g,pcpng in use_static.items():
    rep=next(x for x in groups if x['group']==g)['representative']
    orig=SRC/rep; outpng=PNG/(g+'.png')
    # export current EN representative only to get canvas size
    tmp=PNG/(g+'_canvas.png')
    subprocess.run([str(EXE),'export',str(orig),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    with Image.open(tmp) as cim, Image.open(pcpng).convert('RGBA') as pim:
        target=(cim.width,cim.height)
        # scale content to fit target while preserving aspect ratio, center on transparent canvas
        ratio=min(target[0]/pim.width,target[1]/pim.height)
        nw=max(1,int(round(pim.width*ratio))); nh=max(1,int(round(pim.height*ratio)))
        rs=pim.resize((nw,nh),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',target,(0,0,0,0)); canvas.alpha_composite(rs,((target[0]-nw)//2,(target[1]-nh)//2)); canvas.save(outpng)
    subprocess.run([str(EXE),'import',str(orig),str(outpng),str(WORK/rep)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    report['pc_static'].append({'group':g,'rep':rep,'pc':pcpng.name})
# manual SFUSM render on exact single files; use original EN as structural template
for g,text in manual_text.items():
    matches=[p for p in SRC.iterdir() if p.is_file() and (p.name==g or p.name.startswith(g+'_'))]
    if not matches: continue
    if g=='SPDATA00BTN_EN':
        # use representative canvas and redraw split yes/no
        p=matches[0]; tmp=PNG/(g+'_src.png'); out=PNG/(g+'.png')
        subprocess.run([str(EXE),'export',str(p),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        im=Image.open(tmp).convert('RGBA'); d=ImageDraw.Draw(im); d.rectangle((0,0,im.width,im.height),fill=(0,0,0,0))
        f=ImageFont.truetype(str(FONT),max(18,int(im.height*.32)))
        for yy,tx in [(int(im.height*.25),'是'),(int(im.height*.72),'否')]:
            bb=d.textbbox((0,0),tx,font=f,stroke_width=1); x=(im.width-(bb[2]-bb[0]))//2; y=yy-(bb[3]-bb[1])//2-bb[1]; d.text((x,y),tx,font=f,fill=(255,255,255,255),stroke_width=1,stroke_fill=(0,0,0,255))
        im.save(out); subprocess.run([str(EXE),'import',str(p),str(out),str(WORK/p.name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); report['manual_text'].append(g)
    else:
        for p in matches:
            tmp=PNG/(p.name+'_src.png'); out=PNG/(p.name+'.png')
            subprocess.run([str(EXE),'export',str(p),str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            redraw_text(tmp,out,text)
            subprocess.run([str(EXE),'import',str(p),str(out),str(WORK/p.name)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        report['manual_text'].append(g)
# repack all entries preserving header metadata/names and 2048 alignment
b=ORIGPAK.read_bytes(); u=lambda o:struct.unpack_from('<I',b,o)[0]
hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0); flags=rest[-1]; pos=32; marker=hl//bs
while u(pos)!=marker:pos+=4
names=[]; q=u(pos-4)
for i in range(fc):
    z=b.find(b'\0',q,hl); names.append(b[q:z].decode('utf-8')); q=z+1
head=bytearray(b[:hl]); data=bytearray(head); off=hl
for i,name in enumerate(names):
    if off%bs: off=((off+bs-1)//bs)*bs
    if len(data)<off:data.extend(b'\0'*(off-len(data)))
    d=(WORK/name).read_bytes(); struct.pack_into('<II',head,pos+i*8,off//bs,len(d))
    # head may have changed after data initialized; data head rewritten later
    data.extend(d); off+=len(d)
if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
data[:hl]=head
OUTPAK.write_bytes(data)
# verify every entry hash equals patched source
rb=OUTPAK.read_bytes(); bad=[]
for i,name in enumerate(names):
    bo,ln=struct.unpack_from('<II',rb,pos+i*8); got=rb[bo*bs:bo*bs+ln]; exp=(WORK/name).read_bytes()
    if got!=exp:bad.append(name)
report.update({'entries':fc,'out_size':len(rb),'verify_bad':bad,'sha256':hashlib.sha256(rb).hexdigest().upper()})
(R/'05_build/othcg_build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('STATIC_PC',len(report['pc_static']),'MANUAL',len(report['manual_text']),'JP_FALLBACK_FILES',len(report['jp_fallback']),'MISSING_JP',len(report['missing_jp']),'VERIFY_BAD',len(bad),'OUT',len(rb),'SHA256',report['sha256'])
print('MISSING_SAMPLE',report['missing_jp'][:20])
