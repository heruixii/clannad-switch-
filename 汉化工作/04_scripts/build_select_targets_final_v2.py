from pathlib import Path
import csv,sys,collections,re,json
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'
G=ROOT/'03_text/translated/select_pc_global_map.tsv'
OUT=ROOT/'03_text/translated/select_targets_complete_v2.tsv'
with S.open('r',encoding='utf-8-sig',newline='') as f: sw=list(csv.DictReader(f,delimiter='\t'))
with G.open('r',encoding='utf-8-sig',newline='') as f: gm={(r['scene'],r['code_index']):r for r in csv.DictReader(f,delimiter='\t')}

def norm(s): return ''.join(c for c in s.replace('$d','') if re.match(r'[ぁ-んァ-ヶ一-龯A-Za-z0-9＊％]',c))
def jp_blocks(path):
 dec,h=decompress_blob(path.read_bytes());out=[]
 for i in range(len(dec)-8):
  if not(dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2):continue
  fn=int.from_bytes(dec[i+3:i+5],'little');argc=int.from_bytes(dec[i+5:i+7],'little')
  if fn not in (0,1,2,3,10):continue
  op=dec.find(b'{',i+8,min(len(dec),i+300));cl=dec.find(b'}',op+1,min(len(dec),op+8000)) if op>=0 else -1
  if op<0 or cl<0:continue
  b=dec[op+1:cl];marks=[m.start() for m in re.finditer(b'\x0a..',b,flags=re.S)];parts=[]
  for k,m in enumerate(marks):
   raw=b[m+3:(marks[k+1] if k+1<len(marks) else len(b))]
   try:t=raw.decode('cp932',errors='ignore')
   except:t=''
   n=norm(t)
   if n:parts.append(n)
  out.append({'argc':argc,'sig':''.join(parts)})
 return out
def zh_blocks(path):
 dec,h=decompress_blob(path.read_bytes());out=[]
 for i in range(len(dec)-8):
  if not(dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2):continue
  fn=int.from_bytes(dec[i+3:i+5],'little');argc=int.from_bytes(dec[i+5:i+7],'little')
  if fn not in (0,1,2,3,10):continue
  op=dec.find(b'{',i+8,min(len(dec),i+300));cl=dec.find(b'}',op+1,min(len(dec),op+8000)) if op>=0 else -1
  if op<0 or cl<0:continue
  b=dec[op+1:cl];qs=[];q=0
  while q<len(b):
   a=b.find(b'"',q)
   if a<0:break
   e=b.find(b'"',a+1)
   if e<0:break
   try:t=b[a+1:e].decode('gbk')
   except:t=None
   qs.append(t);q=e+1
  out.append({'argc':argc,'quotes':qs})
 return out
idx=collections.defaultdict(list)
jpbase=ROOT/'03_text/pc_jp/raw';zhbase=ROOT/'03_text/pc_zh/raw';rec=ROOT/'03_text/pc_zh/recovered'
for p in sorted(jpbase.glob('SEEN*.TXT')):
 try:j=jp_blocks(p);zp=(rec/p.name) if (rec/p.name).exists() else (zhbase/p.name);z=zh_blocks(zp) if zp.exists() else []
 except:continue
 for k,b in enumerate(j):
  zz=z[k] if k<len(z) else None
  if zz and len(zz['quotes'])==b['argc'] and all(x is not None for x in zz['quotes']):
   idx[(b['sig'],b['argc'])].append((p.stem,k,'$d'.join(zz['quotes'])))
MAN={
('SEEN0418','738'):'图书室$d回教室',
('SEEN0418','766'):'图书室$d空教室$d回教室',
('SEEN0419','732'):'去图书室$d去社团活动室$d去资料室',
('SEEN0419','758'):'去图书室$d去社团活动室$d回去',
('SEEN0421','969'):'还是算了$d坚持去美佐枝的房间',
('SEEN0421','991'):'还是算了$d坚持去美佐枝的房间',
('SEEN1427','927'):'坦白告诉她$d暂时保密',
('SEEN1428','7873'):'让她参加讨论$d休息一下',
('SEEN3424','3685'):'真的？可以吗？$d不，已经不需要了',
('SEEN4418','832'):'进入图书室$d回教室',
('SEEN4419','1034'):'在这里分别$d提出送她回家',
('SEEN4420','901'):'离开图书室$d问能不能留在这里',
('SEEN4420','1185'):'读$d不读',
('SEEN4429','93'):'就这样待在家里$d出门',
('SEEN6421','275'):'赶紧去食堂$d看向窗外',
('SEEN6421','2140'):'让她继续努力$d我替她去',
('SEEN6422','260'):'跟智代搭话$d直接走过去',
('SEEN6426','1330'):'继续赶路$d问问看',
('SEEN6428','9871'):'选美佐枝$d还是算了',
('SEEN6430','7423'):'最后选美佐枝$d最后选我',
('SEEN6800_1','8001'):'创立者祭$d追牛节$d只穿围裙日',
('SEEN6800_1','8016'):'模拟考试$d追牛节$d只穿围裙日',
('SEEN6800_1','8207'):'模拟考试$d追团子节$d只穿围裙日',
('SEEN7102','1662'):'等到后天再一起去$d让渚一个人去',
}
out=[];stats=collections.Counter();un=[]
for r in sw:
 k=(r['scene'],r['code_index'])
 if k in gm:
  zh=gm[k]['zh_text'];src=gm[k]['match'];stats['global']+=1
 elif k in MAN:
  zh=MAN[k];src='manual-jp';stats['manual']+=1
 else:
  sig=norm(r['jp_text']);argc=r['jp_text'].count('$d')+1;c=idx.get((sig,argc),[])
  same=[x for x in c if x[0]==r['scene']]
  if len(same)==1:
   zh=same[0][2];src='pc-same-scene';stats['same_scene']+=1
  else:
   # for split scenes, prefer base PC scene if uniquely matching
   base=r['scene'].split('_')[0];bs=[x for x in c if x[0]==base]
   if len(bs)==1:
    zh=bs[0][2];src='pc-base-scene';stats['base_scene']+=1
   else:
    un.append((r,c));continue
 if zh.count('$d')!=r['jp_text'].count('$d'):raise RuntimeError(('delimiter',k,r['jp_text'],zh))
 out.append({'scene':r['scene'],'code_index':r['code_index'],'jp_text':r['jp_text'],'en_text':r['en_text'],'zh_text':zh,'source':src})
print(json.dumps({'rows':len(out),'expected':len(sw),'stats':dict(stats),'unresolved':len(un)},ensure_ascii=False,indent=2))
for r,c in un:print('UN',r['scene'],r['code_index'],r['jp_text'],c)
assert len(out)==len(sw) and not un
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(OUT)
