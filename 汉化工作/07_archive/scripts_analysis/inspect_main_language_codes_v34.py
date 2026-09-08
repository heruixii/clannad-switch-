from pathlib import Path
import binascii,re,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');b=p.read_bytes()
for o in [1131672,1141027,1142733,1143458,1146462,1146752,1156061,1159626,1159630,1163165,1163410]:
 lo=max(0,o-180);hi=min(len(b),o+240);c=b[lo:hi]
 print('\n### OFFSET',o,'HEX')
 print(binascii.hexlify(c).decode())
 print('UTF8-IGNORE')
 s=c.decode('utf-8','ignore');print(''.join(ch if ord(ch)>=32 else '·' for ch in s))
 print('ASCII RUNS')
 for m in re.finditer(rb'[\x20-\x7e]{2,}',c):print(m.start()-(o-lo),m.group().decode('ascii','ignore'))
