from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import csv,re,json,math
import numpy as np, cv2
import argostranslate.translate as tr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=R/'03_text/ui_work/ui_ocr_refined_v2.tsv'; IMG=R/'05_build/ui_png_en'; OUTTAB=R/'03_text/ui_work/ui_ocr_zh_v2.tsv'; OUTIMG=R/'05_build/ui_png_zh_v2'
OUTIMG.mkdir(parents=True,exist_ok=True)
font_candidates=[Path(r'C:\Windows\Fonts\msyh.ttc'),Path(r'C:\Windows\Fonts\msyhbd.ttc'),Path(r'C:\Windows\Fonts\simhei.ttf')]
FONT=next(p for p in font_candidates if p.exists())
langs=tr.get_installed_languages(); en=next(x for x in langs if x.code=='en'); zh=next(x for x in langs if x.code=='zh'); trans=en.get_translation(zh)
with SRC.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
# fixed glossary
fixed={
'Configuration':'配置','Basic':'基本','Button1':'按键1','Button2':'按键2','Touch':'触控','Text1':'文本1','Text2':'文本2','Sound':'声音','Voice':'语音',
'Save':'保存','Load':'读取','Dangopedia':'团子词典','Config':'设置','Title':'标题画面','Title Screen':'标题画面','Quick Save':'快速保存','Quick Load':'快速读取','Manual':'使用说明',
'Completion rate':'完成率','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏','Name Change':'姓名变更','Language':'语言','First Name':'名','Last Name':'姓','Cancel':'取消','OK':'确定','0K':'确定',
'Basic Controls':'基本操作','How to Use the Joy-Con(R)':'Joy-Con(R) 使用方法','How to Use the Touchscreen':'触摸屏使用方法','How to Use the Touch Screen':'触摸屏使用方法',
'How to Start the Game':'开始游戏','How to Play the Game':'游戏玩法','About Keywords':'关于关键词','System Menu':'系统菜单','Message Log':'文本记录','Skip & Rewind':'快进与回退','Rewind':'回退','Skip':'快进','Auto Mode':'自动模式','Jump':'跳转','View CGs':'查看CG','Features':'功能',
'NEW GAME':'开始游戏','NAME':'姓名','LOAD':'读取','MANUAL':'使用说明','CONFIG':'设置','DANGOPEDIA':'团子词典',
'Touch screen':'触摸屏','Button':'按键','L Stick':'左摇杆','R Stick':'右摇杆','Directional Buttons':'方向键','VOLUME':'音量','GAME CARD':'游戏卡','R Button':'R键','ZR Button':'ZR键','ZL':'ZL','ZR':'ZR',
'Tap':'点击','Tap and hold':'长按','Drag':'拖动','Flick':'轻扫','Pinch In/Pinch Out':'双指缩小/放大','message window':'消息窗口','User\'s Manual':'使用说明',
'Contact Us':'联系我们','Save & Load':'保存与读取','Screen':'画面','Soft Filter':'柔化滤镜','Color Adjustment':'色彩调整','Voice Output':'语音输出','Sound source':'音源','Font':'字体','Window Transparency':'窗口透明度','Color of Read Text':'已读文本颜色','Dangopedia Keyword':'团子词典关键词','Color':'颜色','Text Speed':'文本速度','Base Wait Time':'基础等待时间','Cursor Control':'光标控制','Auto-Sleep':'自动休眠','Rumble':'震动','Joy-Con Rumble':'Joy-Con 震动','Display':'显示','date':'日期','Two finger tap':'双指点击'
}
# normalization aliases
aliases={
'CIANNAD':'CLANNAD','User9Manua)':'User\'s Manual','UseraManua)':'User\'s Manual','UsersManua)':'User\'s Manual','Buttoni':'Button1','Buttonz':'Button2','Butionz':'Button2','Hext2':'Text2','Text]':'Text1','Textz':'Text2','Volce':'Voice','Dangopediat':'Dangopedia','Dargopedia)':'Dangopedia','Cangcpeda':'Dangopedia','Qunjcpedd':'Dangopedia','Contig':'Config','Conlia':'Config','Ceniig':'Config','Quck Suve':'Quick Save','Quick Suve':'Quick Save','Quick Loud':'Quick Load','iLoad':'Load','EQuick Load':'Quick Load','JHow to Use the Backlog':'How to Use the Backlog','JJump (Forward/Back)':'Jump (Forward/Back)','ARumble':'Rumble','IJoy-Con Rumble':'Joy-Con Rumble','NColor Adjustment':'Color Adjustment','ABase Wait Time':'Base Wait Time','ARight Stick (Right)':'Right Stick (Right)','ARight Stick (Left)':'Right Stick (Left)','ISkip':'Skip','@CG MODE':'CG MODE','ANEW GAME':'NEW GAME','ANAME':'NAME','JLOAD':'LOAD','IMANUAL':'MANUAL','JDANGOPEDIA':'DANGOPEDIA','iTitle Screen':'Title Screen','APinch In/Pinch Out':'Pinch In/Pinch Out','DTap and hold':'Tap and hold','ETap':'Tap','ADrag':'Drag','DFlick':'Flick','Choicess':'Choices','JIgnore her':'Ignore her','Anpan;':'Anpan','Anpan:':'Anpan'
}
term_post=[('系统菜单','系统菜单'),('快速装入','快速读取'),('快速装载','快速读取'),('快速加载','快速读取'),('自动模式','自动模式'),('信息日志','文本记录'),('消息日志','文本记录'),('配置','设置')]
def norm(s):
 s=s.strip().replace('  ',' ')
 if s in aliases:s=aliases[s]
 s=s.replace('0f','of').replace('i5','is').replace('ycu','you').replace("That'5","That's").replace("woman'$","woman's")
 s=re.sub(r'^[@AJDEIX~]+(?=[A-Z][a-z])','',s)
 s=s.replace('Button]','Button1')
 return s.strip()
def zh_for(s):
 key=s.strip(' \"|')
 if key=='CLANNAD':return 'CLANNAD','fixed'
 if key in fixed:return fixed[key],'fixed'
 # see details patterns
 m=re.search(r'See details on page\D*(\d+)\s*[\"\']?([^\"\']*)',s,re.I)
 if m:
  page=m.group(1); label=m.group(2).strip(' ._|[]')
  label=norm(label)
  lz=fixed.get(label)
  if not lz and label:
   try:lz=trans.translate(label)
   except:lz=label
  return (f'详见第{page}页'+(f'“{lz}”' if lz else '')),'rule'
 # common full phrases
 specials={
  'How to Use the Backlog':'文本记录使用方法','Jump(forward)':'向前跳转','Jump(backward)':'向后跳转','Jump (Forward/Back)':'向前/向后跳转','Use skiplrewind touch gestures in the message window':'在消息窗口中使用触控手势进行快进/回退','Press and hold A Button':'按住A键','for AUTO MODE':'用于自动模式','Right Stick (Right)':'右摇杆（右）','Right Stick (Left)':'右摇杆（左）','Color of Read Text':'已读文本颜色','You can change the name of the protagonist, Tomoya Okazaki.':'可以更改主人公冈崎朋也的姓名。','Last name and first name are each at maximum 12 character length.':'姓和名最多各12个字符。',"*Voicing is turned off when the protagonist's name is changed.":'※更改主人公姓名后，将不再播放其姓名语音。',
  'Once you have seen a keyword, you may review it at':'看过一次的关键词，可随时在团子词典中查看。','Title Menu':'标题菜单','Choices':'选项','Apologize':'道歉','Ignore her':'无视她','Girl':'女孩','Anpan':'红豆面包'
 }
 if s in specials:return specials[s],'fixed'
 try:z=trans.translate(s)
 except:z=s
 # terminology cleanup
 repl={'Quick Load':'快速读取','Quick Save':'快速保存','Dangopedia':'团子词典','System Menu':'系统菜单','Message Log':'文本记录','Auto Mode':'自动模式','Config':'设置','Button1':'按键1','Button2':'按键2','View CGs':'查看CG','Text1':'文本1','Text2':'文本2','Joy-Con':'Joy-Con','CLANNAD':'CLANNAD'}
 for a,b in repl.items():z=z.replace(a,b)
 z=z.replace('加拿大','CLANNAD').replace('自动睡眠','自动休眠').replace('快速装载','快速读取').replace('快速装入','快速读取').replace('快速加载','快速读取')
 return z,'argos'
# derive base-page link text by target page for link assets
base_by_asset={}
for r in rows:
 a=r['asset']; t=norm(r.get('refined_text') or r['normalized_en']);
 if '_LINKTO_' not in a and t:base_by_asset.setdefault(a,[]).append(t)
render=[]
for r in rows:
 s=norm(r.get('refined_text') or r['normalized_en']); conf=float(r.get('refined_conf') or r['conf']); asset=r['asset']; keep=True
 # explicit garbage/graphic tokens
 if not s or re.fullmatch(r'[\d\W_=+~]+',s): keep=False
 if conf<.30 and not any(k.lower() in s.lower() for k in ['manual','load','save','config','dangopedia','clannad','girl','page','touch','mode']):keep=False
 if asset.startswith('SYSTEM_ICON') and conf<.35:keep=False
 if asset=='MCM_TITLES_EN':keep=False # soundtrack title atlas: preserve original names
 # link overlay recovery from parent page / target page
 if '_LINKTO_' in asset:
  parent=asset.split('_LINKTO_')[0]; target=asset.rsplit('_',1)[-1].lstrip('0') or '0'
  candidates=[x for x in base_by_asset.get(parent,[]) if re.search(r'page\D*0*'+re.escape(target)+r'\b',x,re.I)]
  if candidates:s=candidates[0];keep=True
 z,method=zh_for(s) if keep else ('','skip')
 # reject obvious junk translations if very low confidence
 if keep and conf<.35 and method=='argos' and not re.search(r'[A-Za-z]{4,}',s): keep=False;z='';method='skip'
 o=dict(r);o['final_en']=s;o['final_zh']=z;o['render']='1' if keep else '0';o['final_method']=method;render.append(o)
fields=list(rows[0].keys())+['final_en','final_zh','render','final_method']
with OUTTAB.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(render)
# render grouped
by={}
for r in render:
 if r['render']=='1':by.setdefault(r['asset'],[]).append(r)
def fitfont(text,w,h):
 size=max(12,int(h*.78)); maxw=max(w*1.35,100)
 while size>10:
  fo=ImageFont.truetype(str(FONT),size); box=fo.getbbox(text); tw=box[2]-box[0]; th=box[3]-box[1]
  if tw<=maxw and th<=h*1.15:return fo
  size-=1
 return ImageFont.truetype(str(FONT),10)
for p in sorted(IMG.glob('*.png')):
 im=Image.open(p).convert('RGBA'); arr=np.array(im); rowsa=by.get(p.stem,[])
 for r in rowsa:
  x1=max(0,int(float(r['x1']))-5);y1=max(0,int(float(r['y1']))-3);x2=min(im.width,int(float(r['x2']))+5);y2=min(im.height,int(float(r['y2']))+3)
  if x2<=x1 or y2<=y1:continue
  box=arr[y1:y2,x1:x2]; alpha=box[:,:,3]; trans_ratio=float((alpha<40).mean())
  # erase old glyphs
  if trans_ratio>.25:
   # text-overlay asset: clear opaque/semitransparent glyph pixels in bbox
   arr[y1:y2,x1:x2,3]=0
  else:
   rgb=arr[:,:,:3].copy(); mask=np.zeros((im.height,im.width),np.uint8);mask[y1:y2,x1:x2]=255
   rgb=cv2.inpaint(rgb,mask,3,cv2.INPAINT_TELEA);arr[:,:,:3]=rgb
  im=Image.fromarray(arr,'RGBA'); draw=ImageDraw.Draw(im)
  z=r['final_zh']; w=max(1,x2-x1);h=max(1,y2-y1); fo=fitfont(z,w,h)
  # choose readable contrast from background
  crop=np.array(im)[y1:y2,x1:x2,:3]; lum=float(crop.mean()) if crop.size else 128
  fill=(20,20,20,255) if lum>145 else (255,255,255,255); stroke=(255,255,255,220) if lum>145 else (0,0,0,220)
  draw.text((x1,y1),z,font=fo,fill=fill,stroke_width=1,stroke_fill=stroke)
  arr=np.array(im)
 im.save(OUTIMG/p.name)
print(json.dumps({'rows':len(render),'rendered_rows':sum(r['render']=='1' for r in render),'skipped_rows':sum(r['render']=='0' for r in render),'assets_total':len(list(IMG.glob('*.png'))),'assets_modified':len(by),'font':str(FONT)},ensure_ascii=False,indent=2))
# suspicious translation report
sus=[]
allow=['CLANNAD','Joy-Con','CG','A','B','R','L','ZL','ZR','AUTO']
for r in render:
 if r['render']!='1':continue
 z=r['final_zh']; latin=re.findall(r'[A-Za-z]{2,}',z)
 bad=[x for x in latin if x not in allow]
 if bad:sus.append((r['asset'],r['final_en'],z,r['conf'],bad))
print('SUSPICIOUS',len(sus))
for x in sus[:80]:print(x)
