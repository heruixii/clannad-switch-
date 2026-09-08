from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\repack_script_fix6_v21.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("if off%bs:data.extend(b'\\0'*(((off+bs-1)//bs)*bs-off));data[:hl]=head", "if off%bs:\n data.extend(b'\\0'*(((off+bs-1)//bs)*bs-off))\ndata[:hl]=head")
p.write_text(s,encoding='utf-8')
