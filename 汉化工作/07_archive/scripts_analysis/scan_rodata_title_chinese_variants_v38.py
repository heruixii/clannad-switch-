from pathlib import Path
import json
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');b=(D/'rodata.bin').read_bytes();mem=0x1A3000
terms=['游戏开始','遊戲開始','开始','開始','新游戏','新遊戲','读档','讀檔','读取','讀取','载入','載入','后日谈','後日談','后日譚','後日譚','鉴赏','鑑賞','音乐','音樂','设置','設定','配置','名字','姓名','团子','團子','糰子','百科','说明','說明','手册','手冊','帮助','幫助','返回标题','返回標題','标题','標題']
rows=[]
for t in terms:
 q=t.encode('utf-8');st=0
 while True:
  o=b.find(q,st)
  if o<0:break
  lo=max(0,o-64);hi=min(len(b),o+len(q)+96);ctx=b[lo:hi].decode('utf-8','ignore');ctx=''.join(c if ord(c)>=32 else '·' for c in ctx)
  rows.append({'term':t,'ro_offset':o,'mem_offset':mem+o,'context':ctx});st=o+len(q)
print(json.dumps(rows,ensure_ascii=False,indent=2));(D/'title_chinese_variants_v38.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('HITS',len(rows))
