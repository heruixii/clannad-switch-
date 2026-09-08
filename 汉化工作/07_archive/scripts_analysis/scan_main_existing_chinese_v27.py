from pathlib import Path
import json,re
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main'); b=p.read_bytes()
terms=['新游戏','开始游戏','读取','载入','讀取','读取游戏','后日谈','後日談','CG鉴赏','CG鑑賞','音乐鉴赏','音樂鑑賞','设置','設定','姓名','名字','团子百科','糰子百科','使用说明','使用說明','手册','說明書','基本','按键1','按鍵1','按键2','按鍵2','触摸','觸摸','文本1','文字1','文本2','文字2','音效','声音','聲音','语音','語音','画面','畫面','自动休眠','自動休眠','固定待机时间','固定待機時間','绿色等级','綠色等級','蓝色等级','藍色等級','快速读取','快速讀取','快速保存','快速儲存']
rows=[]
for t in terms:
 q=t.encode('utf-8'); start=0
 while True:
  o=b.find(q,start)
  if o<0:break
  lo=max(0,o-80);hi=min(len(b),o+len(q)+120)
  chunk=b[lo:hi]
  # show utf8 with bad bytes removed and C0 controls replaced
  s=chunk.decode('utf-8','ignore')
  s=''.join(ch if ord(ch)>=32 else '·' for ch in s)
  rows.append({'term':t,'offset':o,'context':s})
  start=o+len(q)
print(json.dumps(rows,ensure_ascii=False,indent=2));(p.parent/'existing_chinese_hits_v27.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('HITS',len(rows))
