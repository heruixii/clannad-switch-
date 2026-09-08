from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,ast,re,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';bid='CF38595316BAA425E792CE5CD122DFC6';IPS=R/'05_build/fix3_exefs'/(bid+'.ips')
tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
size=0x100+DB+len(db);img=bytearray(size);img[0x100:0x100+len(tb)]=tb;img[0x100+RB:0x100+RB+len(rb)]=rb;img[0x100+DB:0x100+DB+len(db)]=db;orig=bytes(img)
b=IPS.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;records=[]
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 assert off+len(data)<=len(img);img[off:off+len(data)]=data;records.append((off,data))
assert pos==len(b)-3
pt=bytes(img[0x100:0x100+len(tb)]);md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;pins=list(md.disasm(pt,0));ai={x.address:i for i,x in enumerate(pins)}
def readstr(a):
 o=0x100+a;e=img.find(0,o,min(len(img),o+3000));return bytes(img[o:e]).decode('utf-8')
# config map and original refs
mod=ast.parse((R/'04_scripts/build_config_chs_ips_fix3_v29.py').read_text(encoding='utf-8-sig'));T=None
for n in mod.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='T' for t in n.targets):T=ast.literal_eval(n.value);break
omd=Cs(CS_ARCH_ARM64,CS_MODE_ARM);omd.detail=True;omd.skipdata=True;oins=list(omd.disasm(tb,0))
def ostr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+3000))
 try:return rb[o:e].decode('utf-8')
 except:return None
def has_cjk(s):return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in s)
refs={}
for i,x in enumerate(oins):
 if not 0x14F000<=x.address<0x15C000 or x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(oins))):
  y=oins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=ostr(a)
   if s and len(re.findall(r'[A-Za-z]',s))>=2 and not has_cjk(s) and not s.startswith('ZN4task') and s!='PARTS/VOICE_ICON':refs.setdefault(s,[]).append((x.address,y.address))
   break
badcfg=[];cfgsites=0
for s,hs in refs.items():
 for aa,ab in hs:
  x=pins[ai[aa]];y=pins[ai[ab]];target=x.operands[1].imm+y.operands[2].imm;got=readstr(target);cfgsites+=1
  if got!=T[s]:badcfg.append((s,T[s],got,hex(aa),hex(target)))
# system groups
sysrep=json.loads((R/'05_build/fix3_exefs/CLANNAD_CHS_fix3_ips_report.json').read_text(encoding='utf-8'))['system'];badsys=[]
for z in sysrep:
 aa=int(z['code_adrp'],16);ab=int(z['code_add'],16);x=pins[ai[aa]];y=pins[ai[ab]];target=x.operands[1].imm+y.operands[2].imm;got=readstr(target)
 if target!=int(z['target'],16) or got!=z['zh']:badsys.append((z['en'],z['zh'],got,hex(target),z['target']))
mask=bytearray(len(img))
for off,data in records:mask[off:off+len(data)]=b'\x01'*len(data)
changed=[i for i,(a,c) in enumerate(zip(orig,img)) if a!=c]
rep={'build_id':bid,'ips_records':len(records),'ips_size':len(b),'ips_sha256':hashlib.sha256(b).hexdigest().upper(),'config_strings':len(refs),'config_ref_sites':cfgsites,'config_bad':len(badcfg),'system_groups':len(sysrep),'system_bad':len(badsys),'changed_bytes':len(changed),'changed_outside_ips_ranges':sum(1 for i in changed if not mask[i]),'virtual_patched_sha256':hashlib.sha256(img).hexdigest().upper()}
(R/'05_build/fix3_exefs/FINAL_IPS_QA_fix3.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
if badcfg:print('BADCFG',badcfg[:10])
if badsys:print('BADSYS',badsys[:10])
if badcfg or badsys:raise SystemExit(2)
print('FINAL_IPS_QA_OK')
