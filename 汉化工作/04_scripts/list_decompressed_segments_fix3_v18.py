from pathlib import Path
D=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main_decompressed')
for f in D.iterdir():
 if f.is_file(): print(f.name,f.stat().st_size)
