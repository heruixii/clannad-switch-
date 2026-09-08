from pathlib import Path
import shutil,struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');O=R/'05_build/script_package_fix6';W=O/'SCRIPT.PAK_unpacked'
if O.exists():shutil.rmtree(O)
shutil.copytree(R/'05_build/script_package_fix5/SCRIPT.PAK_unpacked',W)
shutil.copy2(R/'05_build/keyword_fix6/_KEYWORD_CHS',W/'_KEYWORD')
def parse_named(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);flags=rest[-1];pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 q=u(pos-4);names=[]
 for _ in range(fc):z=b.find(b'\0',q,hl);assert z>=0;names.append(b[q:z].decode('utf-8'));q=z+1
 return b,hl,fc,idstart,bs,pos,names
orig=R/'03_text/switch_work/script_probe/SCRIPT.PAK';b,hl,fc,idstart,bs,pos,names=parse_named(orig);head=bytearray(b[:hl]);data=bytearray(head);off=hl
for i,n in enumerate(names):
 d=(W/n).read_bytes();off=((off+bs-1)//bs)*bs
 if len(data)<off:data.extend(b'\0'*(off-len(data)))
 struct.pack_into('<II',head,pos+i*8,off//bs,len(d));data.extend(d);off+=len(d)
if off%bs:
 data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
data[:hl]=head
out=O/'SCRIPT.PAK.out';out.write_bytes(data);rb=out.read_bytes();bad=[];over=[];prev=hl
for i,n in enumerate(names):
 bo,ln=struct.unpack_from('<II',rb,pos+i*8);fo=bo*bs
 if ln and fo<prev:over.append([n,fo,prev])
 if ln:prev=max(prev,fo+ln)
 if rb[fo:fo+ln]!=(W/n).read_bytes():bad.append(n)
base=R/'05_build/script_package_fix5/SCRIPT.PAK_unpacked';diff=[n for n in names if (base/n).read_bytes()!=(W/n).read_bytes()]
kq=json.loads((R/'05_build/keyword_fix6/keyword_fix6_qa.json').read_text(encoding='utf-8'))
rep={'entries':fc,'size':len(rb),'sha256':hashlib.sha256(rb).hexdigest().upper(),'bad':bad,'overlap':over,'changed_vs_fix5':diff,'keyword_qa':kq}
(O/'script_fix6_repack_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));assert not bad and not over and diff==['_KEYWORD'] and not kq['parse_bad'] and not kq['visible_old_english_residue'] and kq['sort_keys_restored'] and kq['directory_groups']==22
