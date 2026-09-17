from pathlib import Path
from collections import defaultdict
import hashlib, json

R=Path(__file__).resolve().parents[1]
P8=R/'05_build/fix8_exefs/CF38595316BAA425E792CE5CD122DFC6.ips'
P9=R/'05_build/fix9_exefs/CF38595316BAA425E792CE5CD122DFC6.ips'
OUT=R/'05_build/fix9_exefs/FINAL_IPS_QA_fix9.json'
TARGET=0x1E4276
KEEP=(0x2A00,0x2A04)
REVERT=[(0x11D24C,0x11D250),(0x160550,0x160554),(0x1606C4,0x1606C8),(0x167EDC,0x167EE0),(0x169AD0,0x169AD4),(0x16D7B8,0x16D7BC)]
RUNTIME_NAME=[0xD2E8,0x143884,0x1438F0,0x16A0BC,0x16A2D4,0x16A3B0,0xF87FC]

def parse(p):
 b=p.read_bytes(); assert b[:5]==b'PATCH' and b[-3:]==b'EOF'
 pos=5;m={};records=[];over=[]
 while b[pos:pos+3]!=b'EOF':
  off=int.from_bytes(b[pos:pos+3],'big');ln=int.from_bytes(b[pos+3:pos+5],'big');pos+=5
  if ln==0:
   rln=int.from_bytes(b[pos:pos+2],'big');val=b[pos+2];pos+=3;data=bytes([val])*rln
  else:data=b[pos:pos+ln];pos+=ln
  for i,v in enumerate(data):
   if off+i in m:over.append(off+i)
   m[off+i]=v
  records.append((off,len(data)))
 assert pos+3==len(b)
 return b,m,records,over

def w(m,o):
 try:return int.from_bytes(bytes(m[o+i] for i in range(4)),'little')
 except KeyError:return None

def adrp(x,pc):
 if x is None or (x&0x9F000000)!=0x90000000:return None
 rd=x&31;u=(((x>>5)&0x7FFFF)<<2)|((x>>29)&3)
 if u&(1<<20):u-=1<<21
 return rd,(pc&~0xFFF)+(u<<12)

def add(x):
 if x is None or (x&0xFF000000)!=0x91000000:return None
 return x&31,(x>>5)&31,((x>>10)&0xFFF)<<(12 if ((x>>22)&1) else 0)

def target_pairs(m,target):
 out=[]
 for off in sorted({x-(x%4) for x in m if 0x100<=x<0x1A3100}):
  if (off-0x100)%4:continue
  pc=off-0x100;a=adrp(w(m,off),pc)
  if not a:continue
  rd,page=a
  for d in range(4,29,4):
   z=add(w(m,off+d))
   if z and z[0]==rd and z[1]==rd and page+z[2]==target:
    out.append((pc,pc+d));break
 return out

b8,m8,r8,o8=parse(P8);b9,m9,r9,o9=parse(P9)
removed=set(m8)-set(m9);added=set(m9)-set(m8);changed={k for k in set(m8)&set(m9) if m8[k]!=m9[k]}
expected={pc+0x100+i for pair in REVERT for pc in pair for i in range(4)}
pairs8=target_pairs(m8,TARGET);pairs9=target_pairs(m9,TARGET)
name_bad=[]
for pc in RUNTIME_NAME:
 off=pc+0x100
 for i in range(4):
  if m8.get(off+i)!=m9.get(off+i): name_bad.append(hex(pc));break
rep={
 'fix8_sha256':hashlib.sha256(b8).hexdigest().upper(),
 'fix9_sha256':hashlib.sha256(b9).hexdigest().upper(),
 'fix8_records':len(r8),'fix9_records':len(r9),
 'fix8_overlap_bytes':len(o8),'fix9_overlap_bytes':len(o9),
 'removed_bytes':len(removed),'expected_removed_bytes':len(expected),
 'removed_exact_match':removed==expected,
 'added_bytes':len(added),'changed_common_bytes':len(changed),
 'close_target':hex(TARGET),
 'fix8_close_pairs':[[hex(a),hex(b)] for a,b in pairs8],
 'fix9_close_pairs':[[hex(a),hex(b)] for a,b in pairs9],
 'fix9_only_expected_display_pair':pairs9==[KEEP],
 'runtime_name_sites_checked':[hex(x) for x in RUNTIME_NAME],
 'runtime_name_sites_changed':name_bad,
 'all_other_fix8_patch_bytes_identical':not added and not changed and removed==expected,
}
rep['total_bad']=sum([
 bool(o8),bool(o9),not rep['removed_exact_match'],bool(added),bool(changed),
 not rep['fix9_only_expected_display_pair'],bool(name_bad),not rep['all_other_fix8_patch_bytes_identical']
])
OUT.write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
if rep['total_bad']:raise SystemExit(2)
