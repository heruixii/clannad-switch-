from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
for q in ['删除',' 删除 ','删除 ','最新','前往最近一次的存档']:
 b=q.encode('utf-8');st=0;print('\n',repr(q))
 while True:
  o=rb.find(b,st)
  if o<0:break
  # require string-ish boundary
  lo=max(0,o-8);hi=min(len(rb),o+len(b)+16)
  print(hex(RB+o),rb[lo:hi])
  st=o+1
