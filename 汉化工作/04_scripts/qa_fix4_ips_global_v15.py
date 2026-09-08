from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,hashlib,re,ast
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000;ips=R/'05_build/fix4_exefs/CF38595316BAA425E792CE5CD122DFC6.ips'
# virtual image
size=0x100+DB+len(db);img=bytearray(size);img[0x100:0x100+len(tb)]=tb;img[0x100+RB:0x100+RB+len(rb)]=rb;img[0x100+DB:0x100+DB+len(db)]=db;orig=bytes(img)
b=ips.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;records=[]
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 img[off:off+len(data)]=data;records.append((off,data))
pt=bytes(img[0x100:0x100+len(tb)]);md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(pt,0))
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
# old moved config refs must be gone
cfg=json.loads((R/'05_build/fix3_exefs/config_chs_v1_report.json').read_text(encoding='utf-8'))['placements'];old_bad=[]
for s,v in cfg.items():
 if v['moved']:
  rr=refs(int(v['old'],16))
  if rr:old_bad.append([s,hex(int(v['old'],16)),[(hex(a),hex(b)) for a,b in rr]])
# system old refs must be gone (unless target equals old, none expected)
G=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'));sys_bad=[]
for g in G:
 rr=refs(g['en_addr'])
 if rr:sys_bad.append([g['en'],hex(g['en_addr']),[(hex(a),hex(b)) for a,b in rr]])
# revalidate config visible strings at all original code refs using T map
mod=ast.parse((R/'04_scripts/build_config_chs_ips_fix3_v29.py').read_text(encoding='utf-8-sig'));T=None
for n in mod.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='T' for t in n.targets):T=ast.literal_eval(n.value);break
# original refs from fix3 report placements: scan original code for old address, but target after patch should yield zh at all refs. moved+inplace handled differently
origmd=Cs(CS_ARCH_ARM64,CS_MODE_ARM);origmd.detail=True;origmd.skipdata=True;oins=list(origmd.disasm(tb,0));pidx={x.address:i for i,x in enumerate(ins)}
def orefs(addr):
 pg=addr&~0xfff;lo=addr&0xfff;res=[]
 for i,x in enumerate(oins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(oins))):
    y=oins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:res.append((x.address,y.address));break
 return res
def readstr(addr):
 off=0x100+addr;e=img.find(0,off,min(len(img),off+3000));return bytes(img[off:e]).decode('utf-8')
vis_bad=[];vis_sites=0
for s,v in cfg.items():
 old=int(v['old'],16)
 for aa,ab in orefs(old):
  # only UI refs? for moved globally all; for inplace any shared ref reads same changed string
  x=ins[pidx[aa]];y=ins[pidx[ab]];target=x.operands[1].imm+y.operands[2].imm;got=readstr(target);vis_sites+=1
  if got!=T[s]:vis_bad.append([s,hex(aa),hex(target),got,T[s]])
mask=bytearray(len(img))
for off,data in records:mask[off:off+len(data)]=b'\x01'*len(data)
changed=[i for i,(a,c) in enumerate(zip(orig,img)) if a!=c]
rep={'ips_size':len(b),'ips_sha256':hashlib.sha256(b).hexdigest().upper(),'records':len(records),'old_moved_config_ref_groups_remaining':len(old_bad),'old_system_ref_groups_remaining':len(sys_bad),'config_all_ref_sites_checked':vis_sites,'config_visible_bad':len(vis_bad),'changed_bytes':len(changed),'changed_outside_ips_ranges':sum(1 for i in changed if not mask[i]),'old_bad':old_bad,'sys_bad':sys_bad,'vis_bad':vis_bad[:20]}
(R/'05_build/fix4_exefs/FINAL_IPS_QA_fix4.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in rep.items() if k not in ('old_bad','sys_bad','vis_bad')},ensure_ascii=False,indent=2));
if old_bad or sys_bad or vis_bad or rep['changed_outside_ips_ranges']:raise SystemExit(2)
