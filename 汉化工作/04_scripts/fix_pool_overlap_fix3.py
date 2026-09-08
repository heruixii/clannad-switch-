from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_config_chs_ips_fix3_v29.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("writes.append((a,tr+b'\\0'*(cap-len(tr)),s,'own'))","writes.append((a,tr,s,'own'))")
p.write_text(s,encoding='utf-8')
