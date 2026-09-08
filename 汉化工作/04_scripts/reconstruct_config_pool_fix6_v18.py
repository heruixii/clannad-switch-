from pathlib import Path
from capstone import *
from capstone.arm64 import *
import ast,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
# extract T literal from original config builder
mod=ast.parse((R/'04_scripts/build_config_chs_ips_fix3_v29.py').read_text(encoding='utf-8-sig'));T=None
for n in mod.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='T' for t in n.targets):T=ast.literal_eval(n.value);break
assert T is not None
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def cstr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+3000))
 if e<0:return None
 try:return rb[o:e].decode('utf-8')
 except:return None
def has_cjk(s):return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in s)
refs={}
for i,x in enumerate(ins):
 if not(0x14F000<=x.address<0x15C000):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=cstr(a)
   if s and len(re.findall(r'[A-Za-z]',s))>=2 and not has_cjk(s):refs.setdefault(s,{'addr':a,'refs':[]})['refs'].append((x.address,y.address))
   break
exclude={'PARTS/VOICE_ICON'};ui={s:v for s,v in refs.items() if not s.startswith('ZN4task') and s not in exclude}
assert set(ui)<=set(T),(set(ui)-set(T))
placements={};free=[];overflow=[]
for s,v in sorted(ui.items(),key=lambda kv:kv[1]['addr']):
 tr=T[s].encode('utf-8')+b'\0';cap=len(s.encode('utf-8'))+1;a=v['addr']
 if len(tr)<=cap:
  placements[s]=a
  if cap-len(tr)>=4:free.append([a+len(tr),cap-len(tr),s])
 else:overflow.append((s,tr))
for s,tr in sorted(overflow,key=lambda x:len(x[1]),reverse=True):
 cand=[(sz,i) for i,(a,sz,d) in enumerate(free) if sz>=len(tr)];assert cand,(s,len(tr))
 _,i=min(cand);a,sz,d=free[i];placements[s]=a;free[i]=[a+len(tr),sz-len(tr),d]
print('FREE_TOTAL',sum(x[1] for x in free),'RANGES',len(free))
for a,sz,d in sorted(free,key=lambda x:(-x[1],x[0])):print(hex(a),sz,repr(d))
# choose best fit >=10
need=len('下一项'.encode('utf-8'))+1;cand=sorted((sz,a,d) for a,sz,d in free if sz>=need)
print('NEED',need,'CAND',[(s,hex(a),d) for s,a,d in cand[:20]])
assert cand
sel=cand[0];(R/'05_build/fix6_pool_choice.json').write_text(json.dumps({'addr':hex(sel[1]),'size':sel[0],'donor':sel[2],'need':need},ensure_ascii=False,indent=2),encoding='utf-8')
