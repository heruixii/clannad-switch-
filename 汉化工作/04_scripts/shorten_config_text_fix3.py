from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_config_chs_ips_fix3_v29.py')
s=p.read_text(encoding='utf-8')
repl={
'【ZR键】快进设置与“按键1”的“ZR键（快进）”相同。\\n$C[AD002D]当前设置为“按住时”。':'【ZR键】快进同“按键1”的ZR键设置。\\n$C[AD002D]当前：按住时。',
'【ZR键】快进设置与“按键1”的“ZR键（快进）”相同。\\n$C[AD002D]当前设置为“开始/解除”。':'【ZR键】快进同“按键1”的ZR键设置。\\n$C[AD002D]当前：开始/解除。',
'【ZR键】快进设置与“按键1”的“ZR键（快进）”相同。\\n$C[AD002D]当前设置为“禁用”。':'【ZR键】快进同“按键1”的ZR键设置。\\n$C[AD002D]当前：禁用。',
'【ZR键】快退设置与“按键1”的“L键（快退）”相同。\\n$C[AD002D]当前设置为“按住时”。':'【ZR键】快退同“按键1”的L键设置。\\n$C[AD002D]当前：按住时。',
'【ZR键】快退设置与“按键1”的“L键（快退）”相同。\\n$C[AD002D]当前设置为“开始/解除”。':'【ZR键】快退同“按键1”的L键设置。\\n$C[AD002D]当前：开始/解除。',
}
for a,b in repl.items():
 if a not in s: print('NOTFOUND',a)
 s=s.replace(a,b)
p.write_text(s,encoding='utf-8')
for b in repl.values(): print(len(b.encode('utf-8'))+1,repr(b))
