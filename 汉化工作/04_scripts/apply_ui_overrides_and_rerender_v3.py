from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,re,json
import numpy as np,cv2
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
TAB=R/'03_text/ui_work/ui_ocr_zh_v2.tsv'; OUTTAB=R/'03_text/ui_work/ui_ocr_zh_v3.tsv'; SRCIMG=R/'05_build/ui_png_en'; OUTIMG=R/'05_build/ui_png_zh_v3'; OUTIMG.mkdir(parents=True,exist_ok=True)
FONT=next(p for p in [Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')] if p.exists())
with TAB.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
# exact row overrides by asset and source OCR token/normalized string
ov={
 ('EN_MANUAL01_LINKTO_1_02',None):'基本操作',('EN_MANUAL01_LINKTO_2_07',None):'开始游戏',('EN_MANUAL01_LINKTO_3_09',None):'游戏玩法',('EN_MANUAL01_LINKTO_4_11',None):'系统菜单',('EN_MANUAL01_LINKTO_5_13',None):'功能',('EN_MANUAL01_LINKTO_6_17',None):'设置',('EN_MANUAL01_LINKTO_7_25',None):'保存与读取',('EN_MANUAL01_LINKTO_8_26',None):'联系我们',
 ('EN_MANUAL10','"Dangopedia Keyword" and select "Off"'):'选择“团子词典关键词”，设为“关闭”',
 ('EN_MANUAL13',"there's a girl who liked You wou d you go out with ner?"):'有个女孩喜欢你。你愿意和她交往吗？',
 ('EN_MANUAL18','Lir Buttons ZL/ZR Buttons'):'L/R键、ZL/ZR键',
 ('EN_MANUAL17','Geuter Rositien'):'中央位置',('EN_MANUAL17','Bottom Rositiom'):'底部位置',
 ('EN_MANUAL25','Cangcpeda'):'团子词典',('EN_MANUAL25','Conlia'):'设置',('EN_MANUAL25','Quck Suve'):'快速保存',('EN_MANUAL25','Quick Loud'):'快速读取',('EN_MANUAL25','Ceniig'):'设置',('EN_MANUAL25','Tilla'):'标题画面',('EN_MANUAL25','Quick Suve'):'快速保存',('EN_MANUAL25','MerJal'):'使用说明',('EN_MANUAL25','Qunjcpedd'):'团子词典',
 ('SYSTEM_ICON_EN','Dangopediat'):'团子词典',
}
# rows known to be screenshot noise / too ambiguous to alter safely
skip={
 ('EN_MANUAL17',"'Ensitior '"),('EN_MANUAL17','Of'),('EN_MANUAL17',"Keec 'alking"),('EN_MANUAL17','Jusl [esa'),('EN_MANUAL17','Keep (elking'),
 ('EN_MANUAL25','Mte'),('EN_MANUAL25','~Girl'),('EN_MANUAL25','"Teel-anixious going alone'),('EN_MANUAL25','@Clrd'),('EN_MANUAL25','41s'),('EN_MANUAL25','7 7 } k'),('EN_MANUAL25','0'),('EN_MANUAL25','LCAD'),('EN_MANUAL25','Doc'),('EN_MANUAL25','Ginl'),('EN_MANUAL25','4feel- anxious going alone;'),('EN_MANUAL25','@cha'),('EN_MANUAL25','Ketsual'),
}
for r in rows:
 key=(r['asset'],r['text'])
 if (r['asset'],None) in ov:
  r['final_zh']=ov[(r['asset'],None)];r['render']='1';r['final_method']='asset-fixed'
 if key in ov:
  r['final_zh']=ov[key];r['render']='1';r['final_method']='row-fixed'
 if key in skip:
  r['render']='0';r['final_method']='skip-screenshot-noise';r['final_zh']=''
 # generic cleanup
 z=r.get('final_zh','')
 z=z.replace('丹戈佩迪亚关键词','团子词典关键词').replace('达戈佩迪娅','团子词典').replace('配置','设置')
 z=z.replace('加拿大','CLANNAD').replace('快速装入','快速读取').replace('快速装载','快速读取').replace('快速加载','快速读取')
 z=z.replace('特征','功能').replace('文本日志','文本记录').replace('后端日志','文本记录')
 r['final_zh']=z
fields=rows[0].keys()
with OUTTAB.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
by={}
for r in rows:
 if r['render']=='1' and r['final_zh'].strip():by.setdefault(r['asset'],[]).append(r)
def fitfont(text,w,h):
 size=max(10,int(h*.78)); maxw=max(w*1.35,100)
 while size>9:
  fo=ImageFont.truetype(str(FONT),size); bb=fo.getbbox(text);tw=bb[2]-bb[0];th=bb[3]-bb[1]
  if tw<=maxw and th<=h*1.18:return fo
  size-=1
 return ImageFont.truetype(str(FONT),9)
for p in sorted(SRCIMG.glob('*.png')):
 im=Image.open(p).convert('RGBA');arr=np.array(im)
 for r in by.get(p.stem,[]):
  x1=max(0,int(float(r['x1']))-5);y1=max(0,int(float(r['y1']))-3);x2=min(im.width,int(float(r['x2']))+5);y2=min(im.height,int(float(r['y2']))+3)
  if x2<=x1 or y2<=y1:continue
  region=arr[y1:y2,x1:x2]; alpha=region[:,:,3]; trans=float((alpha<40).mean())
  if trans>.25:arr[y1:y2,x1:x2,3]=0
  else:
   rgb=arr[:,:,:3].copy();mask=np.zeros((im.height,im.width),np.uint8);mask[y1:y2,x1:x2]=255;arr[:,:,:3]=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA)
  im=Image.fromarray(arr,'RGBA');draw=ImageDraw.Draw(im);z=r['final_zh'];fo=fitfont(z,x2-x1,y2-y1)
  crop=np.array(im)[y1:y2,x1:x2,:3];lum=float(crop.mean()) if crop.size else 128
  fill=(20,20,20,255) if lum>145 else (255,255,255,255);stroke=(255,255,255,220) if lum>145 else (0,0,0,220)
  draw.text((x1,y1),z,font=fo,fill=fill,stroke_width=1,stroke_fill=stroke);arr=np.array(im)
 im.save(OUTIMG/p.name)
# QA text table
badpat=re.compile(r'加拿大|丹戈|达戈|快大声|快装|特征|发卡人|涡轮|铁珠|盖特|罗西|Bnoitior|Keec|Lir|Howtol|Ithel|HoWtol|playthe|Ner|oad\)',re.I)
bad=[(r['asset'],r['final_en'],r['final_zh']) for r in rows if r['render']=='1' and badpat.search((r['final_en']+' '+r['final_zh']))]
print(json.dumps({'rows':len(rows),'render_rows':sum(r['render']=='1' for r in rows),'skip_rows':sum(r['render']=='0' for r in rows),'assets_modified':len(by),'bad_text_rows':len(bad)},ensure_ascii=False,indent=2))
for x in bad:print('BAD',x)
