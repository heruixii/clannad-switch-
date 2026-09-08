from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
# parse fix3 final IPS into byte map
base=R/'05_build/fix3_exefs/CF38595316BAA425E792CE5CD122DFC6.ips';b=base.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;patch={}
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 for i,x in enumerate(data):patch[off+i]=x
# helpers

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
added=[]
def redirect(old,target,label):
 for aa,ab in refs(old):
  oi=list(md.disasm(tb[aa:aa+4],aa))[0];name=md.reg_name(oi.operands[0].reg);assert name.startswith('x');rd=int(name[1:]);pairs=[(aa,enc_adrp(aa,target,rd).to_bytes(4,'little'),'adrp'),(ab,enc_add(target,rd).to_bytes(4,'little'),'add')]
  for addr,data,kind in pairs:
   off=addr+0x100
   # validate disassembly and target reconstruction when both instructions available
   for i,v in enumerate(data):patch[off+i]=v
   added.append((label,old,target,addr,kind))
# all moved config strings: redirect every code ref, not just ConfigWin
cfg=json.loads((R/'05_build/fix3_exefs/config_chs_v1_report.json').read_text(encoding='utf-8'))['placements']
for s,v in cfg.items():
 if v['moved']:redirect(int(v['old'],16),int(v['new'],16),'CFG:'+s)
# all system English refs globally
G=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'))
for g in G:
 target=0x1e51f4 if g['en']=='Delete' else g['zh_addr'];redirect(g['en_addr'],target,'SYS:'+g['en'])
# encode byte map into contiguous IPS records
items=sorted(patch.items());runs=[]
if items:
 so=po=items[0][0];buf=bytearray([items[0][1]])
 for off,val in items[1:]:
  if off==po+1:buf.append(val)
  else:runs.append((so,bytes(buf)));so=off;buf=bytearray([val])
  po=off
 runs.append((so,bytes(buf)))
out=bytearray(b'PATCH')
for off,data in runs:
 assert off<0x1000000 and len(data)<=0xffff
 out+=off.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
out+=b'EOF'
O=R/'05_build/fix4_exefs';O.mkdir(parents=True,exist_ok=True);ips=O/'CF38595316BAA425E792CE5CD122DFC6.ips';ips.write_bytes(out)
# QA all redirected refs on virtual patched text only
pt=bytearray(tb)
for off,val in patch.items():
 mo=off-0x100
 if 0<=mo<len(pt):pt[mo]=val
pmd=Cs(CS_ARCH_ARM64,CS_MODE_ARM);pmd.detail=True;pmd.skipdata=True;pins=list(pmd.disasm(bytes(pt),0));ai={x.address:i for i,x in enumerate(pins)};bad=[];uniq={}
for label,old,target,addr,kind in added:uniq[(label,old,target,addr,kind)]=1
# validate each unique pair by ref start addresses
pairs={}
for label,old,target,addr,kind in uniq:
 pairs.setdefault((label,old,target),set()).add(addr)
for (label,old,target),addrs in pairs.items():
 for aa,ab in refs(old):
  if aa not in ai or ab not in ai:bad.append([label,hex(aa),'missing']);continue
  x=pins[ai[aa]];y=pins[ai[ab]];got=x.operands[1].imm+y.operands[2].imm
  if got!=target:bad.append([label,hex(aa),hex(got),hex(target)])
rep={'base_fix3_sha256':hashlib.sha256(b).hexdigest().upper(),'global_redirect_instruction_writes':len(set((a,k) for _,_,_,a,k in added)),'redirect_groups':len(set((l,o,t) for l,o,t,_,_ in added)),'final_records':len(runs),'size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper(),'bad':bad,'extra_refs_expected':{'English':2,'Quick Load':2,'Close':7,'Defaults':2}}
(O/'fix4_ips_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));
if bad:raise SystemExit(2)
