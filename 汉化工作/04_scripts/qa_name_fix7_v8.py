from pathlib import Path
import struct,json,hashlib
from capstone import *
from capstone.arm64 import *
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
# parse/apply fix7 IPS to virtual text/rodata
ip=(R/'05_build/fix7_exefs/CF38595316BAA425E792CE5CD122DFC6.ips').read_bytes();assert ip[:5]==b'PATCH' and ip[-3:]==b'EOF'
pos=5;records=[];patch={}
while ip[pos:pos+3]!=b'EOF':
 off=int.from_bytes(ip[pos:pos+3],'big');ln=int.from_bytes(ip[pos+3:pos+5],'big');pos+=5
 if ln==0:
  rln=int.from_bytes(ip[pos:pos+2],'big');v=ip[pos+2];pos+=3;d=bytes([v])*rln
 else:d=ip[pos:pos+ln];pos+=ln
 records.append((off,d))
 for i,v in enumerate(d):patch[off+i]=v
D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';tb=bytearray((D/'text.bin').read_bytes());rb=bytearray((D/'rodata.bin').read_bytes());RB=0x1A3000
outside=[]
for po,v in patch.items():
 ma=po-0x100
 if 0<=ma<len(tb):tb[ma]=v
 elif RB<=ma<RB+len(rb):rb[ma-RB]=v
 else:outside.append(hex(ma))
repls={
 0x1E5918:'将主角姓名改为“岡崎朋也”以外的名字后，游戏中的语音将无法播放。\n确定要修改吗？',
 0x1E4CA3:'要开启语音输出，需要将主角姓名恢复为默认的“岡崎朋也”。\n是否恢复默认姓名？',
}
prompt_bad=[]
for a,s in repls.items():
 got=bytes(rb[a-RB:a-RB+len(s.encode('utf-8'))+1]);exp=s.encode('utf-8')+b'\0'
 if got!=exp:prompt_bad.append({'addr':hex(a),'got':got.hex(),'exp':exp.hex()})
old_prompts=[
 b'Changing the protagonist\'s name \nfrom "Okazaki Tomoya" will disable \nvoices within the game.\nAre you sure you wish to do this?',
 b'In order to turn on the voice output, it is necessary to return the protagonist\'s name to the default setting \xe2\x80\x9cOkazaki Tomoya\xe2\x80\x9d. Are you sure you want to change the name to the default ?'
]
old_prompt_hits=[x.decode('utf-8',errors='ignore') for x in old_prompts if x in bytes(rb)]
# inherited fix6 dynamic targets still intact by reusing known QA site list
fix6qa=json.loads((R/'05_build/fix6_exefs/FINAL_IPS_QA_fix6.json').read_text(encoding='utf-8'))
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins={x.address:x for x in md.disasm(bytes(tb),0)}
site_bad=[]
for label,sites in fix6qa['resolved'].items():
 for e in sites:
  aa=int(e['site'],16);ab=int(e['add'],16);target=int(e['target'],16)
  x=ins.get(aa);y=ins.get(ab)
  if not x or not y or x.mnemonic!='adrp' or y.mnemonic!='add':site_bad.append([label,e,'missing']);continue
  pg=x.operands[1].imm if len(x.operands)>1 and x.operands[1].type==ARM64_OP_IMM else None
  lo=y.operands[2].imm if len(y.operands)>2 and y.operands[2].type==ARM64_OP_IMM else None
  got=(pg or 0)+(lo or 0)
  if got!=target:site_bad.append([label,e,hex(got)])
# font coverage
info=(R/'05_build/font_package_fix2/FONT.PAK_unpacked/info24').read_bytes();fs,bs,cn=struct.unpack_from('<HHH',info,0);o=6
if cn==100:cn=struct.unpack_from('<H',info,6)[0];o=8
o+=cn*3;ui=struct.unpack_from('<65536H',info,o)
chars=set('朋也'+''.join(repls.values()));missing=[]
for c in sorted(chars):
 cp=ord(c)
 if cp>=128 and cp<65536 and ui[cp]==0:missing.append(c)
# script final checks
s=(R/'05_build/script_package_fix7/SCRIPT.PAK_unpacked/SEEN2417').read_bytes()
rep={
 'ips_size':len(ip),'ips_sha256':hashlib.sha256(ip).hexdigest().upper(),'ips_records':len(records),'ips_outside_segment_writes':outside,
 'prompt_bad':prompt_bad,'old_name_prompt_hits':old_prompt_hits,'inherited_fix6_site_bad':site_bad,
 'font_missing_chars':missing,'font_missing_count':len(missing),
 'seen2417_tomoya_remaining':s.count(b'Tomoya'),'seen2417_pengyou_utf8_count':s.count('朋也'.encode('utf-8')),
 'script_sha256':hashlib.sha256((R/'05_build/script_package_fix7/SCRIPT.PAK.out').read_bytes()).hexdigest().upper()
}
rep['total_bad']=len(outside)+len(prompt_bad)+len(old_prompt_hits)+len(site_bad)+len(missing)+rep['seen2417_tomoya_remaining']+(0 if rep['seen2417_pengyou_utf8_count']>=1 else 1)
(R/'05_build/fix7_name_qa.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));raise SystemExit(1 if rep['total_bad'] else 0)

