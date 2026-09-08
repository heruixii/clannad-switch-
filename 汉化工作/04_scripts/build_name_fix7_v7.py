from pathlib import Path
import shutil,struct,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
# ---------- SCRIPT fix7 ----------
O=R/'05_build/script_package_fix7'; W=O/'SCRIPT.PAK_unpacked'
if O.exists(): shutil.rmtree(O)
shutil.copytree(R/'05_build/script_package_fix6/SCRIPT.PAK_unpacked',W)
f=W/'SEEN2417'; b=bytearray(f.read_bytes()); old=b'Tomoya'; new='朋也'.encode('utf-8'); assert len(old)==len(new)==6
hits=[];st=0
while True:
 o=b.find(old,st)
 if o<0: break
 hits.append(o);st=o+1
assert hits==[0x6239],hits
b[hits[0]:hits[0]+6]=new;f.write_bytes(b)
assert old not in f.read_bytes()
# repack named PAK
def parse_named(p):
 b=p.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0];hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);pos=32;marker=hl//bs
 while pos+4<=hl and u(pos)!=marker:pos+=4
 q=u(pos-4);names=[]
 for _ in range(fc):
  z=b.find(b'\0',q,hl);assert z>=0;names.append(b[q:z].decode('utf-8'));q=z+1
 return b,hl,fc,idstart,bs,pos,names
orig=R/'03_text/switch_work/script_probe/SCRIPT.PAK';ob,hl,fc,idstart,bs,pos,names=parse_named(orig);head=bytearray(ob[:hl]);data=bytearray(head);off=hl
for i,n in enumerate(names):
 d=(W/n).read_bytes();off=((off+bs-1)//bs)*bs
 if len(data)<off:data.extend(b'\0'*(off-len(data)))
 struct.pack_into('<II',head,pos+i*8,off//bs,len(d));data.extend(d);off+=len(d)
if off%bs:data.extend(b'\0'*(((off+bs-1)//bs)*bs-off))
data[:hl]=head;out=O/'SCRIPT.PAK.out';out.write_bytes(data)
rb=out.read_bytes();bad=[];over=[];prev=hl
for i,n in enumerate(names):
 bo,ln=struct.unpack_from('<II',rb,pos+i*8);fo=bo*bs
 if ln and fo<prev:over.append([n,fo,prev])
 if ln:prev=max(prev,fo+ln)
 if rb[fo:fo+ln]!=(W/n).read_bytes():bad.append(n)
base=R/'05_build/script_package_fix6/SCRIPT.PAK_unpacked';diff=[n for n in names if (base/n).read_bytes()!=(W/n).read_bytes()]
srep={'entries':fc,'size':len(rb),'sha256':hashlib.sha256(rb).hexdigest().upper(),'bad':bad,'overlap':over,'changed_vs_fix6':diff,'seen2417_tomoya_remaining':(W/'SEEN2417').read_bytes().count(b'Tomoya'),'seen2417_pengyou_utf8_count':(W/'SEEN2417').read_bytes().count(new)}
(O/'script_fix7_repack_report.json').write_text(json.dumps(srep,ensure_ascii=False,indent=2),encoding='utf-8');print('SCRIPT',json.dumps(srep,ensure_ascii=False))
assert not bad and not over and diff==['SEEN2417'] and srep['seen2417_tomoya_remaining']==0 and srep['seen2417_pengyou_utf8_count']>=1
# ---------- IPS fix7: inherit fix6, overwrite EN prompt slots in place ----------
baseips=R/'05_build/fix6_exefs/CF38595316BAA425E792CE5CD122DFC6.ips';ib=baseips.read_bytes();assert ib[:5]==b'PATCH' and ib[-3:]==b'EOF'
posi=5;patch={}
while ib[posi:posi+3]!=b'EOF':
 offi=int.from_bytes(ib[posi:posi+3],'big');ln=int.from_bytes(ib[posi+3:posi+5],'big');posi+=5
 if ln==0:
  rln=int.from_bytes(ib[posi:posi+2],'big');val=ib[posi+2];posi+=3;d=bytes([val])*rln
 else:d=ib[posi:posi+ln];posi+=ln
 for i,v in enumerate(d):patch[offi+i]=v
ro=(R/'05_build/exefs_fix2/update_exefs/main_decompressed/rodata.bin').read_bytes();RB=0x1A3000
repls={
 0x1E5918:'将主角姓名改为“岡崎朋也”以外的名字后，游戏中的语音将无法播放。\n确定要修改吗？',
 0x1E4CA3:'要开启语音输出，需要将主角姓名恢复为默认的“岡崎朋也”。\n是否恢复默认姓名？',
}
prompt_rep=[]
for addr,zh in repls.items():
 o=addr-RB;end=ro.find(b'\0',o);assert end>o
 old=ro[o:end];zb=zh.encode('utf-8')+b'\0';capacity=len(old)+1
 assert len(zb)<=capacity,(hex(addr),len(zb),capacity)
 # zero whole original slot then write zh
 for i in range(capacity):patch[addr+0x100+i]=0
 for i,v in enumerate(zb):patch[addr+0x100+i]=v
 prompt_rep.append({'addr':hex(addr),'old_bytes':len(old),'capacity':capacity,'zh_bytes_with_nul':len(zb),'zh':zh})
# contiguous records
items=sorted(patch.items());runs=[];so=po=items[0][0];buf=bytearray([items[0][1]])
for offi,val in items[1:]:
 if offi==po+1:buf.append(val)
 else:runs.append((so,bytes(buf)));so=offi;buf=bytearray([val])
 po=offi
runs.append((so,bytes(buf)));outips=bytearray(b'PATCH')
for offi,d in runs:outips+=offi.to_bytes(3,'big')+len(d).to_bytes(2,'big')+d
outips+=b'EOF';EO=R/'05_build/fix7_exefs';EO.mkdir(parents=True,exist_ok=True);ip=EO/'CF38595316BAA425E792CE5CD122DFC6.ips';ip.write_bytes(outips)
irep={'base_fix6_sha256':hashlib.sha256(ib).hexdigest().upper(),'prompt_replacements':prompt_rep,'records':len(runs),'size':len(outips),'sha256':hashlib.sha256(outips).hexdigest().upper()}
(EO/'fix7_ips_build_report.json').write_text(json.dumps(irep,ensure_ascii=False,indent=2),encoding='utf-8');print('IPS',json.dumps(irep,ensure_ascii=False))
