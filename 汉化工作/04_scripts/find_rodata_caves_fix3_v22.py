from pathlib import Path
b=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed\rodata.bin').read_bytes();base=0x1A3000
runs=[];i=0
while i<len(b):
 if b[i]!=0:i+=1;continue
 j=i+1
 while j<len(b) and b[j]==0:j+=1
 if j-i>=32:runs.append((i,j-i))
 i=j
print('RUNS>=32',len(runs),'TOTAL',sum(n for _,n in runs),'MAX',max(n for _,n in runs))
for o,n in sorted(runs,key=lambda x:x[1],reverse=True)[:80]:print(hex(base+o),hex(o),n)
# contiguous trailing zero
z=len(b)
while z>0 and b[z-1]==0:z-=1
print('TRAIL',len(b)-z,'start',hex(base+z))
