from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,ast,re,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';IPS=R/'05_build/fix3_exefs/config_chs_v1.ips'
tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
# virtual uncompressed NSO mapped layout: 0x100 header bias used by Atmosphere IPS
size=0x100+DB+len(db);img=bytearray(size);img[0x100:0x100+len(tb)]=tb;img[0x100+RB:0x100+RB+len(rb)]=rb;img[0x100+DB:0x100+DB+len(db)]=db
orig=bytes(img)
# parse/apply standard IPS
b=IPS.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;records=[]
while b[pos:pos+3]!=b'EOF':
 off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
 else:data=b[pos:pos+ln];pos+=ln
 assert off+len(data)<=len(img);img[off:off+len(data)]=data;records.append((off,data))
assert pos==len(b)-3
# Load translation map T by AST from builder
builder=R/'04_scripts/build_config_chs_ips_fix3_v29.py';mod=ast.parse(builder.read_text(encoding='utf-8-sig'));T=None
for n in mod.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='T' for t in n.targets):T=ast.literal_eval(n.value);break
assert T
# Re-disassemble patched text and collect config Latin-origin refs from original list; expected strings are T values.
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True
pt=bytes(img[0x100:0x100+len(tb)]);pins=list(md.disasm(pt,0));ai={x.address:i for i,x in enumerate(pins)}
# rebuild original refs same as builder
origmd=Cs(CS_ARCH_ARM64,CS_MODE_ARM);origmd.detail=True;origmd.skipdata=True;oins=list(origmd.disasm(tb,0))
def cstr_from_orig(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+3000))
 if e<0:return None
 try:return rb[o:e].decode('utf-8')
 except:return None
def has_cjk(s):return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in s)
refs={}
for i,x in enumerate(oins):
 if not(0x14F000<=x.address<0x15C000):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(oins))):
  y=oins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=cstr_from_orig(a)
   if s and len(re.findall(r'[A-Za-z]',s))>=2 and not has_cjk(s) and not s.startswith('ZN4task') and s!='PARTS/VOICE_ICON': refs.setdefault(s,[]).append((x.address,y.address))
   break
assert set(refs)==set(T),(len(refs),len(T),set(refs)^set(T))
def read_patched_str(addr):
 off=0x100+addr;e=img.find(0,off,min(len(img),off+2000));assert e>=0
 return bytes(img[off:e]).decode('utf-8')
bad=[];rows=[]
for s,hs in refs.items():
 exp=T[s]
 for aa,ab in hs:
  x=pins[ai[aa]];y=pins[ai[ab]]
  assert x.mnemonic=='adrp' and y.mnemonic=='add',(s,hex(aa),x.mnemonic,y.mnemonic)
  target=x.operands[1].imm+y.operands[2].imm
  got=read_patched_str(target)
  ok=(got==exp);rows.append((s,exp,aa,ab,target,got,ok))
  if not ok:bad.append(rows[-1])
# touched ranges and unchanged outside
mask=bytearray(len(img))
for off,data in records:mask[off:off+len(data)]=b'\x01'*len(data)
changed=[i for i,(a,c) in enumerate(zip(orig,img)) if a!=c]
outside=sum(1 for i in changed if not mask[i]);inside_unchanged=sum(1 for i,v in enumerate(mask) if v and orig[i]==img[i])
rep={'ips_records':len(records),'ips_bytes':len(b),'original_ui_strings':len(refs),'ui_ref_sites':sum(len(v) for v in refs.values()),'validated_ref_sites':len(rows),'bad_ref_sites':len(bad),'changed_bytes':len(changed),'changed_outside_ips_ranges':outside,'ips_range_bytes_unchanged':inside_unchanged,'virtual_image_sha256':hashlib.sha256(img).hexdigest().upper()}
O=R/'05_build/fix3_exefs/config_chs_v1_offline_qa.json';O.write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
if bad:
 for z in bad[:20]:print('BAD',z)
 raise SystemExit(2)
print('QA_OK 151 strings /',len(rows),'reference sites')
