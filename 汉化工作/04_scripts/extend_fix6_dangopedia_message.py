from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_buttons_ips_fix6_v19.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace(" 'Next':(0x1E237B,0x1E484A),\n}", " 'Next':(0x1E237B,0x1E484A),\n 'NoKeywords':(0x1DE99C,0x1E4854),\n}")
s=s.replace("for i,v in enumerate(next_bytes):patch[0x1E484A+0x100+i]=v", "for i,v in enumerate(next_bytes):patch[0x1E484A+0x100+i]=v\nempty_kw='没有百科词条。'.encode('utf-8')+b'\\0';assert len(empty_kw)<=32\nfor i,v in enumerate(empty_kw):patch[0x1E4854+0x100+i]=v")
p.write_text(s,encoding='utf-8')
# patch QA expected map and extra string check
q=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\qa_buttons_ips_fix6_v20.py');t=q.read_text(encoding='utf-8-sig')
t=t.replace("old={'Yes':0x1DC084,'No':0x1DCC54,'Back':0x1E3BB7,'Next':0x1E237B};expected={'Yes':'是','No':'否','Back':'返回 ','Next':'下一项'}", "old={'Yes':0x1DC084,'No':0x1DCC54,'Back':0x1E3BB7,'Next':0x1E237B,'NoKeywords':0x1DE99C};expected={'Yes':'是','No':'否','Back':'返回 ','Next':'下一项','NoKeywords':'没有百科词条。'}")
t=t.replace("'next_pool_text':cstr(0x1E484A)", "'next_pool_text':cstr(0x1E484A),'empty_keyword_text':cstr(0x1E4854)")
t=t.replace("rep['next_pool_text']!='下一项'", "rep['next_pool_text']!='下一项' or rep['empty_keyword_text']!='没有百科词条。'")
q.write_text(t,encoding='utf-8')
