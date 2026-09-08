from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
terms=['Master Volume','Text Speed','Text','Window','Voice','Touch','Defaults','Default','Sound','Language','Languages','Screen','Transparency','Font','System sounds','Auto','Skip','Cursor Control','Color of Read Text','Soft Filter','Color Adjustment','Quick Load','Sample Voice','Play Voice','Message Window','Rumble feature']
for t in terms:
 q=t.encode();st=0;found=[]
 while True:
  o=rb.find(q,st)
  if o<0:break
  # only likely string boundary
  if o==0 or rb[o-1]==0:found.append(o)
  st=o+1
 for o in found[:8]:
  print('\n###',t,'ro',hex(o),'mem',hex(RB+o))
  lo=max(0,o-500);hi=min(len(rb),o+800);chunk=rb[lo:hi]
  # show NUL-delimited printable utf8-ish strings around hit
  base=lo;pos=0
  for part in chunk.split(b'\0'):
   if len(part)>=2:
    try:s=part.decode('utf-8')
    except: s=part.decode('utf-8','replace')
    if sum(ch.isprintable() for ch in s)>=max(2,int(len(s)*.7)):
     print(hex(RB+base+pos),repr(s[:180]))
   pos+=len(part)+1
