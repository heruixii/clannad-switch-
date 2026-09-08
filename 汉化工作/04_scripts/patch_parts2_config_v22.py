from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,cv2,subprocess,struct,hashlib,json,shutil,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=R/'05_build/parts2_sparse'; OUT=R/'05_build/parts2_fix2'; OUT.mkdir(parents=True,exist_ok=True)
EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())

def erase_language_pixels(en_img, base_img, extra_boxes=()):
    A=np.array(en_img.convert('RGBA')); B=np.array(base_img.convert('RGBA'))
    diff=np.max(np.abs(A.astype(np.int16)-B.astype(np.int16)),axis=2)
    mask=(diff>4).astype(np.uint8)*255
    # Ensure all anti-aliased fringes from both language variants disappear.
    mask=cv2.dilate(mask,np.ones((5,5),np.uint8),iterations=1)
    for x1,y1,x2,y2 in extra_boxes:
        mask[max(0,y1):min(A.shape[0],y2),max(0,x1):min(A.shape[1],x2)]=255
    # Use Telea independently on RGBA; this preserves the Switch-specific frame/gradient instead of replacing the whole asset.
    O=A.copy()
    for ch in range(4): O[:,:,ch]=cv2.inpaint(A[:,:,ch],mask,3,cv2.INPAINT_TELEA)
    return Image.fromarray(O,'RGBA'),mask

def fit(text,w,h,max_size=46):
    s=min(max_size,int(h*.75))
    while s>=14:
        f=ImageFont.truetype(str(FONT),s)
        bb=f.getbbox(text)
        if bb[2]-bb[0]<=w*.88 and bb[3]-bb[1]<=h*.78:return f
        s-=1
    return ImageFont.truetype(str(FONT),14)

def draw_center(im,box,text,max_size=46):
    x1,y1,x2,y2=box; d=ImageDraw.Draw(im); f=fit(text,x2-x1,y2-y1,max_size)
    bb=d.textbbox((0,0),text,font=f,stroke_width=1)
    x=x1+((x2-x1)-(bb[2]-bb[0]))//2-bb[0]; y=y1+((y2-y1)-(bb[3]-bb[1]))//2-bb[1]
    arr=np.array(im.convert('RGBA')); reg=arr[max(0,y1):min(im.height,y2),max(0,x1):min(im.width,x2),:3]
    lum=float(reg.mean()) if reg.size else 80
    fill=(245,245,245,255) if lum<145 else (25,25,25,255)
    stroke=(0,0,0,210) if lum<145 else (255,255,255,210)
    d.text((x,y),text,font=f,fill=fill,stroke_width=1,stroke_fill=stroke)

def patch_pair(stem):
    en=Image.open(SRC/(stem+'_EN.png')).convert('RGBA'); base=Image.open(SRC/(stem+'.png')).convert('RGBA')
    # language-specific pixels are precisely exposed by EN-vs-base diff.
    clean,mask=erase_language_pixels(en,base)
    if stem=='CONFIG_BG':
        # Title is in the same image as the tabs on the Switch update branch.
        draw_center(clean,(18,0,380,120),'设置',max_size=58)
        ybox=(10,8,10,76)
        top=8; bottom=76
    else:
        top=4; bottom=76
    # Nine Switch tabs, including the update-only Screen tab.
    labels=['基本','按键1','按键2','触摸','文本1','文本2','音效','语音','画面']
    left,right=333,1858
    step=(right-left)/9.0
    for i,t in enumerate(labels):
        x1=round(left+i*step); x2=round(left+(i+1)*step)
        draw_center(clean,(x1+5,top,x2-5,bottom),t,max_size=34)
    png=OUT/(stem+'_CHS.png'); clean.save(png)
    # Encode from the untouched PARTS2 EN template; never import in place.
    src_cz=SRC/(stem+'_EN'); out_cz=OUT/(stem+'_CHS')
    subprocess.run([str(EXE),'import',str(src_cz),str(png),str(out_cz)],check=True)
    probe=OUT/(stem+'_CHS.verify.png'); subprocess.run([str(EXE),'export',str(out_cz),str(probe)],check=True)
    A=np.array(clean);B=np.array(Image.open(probe).convert('RGBA'))
    if A.shape!=B.shape: raise RuntimeError(f'CZ shape mismatch {stem}')
    # Palette-backed CZ images may quantize newly rendered colors. Require all material codec differences to stay inside the edited title/tab band.
    d=np.max(np.abs(A.astype(np.int16)-B.astype(np.int16)),axis=2)
    allowed=np.zeros(d.shape,np.uint8)
    if stem=='CONFIG_BG': allowed[0:125,0:1900]=1
    else: allowed[0:80,300:1900]=1
    outside=int(((d>1)&(allowed==0)).sum())
    if outside: raise RuntimeError(f'CZ changed {outside} pixels outside edited region: {stem}')
    return out_cz,png,int((mask>0).sum())

patched={}
for stem in ['CONFIG_BG','CONFIG_TAB']:
    cz,png,maskpix=patch_pair(stem); patched[stem]={'cz':str(cz),'png':str(png),'mask_pixels':maskpix,'size':cz.stat().st_size}

# Rebuild sparse PARTS2.PAK preserving all empty IDs and the unique ID 64116 payload.
orig=R/'03_text/ui_work/PARTS2.PAK'; b=orig.read_bytes(); hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0); pos=40
entries=[]
for i in range(fc):
    bo,ln=struct.unpack_from('<II',b,pos+i*8); data=b[bo*bs:bo*bs+ln] if (bo or ln) else b''
    if i in (8,9): data=(OUT/'CONFIG_BG_CHS').read_bytes()
    if i in (12,13): data=(OUT/'CONFIG_TAB_CHS').read_bytes()
    entries.append(data)
head=bytearray(b[:hl]); out=bytearray(head); off=hl
for i,data in enumerate(entries):
    if not data:
        struct.pack_into('<II',head,pos+i*8,0,0); continue
    if off%bs: off=((off+bs-1)//bs)*bs
    if len(out)<off: out.extend(b'\0'*(off-len(out)))
    struct.pack_into('<II',head,pos+i*8,off//bs,len(data)); out.extend(data); off+=len(data)
if off%bs: out.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
out[:hl]=head
pak=OUT/'PARTS2.PAK.out';pak.write_bytes(out)
# Independent extraction verification.
rb=pak.read_bytes();bad=[];nonzero=[]
for i,exp in enumerate(entries):
    bo,ln=struct.unpack_from('<II',rb,pos+i*8)
    got=rb[bo*bs:bo*bs+ln] if (bo or ln) else b''
    if got!=exp:bad.append(i)
    if exp:nonzero.append({'index':i,'id':idstart+i,'length':len(exp),'block_offset':bo})
rep={'header_length':hl,'entries':fc,'idstart':idstart,'block':bs,'nonzero':nonzero,'bad':bad,'size':len(rb),'sha256':hashlib.sha256(rb).hexdigest().upper(),'patched':patched}
(OUT/'parts2_fix2_verify.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
if bad:raise SystemExit(2)

