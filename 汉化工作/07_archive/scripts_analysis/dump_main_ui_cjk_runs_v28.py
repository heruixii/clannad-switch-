from pathlib import Path
import re,json
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');b=P.read_bytes()
regions=[('config',1137600,1141800),('title',1143800,1147400),('ui2',1147400,1151000),('ui3',1159000,1161800)]
# match contiguous utf8 CJK/kana/hangul plus punctuation/ASCII spaces, minimum one CJK
pat=re.compile(rb'(?:[\x20-\x7e]|\xe3[\x80-\xbf][\x80-\xbf]|[\xe4-\xe9][\x80-\xbf][\x80-\xbf]|\xef[\xbc-\xbf][\x80-\xbf]){2,}')
for name,a,z in regions:
 print('\n###',name,a,z)
 rows=[]
 for m in pat.finditer(b[a:z]):
  raw=m.group();
  try:s=raw.decode('utf-8')
  except:continue
  if not any(ord(c)>=0x3000 for c in s): continue
  s=s.strip()
  if not s: continue
  rows.append((a+m.start(),s))
 for off,s in rows:
  print(f'{off}\t{s}')
# language codes exact standalone-ish
print('\n### LANG CODES')
for code in [b'jpn',b'eng',b'zho',b'chi',b'chs',b'cht',b'fra',b'deu',b'kor']:
 st=0;hits=[]
 while True:
  o=b.find(code,st)
  if o<0:break
  if 1100000<=o<=1200000:hits.append(o)
  st=o+1
 print(code.decode(),hits)
