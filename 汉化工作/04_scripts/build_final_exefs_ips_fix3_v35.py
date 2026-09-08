from pathlib import Path
import json,hashlib
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True
# read config IPS records
def read_ips(p):
 b=p.read_bytes();assert b[:5]==b'PATCH' and b[-3:]==b'EOF';pos=5;out=[]
 while b[pos:pos+3]!=b'EOF':
  off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
  if ln==0:
   rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
  else:data=b[pos:pos+ln];pos+=ln
  out.append((off,data,'config'))
 return out
records=read_ips(R/'05_build/fix3_exefs/config_chs_v1.ips')
g=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'))
def cstr(a):
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+1000));return rb[o:e].decode('utf-8')
def enc_adrp(pc,target,rd):
 imm=((target&~0xfff)-(pc&~0xfff))>>12;u=imm&((1<<21)-1);return 0x90000000|((u&3)<<29)|((u>>2)<<5)|rd
def enc_add(target,rd):return 0x91000000|((target&0xfff)<<10)|(rd<<5)|rd
system=[]
for i,x in enumerate(g):
 target=0x1e51f4 if x['en']=='Delete' else x['zh_addr']
 zh=' 删除 ' if x['en']=='Delete' else cstr(target)
 assert any('\u3400'<=c<='\u9fff' for c in zh) or x['en'] in ('Close',), (x['en'],zh)
 aa=x['adrp_off'];ab=x['add_off'];oi=list(md.disasm(tb[aa:aa+4],aa))[0];name=md.reg_name(oi.operands[0].reg);assert name.startswith('x');rd=int(name[1:])
 b1=enc_adrp(aa,target,rd).to_bytes(4,'little');b2=enc_add(target,rd).to_bytes(4,'little')
 q1=list(md.disasm(b1,aa))[0];q2=list(md.disasm(b2,ab))[0];got=q1.operands[1].imm+q2.operands[2].imm;assert got==target
 system += [(aa+0x100,b1,f'system:{x["en"]}:adrp'),(ab+0x100,b2,f'system:{x["en"]}:add')]
 x['final_target']=target;x['final_zh']=zh
records += system
records.sort(key=lambda x:x[0])
# ensure no overlaps, merge contiguous
merged=[]
for off,data,n in records:
 if merged and off<merged[-1][0]+len(merged[-1][1]):raise RuntimeError(('overlap',hex(off),n,hex(merged[-1][0]),merged[-1][2]))
 if merged and off==merged[-1][0]+len(merged[-1][1]):merged[-1]=(merged[-1][0],merged[-1][1]+data,merged[-1][2]+'|'+n)
 else:merged.append((off,data,n))
out=bytearray(b'PATCH')
for off,data,n in merged:out+=off.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
out+=b'EOF'
O=R/'05_build/fix3_exefs';bid='CF38595316BAA425E792CE5CD122DFC6';ips=O/(bid+'.ips');ips.write_bytes(out)
rep={'build_id':bid,'config_records_source':len(records)-len(system),'system_groups':len(g),'system_instruction_writes':len(system),'final_records':len(merged),'size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper(),'system':[{'en':x['en'],'zh':x['final_zh'],'code_adrp':hex(x['adrp_off']),'code_add':hex(x['add_off']),'target':hex(x['final_target'])} for x in g]}
(O/'CLANNAD_CHS_fix3_ips_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in rep.items() if k!='system'},ensure_ascii=False,indent=2));print('IPS',ips)
for x in rep['system']:print(repr(x['en']),'->',repr(x['zh']),x['target'])
