from pathlib import Path
import shutil,struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');O=R/'05_build/ui_packages_fix4';W=O/'PARTS.PAK_unpacked'
if O.exists():shutil.rmtree(O)
W.mkdir(parents=True)
shutil.copytree(R/'05_build/ui_packages_v1/PARTS.PAK_unpacked',W,dirs_exist_ok=True)
C=R/'05_build/config_fix4'
for n in ['CONFIG_BG','CONFIG_BG_EN','CONFIG_TAB','CONFIG_TAB_EN']:
 shutil.copy2(C/f'PARTS1_{n}_NEUTRAL',W/n)

def repack_named(orig,work,out):
 b=orig.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 q=u(pos-4);names=[]
 for _ in range(fc):z=b.find(b'\0',q,hl);names.append(b[q:z].decode('utf-8'));q=z+1
 head=bytearray(b[:hl]);data=bytearray(head);off=hl
 for i,n in enumerate(names):
  d=(work/n).read_bytes();off=((off+bs-1)//bs)*bs
  if len(data)<off:data.extend(b'\0'*(off-len(data)))
  struct.pack_into('<II',head,pos+i*8,off//bs,len(d));data.extend(d);off+=len(d)
 if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off));data[:hl]=head;out.write_bytes(data)
 rb=out.read_bytes();bad=[]
 for i,n in enumerate(names):bo,ln=struct.unpack_from('<II',rb,pos+i*8);got=rb[bo*bs:bo*bs+ln];exp=(work/n).read_bytes();bad += [n] if got!=exp else []
 return {'entries':fc,'size':len(rb),'bad':bad,'sha256':hashlib.sha256(rb).hexdigest().upper()}
parts_out=O/'PARTS.PAK.out';parts_rep=repack_named(R/'03_text/ui_work/PARTS.PAK',W,parts_out)
# PARTS2 sparse rebuild from untouched original; replace 4 config ids only.
P2O=R/'05_build/parts2_fix4';P2O.mkdir(parents=True,exist_ok=True);orig=R/'03_text/ui_work/PARTS2.PAK';b=orig.read_bytes();hl,fc,idstart,bs,*_=struct.unpack_from('<9I',b,0);pos=40;entries=[]
for i in range(fc):
 bo,ln=struct.unpack_from('<II',b,pos+i*8);entries.append(b[bo*bs:bo*bs+ln] if (bo or ln) else b'')
entries[8]=(C/'PARTS2_CONFIG_BG_CHS').read_bytes();entries[9]=entries[8];entries[12]=(C/'PARTS2_CONFIG_TAB_CHS').read_bytes();entries[13]=entries[12]
head=bytearray(b[:hl]);out=bytearray(head);off=hl
for i,d in enumerate(entries):
 if not d:struct.pack_into('<II',head,pos+i*8,0,0);continue
 off=((off+bs-1)//bs)*bs
 if len(out)<off:out.extend(b'\0'*(off-len(out)))
 struct.pack_into('<II',head,pos+i*8,off//bs,len(d));out.extend(d);off+=len(d)
if off%bs:out.extend(b'\0'*(((off+bs-1)//bs)*bs-off));out[:hl]=head
p2=P2O/'PARTS2.PAK.out';p2.write_bytes(out);rb=p2.read_bytes();bad=[];nz=[]
for i,exp in enumerate(entries):
 bo,ln=struct.unpack_from('<II',rb,pos+i*8);got=rb[bo*bs:bo*bs+ln] if (bo or ln) else b''
 if got!=exp:bad.append(i)
 if exp:nz.append({'index':i,'id':idstart+i,'length':len(exp),'block_offset':bo})
p2rep={'entries':fc,'size':len(rb),'bad':bad,'nonzero':nz,'sha256':hashlib.sha256(rb).hexdigest().upper()}
rep={'PARTS':parts_rep,'PARTS2':p2rep};(R/'05_build/ui_fix4_repack_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));
if parts_rep['bad'] or bad:raise SystemExit(2)
