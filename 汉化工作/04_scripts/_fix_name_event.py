from pathlib import Path
p=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_pc_control_corpus.py")
s=p.read_text(encoding='utf-8')
# insert helper after clean_zh
needle="""def clean_zh(s):
    s=s.strip()
    # compiler-inserted extra ASCII quotes around Chinese strings; safe to strip only outer quote chars
    while len(s)>=2 and s[0]=='\"' and s[-1]=='\"': s=s[1:-1]
    return s
"""
helper=needle+"""
def standalone_name_match(jt,zt):
    jm=re.fullmatch(r'【([^】]+)】', jt.strip(' \"'))
    if not jm: return False
    z=zt.strip(' \"')
    zm=re.fullmatch(r'【([^】]+)】',z)
    if zm: z=zm.group(1).strip(' \"')
    else: z=z.strip(' \"')
    return z==jm.group(1).strip(' \"')
"""
if 'def standalone_name_match' not in s:
    if needle not in s: raise SystemExit('clean_zh needle missing')
    s=s.replace(needle,helper)
old="""                jm=re.fullmatch(r'【([^】]+)】', trim(jt)); zn=trim(zt).strip('\\\"')
                if jm and zn==jm.group(1):
                    status='name-event'; reason='standalone-speaker-name'
"""
new="""                if standalone_name_match(jt,zt):
                    status='name-event'; reason='standalone-speaker-name'
"""
if old not in s: raise SystemExit('broken name-event snippet missing')
s=s.replace(old,new)
s=s.replace("sfields=['scene','jp_rows','zh_rows','anchors','anchor','equal-segment','source-unusable','review-decode-garbage','review-type-mismatch','review-jp','review-zh']",
            "sfields=['scene','jp_rows','zh_rows','anchors','anchor','equal-segment','name-event','source-unusable','review-decode-garbage','review-type-mismatch','review-jp','review-zh']")
s=s.replace("safe=total['anchor']+total['equal-segment'];print('scenes'",
            "safe=total['anchor']+total['equal-segment']+total['name-event'];print('scenes'")
p.write_text(s,encoding='utf-8')
print('fixed',p)
