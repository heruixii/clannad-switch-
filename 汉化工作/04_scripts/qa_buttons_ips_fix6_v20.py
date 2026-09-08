from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,hashlib,struct,ast
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
size=0x100+DB+len(db);img=bytearray(size);img[0x100:0x100+len(tb)]=tb;img[0x100+RB:0x100+RB+len(rb)]=rb;img[0x100+DB:0x100+DB+len(db)]=db;orig=bytes(img)
ips=R/'05_build/fix6_exefs/CF38595316BAA425E792CE5CD122DFC6.ips';b=ips.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;records=[]
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 img[off:off+len(data)]=data;records.append((off,data))
pt=bytes(img[0x100:0x100+len(tb)]);md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(pt,0));idx={x.address:i for i,x in enumerate(ins)}
def refs(addr):
 pg=addr&~0xfff;lo=addr&0xfff;res=[]
 for i,x in enumerate(ins):
  if x.mnemonic=='adrp' and len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM and x.operands[1].imm==pg:
   r=x.operands[0].reg
   for j in range(i+1,min(i+7,len(ins))):
    y=ins[j]
    if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM and y.operands[2].imm==lo:res.append((x.address,y.address));break
 return res
def cstr(a):
 o=0x100+a;e=img.find(0,o,min(len(img),o+1000));return bytes(img[o:e]).decode('utf-8')
old={'Yes':0x1DC084,'No':0x1DCC54,'Back':0x1E3BB7,'Next':0x1E237B,'NoKeywords':0x1DE99C};expected={'Yes':'是','No':'否','Back':'返回 ','Next':'下一项','NoKeywords':'没有百科词条。'}
# original call sites expected from build report
build=json.loads((R/'05_build/fix6_exefs/fix6_ips_build_report.json').read_text(encoding='utf-8'));sites={}
for w in build['writes']:
 if w['kind']=='adrp':sites.setdefault(w['label'],[]).append(int(w['addr'],16))
site_bad=[];resolved={}
for label,aas in sites.items():
 resolved[label]=[]
 for aa in aas:
  x=ins[idx[aa]]
  # find matching add in next 6 instructions same reg
  reg=x.operands[0].reg;target=None;ab=None
  for j in range(idx[aa]+1,min(idx[aa]+7,len(ins))):
   y=ins[j]
   if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==reg and y.operands[1].reg==reg and y.operands[2].type==ARM64_OP_IMM:
    target=x.operands[1].imm+y.operands[2].imm;ab=y.address;break
  if target is None:site_bad.append([label,hex(aa),'no add']);continue
  got=cstr(target);resolved[label].append({'site':hex(aa),'add':hex(ab),'target':hex(target),'text':got})
  if got!=expected[label]:site_bad.append([label,hex(aa),hex(target),got,expected[label]])
old_remaining={k:[(hex(a),hex(c)) for a,c in refs(v)] for k,v in old.items()}
# inherited fix4 gates from its source lists: moved config old refs + 36 system old refs must stay gone
cfg=json.loads((R/'05_build/fix3_exefs/config_chs_v1_report.json').read_text(encoding='utf-8'))['placements'];cfg_rem=[]
for s,v in cfg.items():
 if v['moved']:
  rr=refs(int(v['old'],16))
  if rr:cfg_rem.append([s,hex(int(v['old'],16)),[(hex(a),hex(c)) for a,c in rr]])
G=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'));sys_rem=[]
for g in G:
 rr=refs(g['en_addr'])
 if rr:sys_rem.append([g['en'],hex(g['en_addr']),[(hex(a),hex(c)) for a,c in rr]])
# patch extent integrity
mask=bytearray(len(img))
for off,data in records:mask[off:off+len(data)]=b'\x01'*len(data)
changed=[i for i,(a,c) in enumerate(zip(orig,img)) if a!=c]
rep={'ips_size':len(b),'ips_sha256':hashlib.sha256(b).hexdigest().upper(),'records':len(records),'resolved':resolved,'site_bad':site_bad,'old_button_refs_remaining':old_remaining,'old_button_ref_count':sum(len(v) for v in old_remaining.values()),'inherited_moved_config_refs_remaining':len(cfg_rem),'inherited_system_refs_remaining':len(sys_rem),'changed_bytes':len(changed),'changed_outside_ips_ranges':sum(1 for i in changed if not mask[i]),'next_pool_text':cstr(0x1E484A),'empty_keyword_text':cstr(0x1E4854),'cfg_remaining':cfg_rem[:10],'sys_remaining':sys_rem[:10]}
(R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in rep.items() if k not in ('cfg_remaining','sys_remaining')},ensure_ascii=False,indent=2));bad=site_bad or rep['old_button_ref_count'] or cfg_rem or sys_rem or rep['changed_outside_ips_ranges'] or rep['next_pool_text']!='下一项' or rep['empty_keyword_text']!='没有百科词条。';raise SystemExit(1 if bad else 0)
