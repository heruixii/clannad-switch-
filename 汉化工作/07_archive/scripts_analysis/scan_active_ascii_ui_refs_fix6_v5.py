from pathlib import Path
from capstone import *
from capstone.arm64 import *
import re,struct,json,string
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=bytearray((D/'text.bin').read_bytes());rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
# apply fix4/fix5 IPS to text virtual (same IPS)
ips=(R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips').read_bytes();pos=5
while ips[pos:pos+3]!=b'EOF':
 off=int.from_bytes(ips[pos:pos+3],'big');ln=int.from_bytes(ips[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(ips[pos:pos+2],'big');val=ips[pos+2];pos+=3;data=bytes([val])*rln
 else:data=ips[pos:pos+ln];pos+=ln
 mo=off-0x100
 if 0<=mo<len(tb):tb[mo:mo+len(data)]=data
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(bytes(tb),0))
# build direct ADRP+ADD resolved refs map
refs={}
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;page=x.operands[1].imm
 for j in range(i+1,min(i+7,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   addr=page+y.operands[2].imm
   if RB<=addr<RB+len(rb):refs.setdefault(addr,[]).append((x.address,y.address))
   break
# enumerate null ascii strings starting exactly at ref addresses
rows=[]
for addr,hits in refs.items():
 o=addr-RB
 if o<0 or o>=len(rb):continue
 z=rb.find(b'\0',o,min(len(rb),o+300))
 if z<0 or z==o:continue
 raw=rb[o:z]
 try:s=raw.decode('utf-8')
 except:continue
 if len(s)<2 or len(s)>160:continue
 if sum(c.isalpha() for c in s)<2:continue
 if any(ord(c)>127 for c in s):continue
 # UI-ish score
 score=0
 if ' ' in s:score+=2
 if s[:1].isupper():score+=1
 if re.fullmatch(r"[A-Za-z0-9 .,'!?/()\-:+%&]+",s):score+=2
 if len(s)<=40:score+=1
 badtokens=['::','operator','lambda','/','\\','%s','%d','.cpp','.h','task::','std::','basic_string','typeinfo','vtable','subsdk','nn::','abort','assert','allocation','mutex','thread']
 if any(t.lower() in s.lower() for t in badtokens):score-=5
 if s.startswith('_') or s.isupper() and '_' in s:score-=2
 rows.append({'addr':addr,'text':s,'hits':hits,'score':score})
rows.sort(key=lambda r:(-r['score'],r['text'].lower(),r['addr']))
print('TOTAL_REF_ASCII',len(rows))
for r in rows:
 if r['score']>=4:
  print(f"{hex(r['addr'])}\t{r['score']}\t{r['text']!r}\t{[(hex(a),hex(b)) for a,b in r['hits']]}")
(R/'05_build/active_ascii_refs_fix6.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
