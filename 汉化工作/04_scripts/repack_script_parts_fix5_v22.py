from pathlib import Path
import shutil,struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')

def parse_named(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 if pos+8*fc>hl:raise RuntimeError(('bad table',p,pos,hl,fc))
 names=[]
 if flags&512:
  q=u(pos-4)
  for _ in range(fc):
   z=b.find(b'\0',q,hl);assert z>=0;names.append(b[q:z].decode('utf-8'));q=z+1
 else:names=[str(i) for i in range(fc)]
 return b,hl,fc,idstart,bs,pos,names

def repack(orig,work,out):
 b,hl,fc,idstart,bs,pos,names=parse_named(orig);head=bytearray(b[:hl]);data=bytearray(head);off=hl
 for i,n in enumerate(names):
  f=work/n;assert f.exists(),f;d=f.read_bytes();off=((off+bs-1)//bs)*bs
  if len(data)<off:data.extend(b'\0'*(off-len(data)))
  struct.pack_into('<II',head,pos+i*8,off//bs,len(d));data.extend(d);off+=len(d)
 if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
 data[:hl]=head;out.write_bytes(data)
 rb=out.read_bytes();bad=[]
 for i,n in enumerate(names):
  bo,ln=struct.unpack_from('<II',rb,pos+i*8);got=rb[bo*bs:bo*bs+ln];exp=(work/n).read_bytes()
  if got!=exp:bad.append(n)
 return {'entries':fc,'size':len(rb),'bad':bad,'sha256':hashlib.sha256(rb).hexdigest().upper(),'names':names}
# SCRIPT
SO=R/'05_build/script_package_fix5';SW=SO/'SCRIPT.PAK_unpacked'
if SO.exists():shutil.rmtree(SO)
shutil.copytree(R/'05_build/script_package/SCRIPT.PAK_unpacked',SW)
shutil.copy2(R/'05_build/keyword_fix5/_KEYWORD_CHS',SW/'_KEYWORD')
script_out=SO/'SCRIPT.PAK.out';srep=repack(R/'03_text/switch_work/script_probe/SCRIPT.PAK',SW,script_out)
# Compare work contents with fix4 source directory: exactly _KEYWORD should differ.
diffs=[]
base=R/'05_build/script_package/SCRIPT.PAK_unpacked'
for n in srep['names']:
 if (base/n).read_bytes()!=(SW/n).read_bytes():diffs.append(n)
srep['changed_vs_fix4']=diffs
# PARTS
PO=R/'05_build/ui_packages_fix5';PW=PO/'PARTS.PAK_unpacked'
if PO.exists():shutil.rmtree(PO)
shutil.copytree(R/'05_build/ui_packages_fix4/PARTS.PAK_unpacked',PW)
for n in ['SKIP_ICON_00','SKIP_ICON_01','PS_BUTTON_CHIP']:
 shutil.copy2(R/'05_build/button_fix5'/(n+'.fix5'),PW/n)
parts_out=PO/'PARTS.PAK.out';prep=repack(R/'03_text/ui_work/PARTS.PAK',PW,parts_out)
basep=R/'05_build/ui_packages_fix4/PARTS.PAK_unpacked';diffp=[]
for n in prep['names']:
 if (basep/n).read_bytes()!=(PW/n).read_bytes():diffp.append(n)
prep['changed_vs_fix4']=diffp
rep={'SCRIPT':{k:v for k,v in srep.items() if k!='names'},'PARTS':{k:v for k,v in prep.items() if k!='names'}}
(R/'05_build/repack_fix5_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
assert srep['bad']==[] and diffs==['_KEYWORD'],diffs
assert prep['bad']==[] and sorted(diffp)==sorted(['SKIP_ICON_00','SKIP_ICON_01','PS_BUTTON_CHIP']),diffp
