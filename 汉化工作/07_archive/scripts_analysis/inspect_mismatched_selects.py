from pathlib import Path
import csv,sys,collections,re
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'
with S.open('r',encoding='utf-8-sig',newline='') as f: sw=list(csv.DictReader(f,delimiter='\t'))
swb=collections.defaultdict(list)
for r in sw: swb[r['scene']].append(r)

def blocks(path,enc):
 dec,h=decompress_blob(path.read_bytes()); out=[]
 for i in range(len(dec)-8):
  if not(dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2):continue
  fn=int.from_bytes(dec[i+3:i+5],'little'); argc=int.from_bytes(dec[i+5:i+7],'little')
  if fn not in (0,1,2,3,10):continue
  op=dec.find(b'{',i+8,min(len(dec),i+300)); cl=dec.find(b'}',op+1,min(len(dec),op+8000)) if op>=0 else -1
  if op<0 or cl<0:continue
  b=dec[op+1:cl]
  # split at debug 0A u16; segments after markers
  marks=[m.start() for m in re.finditer(b'\x0a..',b,flags=re.S)]
  seg=[]
  for k,m in enumerate(marks):
   a=m+3; e=marks[k+1] if k+1<len(marks) else len(b)
   raw=b[a:e]
   try:t=raw.decode(enc,errors='replace')
   except:t=''
   # printable representation
   seg.append(t)
  out.append((i,argc,seg,b))
 return out
# counts mismatched
# resolve PC scene base for split Switch names by stripping suffix as one useful view
for sc,ss in sorted(swb.items()):
 base=sc.split('_')[0]
 pjp=ROOT/'03_text/pc_jp/raw'/f'{base}.TXT'
 if not pjp.exists():continue
 bs=blocks(pjp,'cp932')
 if len(ss)==len(bs) and sc==base:continue
 if sc not in ['SEEN1002','SEEN1003','SEEN1004','SEEN1005','SEEN1006','SEEN1008','SEEN1009','SEEN6800','SEEN6800_1','SEEN6800_2','SEEN6802','SEEN6802_1','SEEN6810','SEEN6811','SEEN7100','SEEN7102','SEEN7400','SEEN7401_3','SEEN7600','SEEN7601']:continue
 print('\n###',sc,'SW',len(ss),'PCBASE',base,'blocks',len(bs))
 for j,r in enumerate(ss):print('SW',j,r['code_index'],r['jp_text'])
 for j,(off,argc,segs,b) in enumerate(bs):
  pretty=[]
  for x in segs:
   y=''.join(c if (c.isprintable() and c not in '\r\n') else ' ' for c in x)
   if re.search(r'[ぁ-んァ-ヶ一-龯]',y):pretty.append(y[:140])
  print('PC',j,'off',off,'argc',argc,'SEGS',pretty[:argc+3])
