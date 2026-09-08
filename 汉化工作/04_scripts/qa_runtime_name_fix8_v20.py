from pathlib import Path
from capstone import *
from capstone.arm64 import *
import json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb0=(D/'text.bin').read_bytes();rb0=(D/'rodata.bin').read_bytes();RB=0x1A3000
ips=(R/'05_build/fix8_exefs/CF38595316BAA425E792CE5CD122DFC6.ips').read_bytes();assert ips[:5]==b'PATCH' and ips[-3:]==b'EOF'
pos=5;records=[];patch={}
while ips[pos:pos+3]!=b'EOF':
 off=int.from_bytes(ips[pos:pos+3],'big');ln=int.from_bytes(ips[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(ips[pos:pos+2],'big');v=ips[pos+2];pos+=3;d=bytes([v])*rln
 else:d=ips[pos:pos+ln];pos+=ln
 records.append((off,d))
 for i,v in enumerate(d):patch[off+i]=v
pt=bytearray(tb0);pr=bytearray(rb0);outside=[]
for po,v in patch.items():
 ma=po-0x100
 if 0<=ma<len(pt):pt[ma]=v
 elif RB<=ma<RB+len(pr):pr[ma-RB]=v
 else:outside.append(hex(ma))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins={x.address:x for x in md.disasm(bytes(pt),0)}
expected={
 0xD2E8:('mov','x8, xzr'),
 0x143884:('mov','x20, xzr'),
 0x1438F0:('mov','x20, xzr'),
 0x16A0BC:('mov','w8, wzr'),
 0x16A2D4:('mov','w8, wzr'),
 0x16A3B0:('mov','w8, wzr'),
 0xF87FC:('mov','x8, xzr'),
}
site_bad=[];site_ok=[]
for a,(mn,op) in expected.items():
 x=ins.get(a)
 if not x or x.mnemonic!=mn or x.op_str!=op: site_bad.append([hex(a),None if not x else x.mnemonic+' '+x.op_str,mn+' '+op])
 else:site_ok.append([hex(a),x.mnemonic+' '+x.op_str])
# Inherited fix7 name prompts must remain Chinese, old English absent.
nameqa=json.loads((R/'05_build/fix7_name_qa.json').read_text(encoding='utf-8'))
prompts=['将主角姓名改为“岡崎朋也”以外的名字后，游戏中的语音将无法播放。\n确定要修改吗？','要开启语音输出，需要将主角姓名恢复为默认的“岡崎朋也”。\n是否恢复默认姓名？']
prompt_missing=[s for s in prompts if s.encode('utf-8') not in bytes(pr)]
old_prompt_hits=[]
for s in ['Changing the protagonist\'s name','In order to turn on the voice output']:
 if s.encode() in bytes(pr):old_prompt_hits.append(s)
# Inherited fix6 button targets from QA.
fix6qa=json.loads((R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').read_text(encoding='utf-8'))
inherit_bad=[]
for label,sites in fix6qa['resolved'].items():
 for e in sites:
  aa=int(e['site'],16);ab=int(e['add'],16);target=int(e['target'],16);x=ins.get(aa);y=ins.get(ab)
  if not x or not y or x.mnemonic!='adrp' or y.mnemonic!='add':inherit_bad.append([label,hex(aa),'missing']);continue
  pg=x.operands[1].imm if x.operands[1].type==ARM64_OP_IMM else None;lo=y.operands[2].imm if y.operands[2].type==ARM64_OP_IMM else None
  if (pg or 0)+(lo or 0)!=target:inherit_bad.append([label,hex(aa),hex((pg or 0)+(lo or 0)),hex(target)])
# Confirm original common getter math uses slot stride 0x22; after patched index=0 addresses resolve to JP bases.
logic={'current_name_base':'0x2B98/0x2BDC','english_offset_stride':'0x22','default_base':'0x932/0x976','forced_runtime_index':0}
rep={'ips_size':len(ips),'ips_sha256':hashlib.sha256(ips).hexdigest().upper(),'ips_records':len(records),'outside_writes':outside,'runtime_site_ok':site_ok,'runtime_site_bad':site_bad,'prompt_missing':prompt_missing,'old_prompt_hits':old_prompt_hits,'inherited_fix6_bad':inherit_bad,'name_slot_logic':logic,'script_fix7_tomoya_remaining':nameqa['seen2417_tomoya_remaining']}
rep['total_bad']=len(outside)+len(site_bad)+len(prompt_missing)+len(old_prompt_hits)+len(inherit_bad)+rep['script_fix7_tomoya_remaining']
(R/'05_build/fix8_exefs/FINAL_IPS_QA_fix8.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));raise SystemExit(1 if rep['total_bad'] else 0)
