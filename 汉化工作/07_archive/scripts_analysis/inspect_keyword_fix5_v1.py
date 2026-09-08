from pathlib import Path
import hashlib,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
paths={
 'switch_orig':R/'03_text/switch_work/paks/SCRIPT.PAK_unpacked/_KEYWORD',
 'final':R/'05_build/script_package/SCRIPT.PAK_unpacked/_KEYWORD',
 'verify':R/'05_build/script_package_verify/SCRIPT.PAK_unpacked/_KEYWORD',
}
for k,p in paths.items():
 b=p.read_bytes();print(k,len(b),hashlib.sha256(b).hexdigest().upper())
 print(' head',b[:128])
 # printable utf8 runs best effort
 try:s=b.decode('utf-8')
 except Exception as e:print(' utf8 fail',e);continue
 runs=re.findall(r'[^\x00-\x08\x0b\x0c\x0e-\x1f]{4,}',s)
 print(' runs',len(runs))
 for x in runs[:30]:print(repr(x[:240]))
print('final_eq_orig',paths['switch_orig'].read_bytes()==paths['final'].read_bytes())
