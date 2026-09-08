from pathlib import Path
import sys,glob,json,collections
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
base=ROOT/'03_text/pc_zh/raw'; rec=ROOT/'03_text/pc_zh/recovered'
st=collections.Counter();bad=[];total=0
for p in sorted(base.glob('SEEN*.TXT')):
 rp=rec/p.name; use=rp if rp.exists() else p
 try:dec,h=decompress_blob(use.read_bytes())
 except Exception as e:continue
 hits=[]
 for i in range(len(dec)-8):
  if dec[i]==0x23 and dec[i+1]==0 and dec[i+2]==2 and int.from_bytes(dec[i+3:i+5],'little') in (0,1,2,3,10):
   argc=int.from_bytes(dec[i+5:i+7],'little'); func=int.from_bytes(dec[i+3:i+5],'little')
   # find opening brace close to opcode (window expression may precede)
   op=dec.find(b'{',i+8,min(len(dec),i+300))
   if op<0:continue
   # closing brace; text itself should not contain raw ASCII brace unquoted in these selections
   cl=dec.find(b'}',op+1,min(len(dec),op+5000))
   if cl<0:continue
   block=dec[op+1:cl]
   qs=[];q=0
   while q<len(block):
    a=block.find(b'"',q)
    if a<0:break
    b=block.find(b'"',a+1)
    if b<0:break
    qs.append(block[a+1:b]);q=b+1
   hits.append((i,func,argc,len(qs),qs))
 total+=len(hits)
 for x in hits:
  argc,nq=x[2],x[3]
  if nq==argc:st['exact_quote_count']+=1
  else:
   st['mismatch_quote_count']+=1
   if len(bad)<100:
    vals=[]
    for q in x[4]:
     try:vals.append(q.decode('gbk'))
     except:vals.append(q.hex())
    bad.append({'scene':p.stem,'off':x[0],'func':x[1],'argc':argc,'quotes':nq,'vals':vals})
print(json.dumps({'select_blocks':total,'stats':dict(st),'mismatch_examples':bad},ensure_ascii=False,indent=2))
