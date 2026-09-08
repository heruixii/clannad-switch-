from pathlib import Path
import zipfile,hashlib,json,os
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');src=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix3';z=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix3.zip'
if z.exists():z.unlink()
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as q:
    for f in sorted(src.rglob('*')):
        if f.is_file():q.write(f,f.relative_to(src).as_posix())
print('ZIP_CREATED',z,z.stat().st_size)
h=hashlib.sha256()
with z.open('rb') as f:
    for b in iter(lambda:f.read(8<<20),b''):h.update(b)
print('ZIP_SHA256',h.hexdigest().upper())
