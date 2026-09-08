from pathlib import Path
from capstone import *
from capstone.arm64 import *
import hashlib,json,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
base=R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips';b=base.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF'
# parse base IPS into byte map
pos=5;patch={}
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 for i,v in enumerate(data):patch[off+i]=v
# Apply base to text for source refs scan
pt=bytearray(tb)
for off,v in patch.items():
 mo=off-0x100
 if 0<=mo<len(pt):pt[mo]=v
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(bytes(pt),0))
def refs(addr):
 pg=addr&~0xfff;lo=addr&0xfff;res=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:
     res.append((x.address,y.address));break
 return res
def enc_adrp(pc,target,rd):
 imm=((target&~0xfff)-(pc&~0xfff))>>12;u=imm&((1<<21)-1);return 0x90000000|((u&3)<<29)|((u>>2)<<5)|rd
def enc_add(target,rd):return 0x91000000|((target&0xfff)<<10)|(rd<<5)|rd
# targets: official SC, plus own Next pool
mapping={
 'Yes':(0x1DC084,0x1E693E),
 'No':(0x1DCC54,0x1DB64C),
 'Back':(0x1E3BB7,0x1DD1A2),
 'Next':(0x1E237B,0x1E484A),
 'NoKeywords':(0x1DE99C,0x1E4854),
}
# write custom next string in known free tail
next_bytes='下一项'.encode('utf-8')+b'\0';assert len(next_bytes)==10
for i,v in enumerate(next_bytes):patch[0x1E484A+0x100+i]=v
empty_kw='没有百科词条。'.encode('utf-8')+b'\0';assert len(empty_kw)<=32
for i,v in enumerate(empty_kw):patch[0x1E4854+0x100+i]=v
writes=[]
for label,(old,target) in mapping.items():
 hit=refs(old);print(label,'oldrefs',[(hex(a),hex(c)) for a,c in hit]);assert hit,(label,'no refs')
 for aa,ab in hit:
  x=ins[next(i for i,q in enumerate(ins) if q.address==aa)];name=md.reg_name(x.operands[0].reg);assert name.startswith('x');rd=int(name[1:])
  for addr,data,kind in [(aa,enc_adrp(aa,target,rd).to_bytes(4,'little'),'adrp'),(ab,enc_add(target,rd).to_bytes(4,'little'),'add')]:
   for i,v in enumerate(data):patch[addr+0x100+i]=v
   writes.append({'label':label,'old':hex(old),'target':hex(target),'addr':hex(addr),'kind':kind})
# make contiguous records
items=sorted(patch.items());runs=[]
so=po=items[0][0];buf=bytearray([items[0][1]])
for off,val in items[1:]:
 if off==po+1:buf.append(val)
 else:runs.append((so,bytes(buf)));so=off;buf=bytearray([val])
 po=off
runs.append((so,bytes(buf)))
out=bytearray(b'PATCH')
for off,data in runs:out+=off.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
out+=b'EOF';O=R/'05_build/fix6_exefs';O.mkdir(parents=True,exist_ok=True);ips=O/'CF38595316BAA425E792CE5CD122DFC6.ips';ips.write_bytes(out)
rep={'base_fix4_sha256':hashlib.sha256(b).hexdigest().upper(),'next_pool_addr':'0x1E484A','next_bytes':next_bytes.hex(),'added_instruction_writes':len(writes),'final_records':len(runs),'size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper(),'mapping':mapping,'writes':writes}
(O/'fix6_ips_build_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in rep.items() if k!='writes'},ensure_ascii=False,indent=2))
