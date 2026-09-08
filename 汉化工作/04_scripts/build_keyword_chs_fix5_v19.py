from pathlib import Path
import json,struct,hashlib,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');O=R/'05_build/keyword_fix5'
orig=json.loads((O/'keyword_en.json').read_text(encoding='utf-8'))
a=json.loads((O/'keyword_zh_01_35.json').read_text(encoding='utf-8'));b=json.loads((O/'keyword_zh_36_71.json').read_text(encoding='utf-8'))
T={int(k):tuple(v) for k,v in {**a,**b}.items()}
assert set(T)==set(range(1,72)),(len(T),sorted(set(range(1,72))-set(T)))

def packstr(s):
 raw=s.encode('utf-16le');units=len(raw)//2
 assert units<=0xffff
 return struct.pack('<H',units)+raw+b'\0\0'
chunks=[];rows=[]
for r in orig:
 idx=r['index'];title,desc=T[idx]
 display=f'$C[960000]{title}$C[000000]'
 body=f'$C[960000]{title}$C[000000]$d{desc}'
 fields=[title,display,body,body]
 payload=b''.join(packstr(s) for s in fields)
 rec_size=10+len(payload);assert rec_size<=0xffff
 head=struct.pack('<5H',rec_size,r['total'],r['zero'],r['magic'],idx)
 chunks.append(head+payload)
 rows.append({'index':idx,'title':title,'description':desc,'record_size':rec_size,'display_title':display,'body':body})
out=b''.join(chunks);dst=O/'_KEYWORD_CHS';dst.write_bytes(out)
# Parse rebuilt independently.
def parse(buf):
 off=0;rr=[]
 while off<len(buf):
  st=off;size,total,z,magic,idx=struct.unpack_from('<5H',buf,off);off+=10;ss=[]
  for _ in range(4):
   n=struct.unpack_from('<H',buf,off)[0];off+=2;raw=buf[off:off+n*2];off+=n*2;term=struct.unpack_from('<H',buf,off)[0];off+=2
   assert term==0;ss.append(raw.decode('utf-16le'))
  assert off-st==size,(idx,size,off-st);rr.append((idx,total,z,magic,ss,size))
 return rr
rr=parse(out);assert len(rr)==71
bad=[]
for rec in rr:
 idx,total,z,magic,ss,size=rec;title,desc=T[idx];exp=[title,f'$C[960000]{title}$C[000000]',f'$C[960000]{title}$C[000000]$d{desc}',f'$C[960000]{title}$C[000000]$d{desc}']
 if total!=357 or z!=0 or magic!=27 or ss!=exp:bad.append(idx)
# English residue: allow Latin names/technical terms, reject old exact title or old description sentences surviving unchanged.
residue=[]
for old,new in zip(orig,rows):
 blob=new['body']
 olddesc=old['body1'].split('$d',1)[1] if '$d' in old['body1'] else old['body1']
 if olddesc.strip() and olddesc.strip() in blob:residue.append(old['index'])
# font map check from fix2 info24
info=(R/'05_build/font_package_fix2/FONT.PAK_unpacked/info24').read_bytes();fs,bs,cn=struct.unpack_from('<HHH',info,0);off=6
if cn==100: cn=struct.unpack_from('<H',info,6)[0];off=8
off += cn*3
uindex=struct.unpack_from('<65536H',info,off)
chars=sorted(set(''.join(x['title']+x['description'] for x in rows)))
missing=[]
for ch in chars:
 cp=ord(ch)
 if cp>=128 and cp<65536 and uindex[cp]==0 and cp!=32: missing.append(ch)
# index 0 may legitimately map a char? Only space in this format; non-ascii zero means absent.
rep={'records':len(rr),'orig_size':(R/'03_text/switch_work/script_probe/SCRIPT.PAK_unpacked/_KEYWORD').stat().st_size,'new_size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper(),'parse_bad':bad,'old_description_residue':residue,'translation_entries':len(T),'unique_chars':len(chars),'font_missing_chars':missing,'font_missing_count':len(missing)}
(O/'keyword_fix5_qa.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');(O/'keyword_zh_full.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2));raise SystemExit(1 if bad or residue else 0)
