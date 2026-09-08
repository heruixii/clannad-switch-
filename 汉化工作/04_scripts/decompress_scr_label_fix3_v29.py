from pathlib import Path
import struct,re,binascii
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');p=R/'05_build/script_package/SCRIPT.PAK_unpacked/_SCR_LABEL';b=p.read_bytes()
magic=b[:4];rawsz,blocks,ccount,raw2=struct.unpack_from('<4I',b,4);codes=list(struct.unpack_from('<%dH'%ccount,b,20))
print('HEADER',magic,rawsz,blocks,ccount,raw2,'file',len(b),'expected',20+ccount*2,'firstcodes',codes[:20])
# LucaSystem LzwUtil.Decompress exactly: dictionary 0..255, w=dictionary[0], do not remove first code
D={i:bytes([i]) for i in range(256)};w=D[0];out=bytearray()
for idx,k in enumerate(codes):
 if k in D: entry=D[k]
 elif k==len(D): entry=w+w[:1]
 else: raise RuntimeError((idx,k,len(D)))
 out+=entry;D[len(D)]=w+entry[:1];w=entry
print('DECOMP',len(out),'rawsz',rawsz,'sha?',binascii.crc32(out)&0xffffffff)
q=R/'05_build/scr_label_fix3';q.mkdir(parents=True,exist_ok=True);(q/'_SCR_LABEL.raw').write_bytes(out)
# print strings in common encodings, plus raw ascii runs
for enc in ['utf-8','cp932','utf-16le']:
 try:s=out.decode(enc,errors='ignore')
 except:continue
 print('\n###',enc)
 arr=[]
 for z in re.split(r'[\x00\r\n]+',s):
  z=z.strip()
  if len(z)>=2 and (re.search(r'(?i)new|game|load|after|story|cg|music|config|name|dango|manual|title|start|language|basic|button|text|voice|sound',z) or any('\u3040'<=c<='\u9fff' for c in z)):
   arr.append(z[:300])
 print('hits',len(arr))
 for z in arr[:300]:print(repr(z))
# ASCII runs around meaningful words
print('\nASCII_RUNS')
for m in re.finditer(rb'[\x20-\x7e]{3,}',out):
 s=m.group().decode('ascii','ignore')
 if re.search(r'(?i)new|game|load|after|story|cg|music|config|name|dango|manual|title|start|language',s):print(hex(m.start()),repr(s))
