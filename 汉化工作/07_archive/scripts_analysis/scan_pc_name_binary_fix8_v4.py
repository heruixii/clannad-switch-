from pathlib import Path
files=[('JP',Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\pc_jp\raw\SEEN2417.TXT')),('ZH',Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\pc_zh\raw\SEEN2417.TXT'))]
terms=['朋也','岡崎','冈崎','Tomoya','Okazaki']
for label,p in files:
 b=p.read_bytes();print('\n##',label,p,len(b))
 for s in terms:
  found=[]
  for enc in ['cp932','gb18030','utf-8','utf-16le']:
   try:pat=s.encode(enc)
   except:continue
   st=0
   while True:
    o=b.find(pat,st)
    if o<0:break
    found.append((enc,o,pat));st=o+1
  if found:
   print(s,[(e,hex(o),x.hex()) for e,o,x in found])
   for e,o,x in found[:4]:print(' ctx',e,hex(o),b[max(0,o-80):o+120])
