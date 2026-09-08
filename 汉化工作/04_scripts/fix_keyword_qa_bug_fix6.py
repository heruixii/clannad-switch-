from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_keyword_directory_fix6_v4.py')
s=p.read_text(encoding='utf-8-sig')
s=s.replace("for idx,total,z,magic,ss in rr:\n z=Z[idx];exp0=orig[idx-1]['title'];exp1=f\"$C[960000]{z['title']}$C[000000]\";expb=f\"$C[960000]{z['title']}$C[000000]$d{z['description']}\"\n if (total,z,magic)!=(357,0,27) or ss != [exp0,exp1,expb,expb]:bad.append(idx)","for idx,total,zero,magic,ss in rr:\n zrow=Z[idx];exp0=orig[idx-1]['title'];exp1=f\"$C[960000]{zrow['title']}$C[000000]\";expb=f\"$C[960000]{zrow['title']}$C[000000]$d{zrow['description']}\"\n if (total,zero,magic)!=(357,0,27) or ss != [exp0,exp1,expb,expb]:bad.append(idx)")
p.write_text(s,encoding='utf-8')
