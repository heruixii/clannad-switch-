from pathlib import Path
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed'
terms=['Tomoya','Okazaki','TOMOYA','OKAZAKI','朋也','岡崎','冈崎','おかざき','ともや']
for fn,base in [('text.bin',0),('rodata.bin',0x1A3000),('data.bin',0x212000)]:
 b=(D/fn).read_bytes();print('\n##',fn,len(b))
 for s in terms:
  hits=[]
  for enc in ['utf-8','utf-16le','cp932']:
   try:pat=s.encode(enc)
   except:continue
   st=0
   while True:
    o=b.find(pat,st)
    if o<0:break
    hits.append((enc,base+o,o,pat));st=o+1
  if hits:
   print(s,[(e,hex(a),p.hex()) for e,a,_,p in hits])
   for e,a,o,p in hits[:6]:print(' ctx',e,hex(a),b[max(0,o-64):o+len(p)+96])
