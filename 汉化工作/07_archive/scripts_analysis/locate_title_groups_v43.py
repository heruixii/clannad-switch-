from pathlib import Path
import json,re
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed');b=(D/'rodata.bin').read_bytes();base=0x1A3000
terms=['Game Start','Load','After Story','AFTER STORY','CG Mode','CG MODE','Music Mode','MUSIC MODE','Config','CONFIG','Name','NAME','Dangopedia','DANGOPEDIA','Manual','MANUAL','ゲーム開始','ロード','アフターストーリー','AFTER STORY','ＣＧモード','CGモード','音楽モード','設定','名前','だんご大家族','用語','マニュアル','开始游戏','读取','后日谈','後日談','CG鉴赏','CG鑑賞','音乐鉴赏','音樂鑑賞','设置','姓名','团子百科','使用说明']
rows=[]
for t in terms:
 q=t.encode('utf-8'); st=0
 while 1:
  o=b.find(q,st)
  if o<0:break
  # exact NUL-ish bounds where possible
  pre=b[o-1] if o else 0; post=b[o+len(q)] if o+len(q)<len(b) else 0
  if pre==0 and post==0:kind='exact_nul'
  elif pre==0:kind='nul_start'
  else:kind='substring'
  lo=max(0,o-50);hi=min(len(b),o+len(q)+80);ctx=b[lo:hi].decode('utf-8','ignore');ctx=''.join(c if ord(c)>=32 else '·' for c in ctx)
  rows.append({'term':t,'ro':o,'mem':base+o,'kind':kind,'context':ctx});st=o+1
rows.sort(key=lambda x:x['mem']);print(json.dumps(rows,ensure_ascii=False,indent=2));(D/'title_groups_v43.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print('TOTAL',len(rows))
