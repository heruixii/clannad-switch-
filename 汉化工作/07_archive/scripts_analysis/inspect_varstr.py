from pathlib import Path
import json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
rows=[]
for fp in sorted((ROOT/'03_text/switch_export/script_json').glob('SEEN*.json')):
 d=json.loads(fp.read_text(encoding='utf-8-sig'))
 for ci,c in enumerate(d['codes']):
  if c.get('opcode')!='VARSTR':continue
  raw=bytearray()
  for p in c.get('paramDatas',[]):
   v=str(p.get('value',''))
   if v.startswith('0x'):raw.extend(bytes.fromhex(v[2:].replace(' ','')))
  rows.append((fp.stem,ci,c.get('info'),bytes(raw),c))
print('count',len(rows),'lengths',collections.Counter(len(x[3]) for x in rows).most_common(20))
for sc,ci,info,raw,c in rows[:80]:
 print('\n',sc,ci,info,'RAW',raw.hex().upper())
 for off in range(min(12,len(raw))):
  b=raw[off:]
  # try nul-terminated utf16le from offsets
  if len(b)>=4:
   try:
    e=b.find(b'\x00\x00')
    if e>=0 and e%2==0:
     s=b[:e].decode('utf-16le')
     if s:print(' off',off,'utf16',repr(s))
   except:pass
