from pathlib import Path
for fn in [r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\pc_jp\raw\SEEN2417.TXT',r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\pc_zh\raw\SEEN2417.TXT']:
 b=Path(fn).read_bytes();print('\n',fn,'size',len(b),'head',b[:64])
 for enc in ['utf-8-sig','utf-16le','utf-16be','cp932','gb18030']:
  try:s=b.decode(enc);print(enc,'ok',repr(s[:200]));
  except Exception as e:print(enc,'fail')
