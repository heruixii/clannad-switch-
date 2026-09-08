from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
for lang,path in [('jp',ROOT/'03_text/pc_jp/raw/SEEN0414.TXT'),('zh',ROOT/'03_text/pc_zh/raw/SEEN0414.TXT')]:
 dec,h=decompress_blob(path.read_bytes())
 print(lang,'len',len(dec),'hdr',h)
 if lang=='jp':
  for s in ['上書きで何か吹き込む','やめておく','適当に思いついた言葉を発する']:
   b=s.encode('cp932');i=dec.find(b);print(s,'at',i,'hex',dec[i-32:i+len(b)+32].hex() if i>=0 else '')
 else:
  # dump all quote-like runs around structurally similar location percentage to JP first select
  for enc in ['gbk','cp936']:
   try:
    txt='覆盖录入点什么'.encode(enc); print('try zh',enc,dec.find(txt))
   except:pass
 # locate select opcode headers module2 funcs 0-3
 hits=[]
 for i in range(len(dec)-8):
  if dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2 and int.from_bytes(dec[i+3:i+5],'little') in (0,1,2,3,10):hits.append((i,int.from_bytes(dec[i+3:i+5],'little'),int.from_bytes(dec[i+5:i+7],'little'),dec[i+7]))
 print('select headers',len(hits),'first',hits[:20])
 for x in hits[:3]:
  i=x[0];print('RAW',x,dec[i:i+300].hex())
