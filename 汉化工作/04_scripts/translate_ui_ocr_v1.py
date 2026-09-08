from pathlib import Path
import csv,re,json,time
import argostranslate.translate as tr
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=R/'03_text/ui_work/ui_ocr_en.tsv'; OUT=R/'03_text/ui_work/ui_ocr_zh_v1.tsv'
langs=tr.get_installed_languages(); en=next(x for x in langs if x.code=='en'); zh=next(x for x in langs if x.code=='zh'); trans=en.get_translation(zh)
# Exact UI/manual terminology. OCR variants normalized separately.
fixed={
'Configuration':'配置','Basic':'基本','Button1':'按键1','Button2':'按键2','Touch':'触控','Text1':'文本1','Text2':'文本2','Sound':'声音','Voice':'语音',
'Save':'保存','Load':'读取','Dangopedia':'团子词典','Config':'设置','Title':'标题画面','Quick Save':'快速保存','Quick Load':'快速读取','Manual':'使用说明',
'Basic Controls':'基本操作','How to Use the Joy-Con(R)':'Joy-Con(R) 使用方法','How to Use the Touchscreen':'触摸屏使用方法','How to Use the Touch Screen':'触摸屏使用方法',
'How to Start the Game':'开始游戏','How to Play the Game':'游戏玩法','About Keywords':'关于关键词','System Menu':'系统菜单','Message Log':'文本记录','Quick Save':'快速保存','Auto Mode':'自动模式','Jump':'跳转','Skip & Rewind':'快进与回退','View CGs':'查看CG','Touch':'触控','Dangopedia Keyword':'团子词典关键词',
'NEW GAME':'开始游戏','NAME':'姓名','LOAD':'读取','MANUAL':'使用说明','CONFIG':'设置','CG MODE':'CG鉴赏','MUSIC MODE':'音乐鉴赏','DANGOPEDIA':'团子词典',
'Touch screen':'触摸屏','Button':'按键','L Stick':'左摇杆','R Stick':'右摇杆','Directional Buttons':'方向键','VOLUME':'音量','GAME CARD':'游戏卡',
'Tap':'点击','Tap and hold':'长按','Drag':'拖动','Flick':'轻扫','Pinch In/Pinch Out':'双指缩小/放大','message window':'消息窗口',
}
def norm(s):
 s=s.strip()
 # OCR punctuation/character corrections conservative.
 reps={"That'5":"That's","woman'$":"woman's","heartis":"heart is","ycu":"you","0f":"of","i5":"is","Gon":"can","CIANNAD":"CLANNAD","User9Manua)":"User's Manual","UsersManua)":"User's Manual","Volce":"Voice","Buttoni":"Button1","Butionz":"Button2","Buttonz":"Button2","Text]":"Text1","Textz":"Text2","Cargoperja":"Dangopedia","Choicess":"Choices","JIgnore her":"Ignore her","ANEW GAME":"NEW GAME","ANAME":"NAME","JLOAD":"LOAD","IMANUAL":"MANUAL","@CG MODE":"CG MODE","JDANGOPEDIA":"DANGOPEDIA","APinch In/Pinch Out":"Pinch In/Pinch Out","DTap and hold":"Tap and hold","ETap":"Tap","ADrag":"Drag","DFlick":"Flick","iTitle Screen":"Title Screen"}
 if s in reps:s=reps[s]
 s=s.replace('  ',' ')
 return s
with SRC.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
cache={}; out=[]; t=time.time()
for i,r in enumerate(rows,1):
 s0=r['text']; s=norm(s0)
 key=s.strip(' "')
 if key in fixed: z=fixed[key]
 elif s in fixed:z=fixed[s]
 elif re.fullmatch(r'[\d\W_]+',s): z=s
 else:
  if s not in cache:
   try:cache[s]=trans.translate(s)
   except Exception:cache[s]=s
  z=cache[s]
 # post terminology
 for a,b in [('System Menu','系统菜单'),('Message Log','文本记录'),('Quick Save','快速保存'),('Quick Load','快速读取'),('Dangopedia','团子词典'),('Auto Mode','自动模式'),('View CGs','查看CG'),('Config','设置'),('Button1','按键1'),('Button2','按键2'),('Touch','触控')]: z=z.replace(a,b)
 o=dict(r);o['normalized_en']=s;o['zh_text']=z;o['method']='fixed' if (key in fixed or s in fixed) else 'argos';out.append(o)
 if i%50==0:print('TRANSLATED',i,'/',len(rows),flush=True)
fields=list(rows[0].keys())+['normalized_en','zh_text','method']
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print('DONE',len(out),'unique',len(cache),'sec',round(time.time()-t,2))
