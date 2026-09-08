from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed'); parts=[('ro',0x1A3000,D/'rodata.bin'),('data',0x212000,D/'data.bin')]
terms=['新游戏','開始遊戲','开始游戏','读取','讀取','后日谈','後日談','CG鉴赏','CG鑑賞','音乐鉴赏','音樂鑑賞','设置','設定','姓名','团子百科','團子百科','使用说明','使用說明','手册','手冊','读取游戏','載入','ロード','ゲーム開始','アフターストーリー','ＣＧモード','音楽モード','名前','マニュアル']
for name,base,p in parts:
 b=p.read_bytes();print('\n##',name)
 for t in terms:
  q=t.encode('utf-8');st=0;hs=[]
  while 1:
   o=b.find(q,st)
   if o<0:break
   hs.append(base+o);st=o+1
  if hs:print(t,[hex(x) for x in hs[:30]],'count',len(hs))
