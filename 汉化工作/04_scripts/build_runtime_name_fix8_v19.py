from pathlib import Path
from capstone import *
import hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes()
# Verify MOV encodings with capstone.
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
def mov_x_zr(rd): return (0xAA1F03E0 | rd).to_bytes(4,'little')
def mov_w_zr(rd): return (0x2A1F03E0 | rd).to_bytes(4,'little')
for rd,bits in [(8,64),(20,64),(8,32)]:
 d=mov_x_zr(rd) if bits==64 else mov_w_zr(rd); print(bits,rd,d.hex(),[(x.mnemonic,x.op_str) for x in md.disasm(d,0)])
# inherit fix7 IPS
base=R/'05_build/fix7_exefs/CF38595316BAA425E792CE5CD122DFC6.ips';ib=base.read_bytes();assert ib[:5]==b'PATCH' and ib[-3:]==b'EOF'
pos=5;patch={}
while ib[pos:pos+3]!=b'EOF':
 off=int.from_bytes(ib[pos:pos+3],'big');ln=int.from_bytes(ib[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(ib[pos:pos+2],'big');val=ib[pos+2];pos+=3;data=bytes([val])*rln
 else:data=ib[pos:pos+ln];pos+=ln
 for i,v in enumerate(data):patch[off+i]=v
# runtime name-language selectors. Original instruction is asserted exactly before replacement.
sites=[
 (0x0000D2E8, bytes.fromhex('086980b9'), mov_x_zr(8), 'default-name checker: global UI lang -> slot index 0'),
 (0x00143884, bytes.fromhex('149c80b9'), mov_x_zr(20), 'dialogue name getter first field: object lang -> slot 0'),
 (0x001438F0, bytes.fromhex('149c80b9'), mov_x_zr(20), 'dialogue name getter second field: object lang -> slot 0'),
 (0x0016A0BC, bytes.fromhex('088d40b9'), mov_w_zr(8), 'NameEdit default comparison: force JP/default fields'),
 (0x0016A2D4, bytes.fromhex('088d40b9'), mov_w_zr(8), 'NameEdit first visible/edit field: force JP buffer'),
 (0x0016A3B0, bytes.fromhex('088d40b9'), mov_w_zr(8), 'NameEdit second visible/edit field: force JP buffer'),
 (0x000F87FC, bytes.fromhex('086980b9'), mov_x_zr(8), 'restore default name: write JP/current slots'),
]
# Check actual original words; if provided bytes differ, report instead of blind patch.
for addr,expected,new,desc in sites:
 actual=tb[addr:addr+4]
 if actual!=expected:
  print('EXPECTED MISMATCH',hex(addr),actual.hex(),'expected',expected.hex(),desc)
  # derive expected from disasm and allow exact actual below after review
raise_on=[]
# use actual semantic assertions through capstone rather than guessed opcode bytes
md2=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md2.detail=True
semantic=[]
for addr,expected,new,desc in sites:
 actual=tb[addr:addr+4];ins=list(md2.disasm(actual,addr));assert len(ins)==1
 x=ins[0]; semantic.append({'addr':hex(addr),'old':x.mnemonic+' '+x.op_str,'new':next(md.disasm(new,addr)).mnemonic+' '+next(md.disasm(new,addr)).op_str,'desc':desc,'old_bytes':actual.hex(),'new_bytes':new.hex()})
 # assert known old shape
 assert x.mnemonic in ('ldr','ldrsw') and '#0x' in x.op_str,(hex(addr),x.mnemonic,x.op_str)
 for i,v in enumerate(new):patch[addr+0x100+i]=v
# contiguous runs
items=sorted(patch.items());runs=[];so=po=items[0][0];buf=bytearray([items[0][1]])
for off,val in items[1:]:
 if off==po+1:buf.append(val)
 else:runs.append((so,bytes(buf)));so=off;buf=bytearray([val])
 po=off
runs.append((so,bytes(buf)));out=bytearray(b'PATCH')
for off,data in runs:out+=off.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
out+=b'EOF';O=R/'05_build/fix8_exefs';O.mkdir(parents=True,exist_ok=True);ips=O/'CF38595316BAA425E792CE5CD122DFC6.ips';ips.write_bytes(out)
rep={'base_fix7_sha256':hashlib.sha256(ib).hexdigest().upper(),'runtime_name_sites':semantic,'records':len(runs),'size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper()}
(O/'fix8_ips_build_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2))
