from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
for fn,base in [('rodata.bin',0x1A3000),('data.bin',0x212000)]:
 b=(D/fn).read_bytes();runs=[];i=0
 while i<len(b):
  if b[i]!=0:i+=1;continue
  j=i+1
  while j<len(b) and b[j]==0:j+=1
  if j-i>=32:runs.append((j-i,base+i,base+j))
  i=j
 runs.sort(reverse=True)
 print('\n',fn,'zero runs',len(runs),'top')
 for n,a,z in runs[:40]:print(n,hex(a),hex(z))
