from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\verify_release_sources_fix3_v37.py')
s=p.read_text(encoding='utf-8-sig')
old="p=R/'05_build/parts2_fix2/PARTS2.PAK.out';b,hl,fc,idstart,bs,rows,pos=parse(p);bad=[];nz=[]"
new="p=R/'05_build/parts2_fix2/PARTS2.PAK.out';b=p.read_bytes();hl,fc,idstart,bs,*_=struct.unpack_from('<9I',b,0);pos=40;rows=[]\nfor i in range(fc):\n bo,ln=struct.unpack_from('<II',b,pos+i*8);rows.append((str(i),bo*bs,ln,bo))\nbad=[];nz=[]"
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf-8')
