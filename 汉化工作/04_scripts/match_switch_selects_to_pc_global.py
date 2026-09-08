from pathlib import Path
import csv,sys,collections,re,json
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
S=ROOT/'03_text/switch_extracted/switch_selects.tsv'
with S.open('r',encoding='utf-8-sig',newline='') as f: sw=list(csv.DictReader(f,delimiter='\t'))

def norm(s):
 s=s.replace('$d','')
 return ''.join(c for c in s if re.match(r'[ぁ-んァ-ヶ一-龯A-Za-z0-9＊％]',c))

def jp_blocks(path):
 dec,h=decompress_blob(path.read_bytes()); out=[]
 for i in range(len(dec)-8):
  if not(dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2):continue
  fn=int.from_bytes(dec[i+3:i+5],'little'); argc=int.from_bytes(dec[i+5:i+7],'little')
  if fn not in (0,1,2,3,10):continue
  op=dec.find(b'{',i+8,min(len(dec),i+300)); cl=dec.find(b'}',op+1,min(len(dec),op+8000)) if op>=0 else -1
  if op<0 or cl<0:continue
  b=dec[op+1:cl]
  marks=[m.start() for m in re.finditer(b'\x0a..',b,flags=re.S)]
  texts=[]
  for k,m in enumerate(marks):
   a=m+3; e=marks[k+1] if k+1<len(marks) else len(b)
   raw=b[a:e]
   try:t=raw.decode('cp932',errors='ignore')
   except:t=''
   n=norm(t)
   if n:texts.append(n)
  sig=''.join(texts)
  out.append({'off':i,'argc':argc,'sig':sig})
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
   raw=b[a+1:e]
   try:txt=raw.decode('gbk')
   except:txt=None
   qs.append(txt);q=e+1
  out.append({'off':i,'argc':argc,'quotes':qs})
 return out
jpbase=ROOT/'03_text/pc_jp/raw'; zhbase=ROOT/'03_text/pc_zh/raw'; rec=ROOT/'03_text/pc_zh/recovered'
idx=collections.defaultdict(list); pair={}
for p in sorted(jpbase.glob('SEEN*.TXT')):
 try:j=jp_blocks(p)
 except:continue
 zp=rec/p.name if (rec/p.name).exists() else zhbase/p.name
 try:z=zh_blocks(zp) if zp.exists() else []
 except:z=[]
 for k,b in enumerate(j):
  idx[(b['sig'],b['argc'])].append((p.stem,k,b))
  if k<len(z):pair[(p.stem,k)]=z[k]
res=[];st=collections.Counter();un=[]
for r in sw:
 sig=norm(r['jp_text']);argc=r['jp_text'].count('$d')+1;c=idx.get((sig,argc),[])
 good=[]
 for sc,k,b in c:
  z=pair.get((sc,k))
  if z and len(z['quotes'])==argc and all(x is not None for x in z['quotes']):good.append((sc,k,z))
 if len(good)==1:
  sc,k,z=good[0];res.append({'scene':r['scene'],'code_index':r['code_index'],'pc_scene':sc,'pc_select_index':k,'jp_text':r['jp_text'],'zh_text':'$d'.join(z['quotes']),'match':'global-jp-exact'});st['unique']+=1
 elif len(good)>1:
  # if all Chinese identical, safe despite duplicate source locations
  vals={'$d'.join(x[2]['quotes']) for x in good}
  if len(vals)==1:
   sc,k,z=good[0];res.append({'scene':r['scene'],'code_index':r['code_index'],'pc_scene':sc,'pc_select_index':k,'jp_text':r['jp_text'],'zh_text':next(iter(vals)),'match':'global-jp-duplicate-same-zh'});st['duplicate_same_zh']+=1
  else:st['ambiguous']+=1;un.append((r,len(good),[(x[0],x[1],'$d'.join(x[2]['quotes'])) for x in good[:8]]))
 else:st['no_unique_good']+=1;un.append((r,len(c),[(x[0],x[1]) for x in c[:8]]))
print(json.dumps({'switch':len(sw),'mapped':len(res),'stats':dict(st),'unresolved':len(un)},ensure_ascii=False,indent=2))
for r,n,c in un:print('UN',r['scene'],r['code_index'],'JP=',r['jp_text'],'candidates',n,c)
out=ROOT/'03_text/translated/select_pc_global_map.tsv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(res[0]),delimiter='\t');w.writeheader();w.writerows(res)
print(out)
