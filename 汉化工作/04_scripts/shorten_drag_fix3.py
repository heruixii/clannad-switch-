from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_config_chs_ips_fix3_v29.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('在消息窗口内拖动可快进。\\n滑动可自动快进（轻触解除）。','在消息窗口内拖动可快进。\\n滑动自动快进（轻触解除）。')
p.write_text(s,encoding='utf-8')
