from pathlib import Path
for fn,base in [('text.bin',0),('data.bin',0x212000)]:
 b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')/fn;b=b.read_bytes();runs=[];i=0
 while i<len(b):
  if b[i]!=0:i+=1;continue
  j=i+1
  while j<len(b) and b[j]==0:j+=1
  if j-i>=64:runs.append((i,j-i))
  i=j
 print('\n',fn,'runs',len(runs),'total',sum(n for _,n in runs),'max',max((n for _,n in runs),default=0))
 for o,n in sorted(runs,key=lambda x:x[1],reverse=True)[:50]:print(hex(base+o),hex(o),n)
