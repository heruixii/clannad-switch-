from pathlib import Path
import json,csv,struct,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');SRC=ROOT/'03_text/switch_export/script_json';OUT=ROOT/'03_text/switch_extracted/switch_selects.tsv'
def raw_params(c):
 out=bytearray()
 for p in c.get('paramDatas',[]):
  v=str(p.get('value',''))
  if v.startswith('0x'):out.extend(bytes.fromhex(v[2:].replace(' ','')))
 return bytes(out)
def lp(raw,pos):
 if pos+2>len(raw):raise ValueError('len')
 n=struct.unpack_from('<H',raw,pos)[0];pos+=2;b=raw[pos:pos+n*2];pos+=n*2
 if len(b)!=n*2:raise ValueError('short')
 s=b.decode('utf-16le');
 if raw[pos:pos+2]!=b'\0\0':raise ValueError('term')
 return s,pos+2,n
rows=[];errs=[]
for fp in sorted(SRC.glob('SEEN*.json')):
 d=json.loads(fp.read_text(encoding='utf-8-sig'))
 for ci,c in enumerate(d.get('codes',[])):
  if c.get('opcode')!='SELECT':continue
  raw=raw_params(c)
  try:
   # observed CLANNAD SELECT header is 8 bytes before two LP UTF-16 strings
   jp,p,jl=lp(raw,8);en,p,el=lp(raw,p);tail=raw[p:]
   rows.append({'scene':fp.stem,'code_index':ci,'header_hex':raw[:8].hex().upper(),'jp_len':jl,'en_len':el,'jp_text':jp.replace('\n','\\n').replace('\r','\\r'),'en_text':en.replace('\n','\\n').replace('\r','\\r'),'tail_hex':tail.hex().upper()})
  except Exception as e:errs.append((fp.stem,ci,repr(e),raw.hex().upper()[:200]))
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
print('rows',len(rows),'errors',len(errs),'unique_jp',len(set(r['jp_text'] for r in rows)),'unique_en',len(set(r['en_text'] for r in rows)))
print('headers',collections.Counter(r['header_hex'] for r in rows).most_common(10));print('tails',collections.Counter(r['tail_hex'] for r in rows).most_common(10));print('errors',errs[:10]);print(OUT)
