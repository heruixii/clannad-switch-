from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,re
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
size=0x100+DB+len(db);img=bytearray(size);img[0x100:0x100+len(tb)]=tb;img[0x100+RB:0x100+RB+len(rb)]=rb;img[0x100+DB:0x100+DB+len(db)]=db
ips=(R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips').read_bytes();pos=5
while ips[pos:pos+3]!=b'EOF':
 off=int.from_bytes(ips[pos:pos+3],'big');ln=int.from_bytes(ips[pos+3:pos+5],'big');pos+=5
 if ln==0:rln=int.from_bytes(ips[pos:pos+2],'big');val=ips[pos+2];pos+=3;data=bytes([val])*rln
 else:data=ips[pos:pos+ln];pos+=ln
 img[off:off+len(data)]=data
pt=bytes(img[0x100:0x100+len(tb)]);pr=bytes(img[0x100+RB:0x100+RB+len(rb)])
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(pt,0))
refs={}
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;page=x.operands[1].imm
 for j in range(i+1,min(i+7,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=page+y.operands[2].imm
   if RB<=a<RB+len(pr):refs.setdefault(a,[]).append((x.address,y.address))
   break
rows=[]
for a,hits in refs.items():
 o=a-RB;z=pr.find(b'\0',o,min(len(pr),o+100));
 if z<0 or z==o:continue
 raw=pr[o:z]
 try:s=raw.decode('utf-8')
 except:continue
 if len(s)>32 or len(s)<2 or any(ord(c)>127 for c in s):continue
 if sum(c.isalpha() for c in s)<2:continue
 if not re.fullmatch(r"[A-Za-z0-9 .,'!?()/+\-:%&]+",s):continue
 if any(t in s.lower() for t in ['pak','task::','nvn','cz','system data','voice collection','effect','labelselect','scrselect','titlemovie','debug','adpcm','lpcm','opus']):continue
 rows.append({'addr':a,'text':s,'hits':hits})
rows.sort(key=lambda x:(len(x['text']),x['text'].lower()))
for r in rows:print(hex(r['addr']),repr(r['text']),[(hex(a),hex(b)) for a,b in r['hits']])
(R/'05_build/remaining_short_english_fix6.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('COUNT',len(rows))
