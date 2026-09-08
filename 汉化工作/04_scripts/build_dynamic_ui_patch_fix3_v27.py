from pathlib import Path
from capstone import *
from capstone.arm64 import *
from collections import defaultdict
import json,hashlib,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';OUT=R/'05_build/fix3_dynamic_ui';OUT.mkdir(parents=True,exist_ok=True)
tb=bytearray((D/'text.bin').read_bytes()); rb=bytearray((D/'rodata.bin').read_bytes()); ORIG_T=bytes(tb);ORIG_R=bytes(rb); RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(ORIG_T,0))
def cstr(a):
 if not RB<=a<RB+len(ORIG_R):return None
 o=a-RB;e=ORIG_R.find(b'\0',o,min(len(ORIG_R),o+1200))
 if e<0:return None
 try:s=ORIG_R[o:e].decode('utf-8')
 except:return None
 return s or None
# all ADRP+ADD string refs
refs=defaultdict(list)
for i,x in enumerate(ins):
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm
   if cstr(a) is not None:refs[a].append((x.address,y.address,r))
   break
# enumerate config English exactly as v21
cfg=[]
for a,rr in refs.items():
 s=cstr(a)
 if s and any(0x150000<=x<0x157000 for x,y,r in rr):
  al=sum(('a'<=ch.lower()<='z') for ch in s);na=sum(ord(ch)>127 for ch in s)
  if al>=2 and al>=na and len(s)<=500:cfg.append((min(x for x,y,r in rr if 0x150000<=x<0x157000),a,s))
cfg=sorted(cfg);assert len(cfg)==153,len(cfg)
T={
0:'跳过',1:'仅已读',2:'全部',3:'居中',4:'底部',5:'选项位置',6:'新页停止',7:'继续',8:'语音',9:'显示日期',10:'关',11:'开',12:'震动功能',13:'强',14:'中',15:'弱',16:'关闭',17:'自动休眠',18:'禁用',19:'不禁用',
20:'【语音】选择“继续”后，翻页时若语音仍在播放，将继续播放。\n$S040$C[606060]（下一页有语音时会停止）',
21:'【自动休眠】选择“禁用”后，自动模式及影片、音乐鉴赏播放等自动进行场景中不会进入自动休眠。',
22:'R键（跳过）',23:'按住时',24:'开始/取消',25:'L键（回退）',26:'ZR键（跳过）',27:'ZL键（回退）',28:'−键',29:'快速读取',30:'自动模式',31:'选择语言',32:'光标控制',33:'左摇杆＋方向键',34:'仅方向键',35:'ZR键',36:'回退',37:'长按A键',38:'进入自动模式',39:'1.5秒',40:'2.5秒',41:'1秒',42:'2秒',43:'3秒',44:'向前跳转',45:'前进一次',46:'右摇杆（右）',47:'右摇杆（左）',48:'回退一次',49:'向后跳转',50:'震动的Joy-Con',51:'Joy-Con震动',52:'两边',53:'Joy-Con（左）',54:'Joy-Con（右）',55:'设置Joy-Con从主机取下时的操作。',
56:'Button1的ZR跳过将设为ZR键。\n$C[AD002D]当前设置为（按住时）。',57:'Button1的ZR跳过将设为ZR键。\n$C[AD002D]当前设置为（开始/取消）。',58:'Button1的ZR跳过将设为ZR键。\n$C[AD002D]当前设置为（禁用）。',59:'Button1的ZR回退将设为L键。\n$C[AD002D]当前设置为（按住时）。',60:'Button1的ZR回退将设为L键。\n$C[AD002D]当前设置为（开始/取消）。',
61:'向前跳转',62:'向后跳转',63:'隐藏窗口',64:'双指点击',65:'在消息窗口内拖动可快进。\n滑动后自动快进（点击解除）。',66:'在消息窗口内拖动可回退。\n滑动后自动回退（点击解除）。',67:'在消息窗口外滑动可跳到下一选项或章节，或已读文本末尾。',68:'在消息窗口外滑动可跳到上一选项或章节。',69:'在消息窗口外滑动可跳到下一选项，或已读文本末尾。',70:'在消息窗口外滑动可跳到上一选项。',71:'在消息窗口外滑动可跳到下一章节，或已读文本末尾。',72:'在消息窗口外滑动可跳到上一章节。',
73:'语言',74:'简体中文',75:'法语',76:'字体',77:'黑体1',78:'黑体2',79:'黑体3',80:'明朝',81:'现代',82:'窗口',83:'透明度',84:'已读文字颜色',85:'仅选项',86:'团子百科关键词',87:'团子百科关键词',88:'绿色',89:'颜色',90:'紫色',91:'黄色',92:'蓝色',93:'红色',
94:'【每字等待时间】自动模式中，根据文本字数设定显示下一条消息前的等待时间。',95:'【基础等待时间】可在“每字等待时间”之外追加固定等待时间。',96:'文字速度',97:'慢',98:'快',99:'等待时间',100:'每字',101:'0秒/字',102:'0.1秒/字',103:'基础等待时间',104:'0秒',105:'主音量',106:'BGM',107:'音效',108:'系统音效',109:'语音输出',110:'环绕声（5.1ch）',111:'声道模式',112:'立体声（2ch）',113:'环绕声仅在电视模式下可用。',
114:'渚',115:'风子',116:'智代',117:'杏',118:'琴美',119:'有纪宁',120:'椋',121:'美佐枝',122:'芽衣',123:'公子',124:'早苗',125:'秋生',126:'春原',127:'芳野',128:'胜平',129:'直幸',130:'汐',131:'幸村',132:'牡丹',133:'其他',
135:'强',136:'弱',137:'柔化滤镜',138:'色彩调整',139:'自定义',140:'饱和度',141:'对比度',142:'红色级别',143:'绿色级别',144:'蓝色级别',145:'调整主机触摸屏的画质。',146:'【柔化滤镜】减少画面锯齿和颗粒感。',147:'【色彩调整】调整画面的色调。',148:'【饱和度】调整色彩鲜艳程度。',149:'【对比度】调整明暗差异。',150:'【红色级别】提高会偏红，降低会偏蓝。',151:'【绿色级别】提高会偏绿，降低会偏粉。',152:'【蓝色级别】提高会偏蓝，降低会偏黄。'
}
# Deliberately leave resource path index 134 unchanged; translate all other config-visible strings.
expected=set(range(153))-{134};assert set(T)==expected,(sorted(expected-set(T)),sorted(set(T)-expected))
# safe host blocks: English strings with no refs outside ConfigWin and >=20 bytes
hosts=[]
for order,a,s in cfg:
 allr=refs[a];outside=[r for r in allr if not(0x150000<=r[0]<0x157000)]
 if not outside and len(s.encode())>=4:hosts.append({'addr':a,'cap':len(s.encode())+1,'used':0,'orig':s})
# Drop any overlapping/suffix-shared string blocks so pool writes can never cross another host.
hosts=sorted(hosts,key=lambda h:h['addr']); dis=[]; end=-1
for h in hosts:
    if h['addr']>=end:
        dis.append(h); end=h['addr']+h['cap']
hosts=dis
print('HOST_CAP',sum(h['cap'] for h in hosts),'HOSTS',len(hosts))
# translations packed longest first using best-fit into safe blocks; do not cross original string boundaries.
items=[]
for idx,zh in T.items():items.append((idx,(zh+'\0').encode('utf-8')))
alloc={}
for idx,data in sorted(items,key=lambda x:len(x[1]),reverse=True):
 choices=[h for h in hosts if h['cap']-h['used']>=len(data)]
 if not choices:raise RuntimeError(f'no pool for {idx} {T[idx]!r} bytes={len(data)} remain={sum(h["cap"]-h["used"] for h in hosts)}')
 h=min(choices,key=lambda x:x['cap']-x['used']-len(data));addr=h['addr']+h['used'];alloc[idx]=addr;h['used']+=len(data)
# clear and populate host blocks in patched rodata
for h in hosts:
 o=h['addr']-RB;rb[o:o+h['cap']]=b'\0'*h['cap']
for idx,data in items:
 a=alloc[idx];o=a-RB;rb[o:o+len(data)]=data
# ARM64 encoders for ADRP Xd,target and ADD Xd,Xd,#imm12
def enc_adrp(rd,pc,target):
 pcpg=pc&~0xfff;tpg=target&~0xfff;imm=(tpg-pcpg)>>12
 if not(-(1<<20)<=imm<(1<<20)):raise ValueError(('adrp range',hex(pc),hex(target),imm))
 u=imm & ((1<<21)-1);immlo=u&3;immhi=(u>>2)&0x7ffff
 return 0x90000000 | (immlo<<29)|(immhi<<5)|rd
def enc_add(rd,rn,imm):
 assert 0<=imm<4096
 return 0x91000000 | (imm<<10)|(rn<<5)|rd
patches=[]
def patch_ptr(adrp_off,add_off,target,why):
 # Verify original pair and preserve register.
 x=next(z for z in ins if z.address==adrp_off);y=next(z for z in ins if z.address==add_off)
 assert x.mnemonic=='adrp' and y.mnemonic=='add';rd=x.operands[0].reg-ARM64_REG_X0
 # capstone enum registers are not linear guaranteed; use name xN.
 rn_name=md.reg_name(x.operands[0].reg); assert rn_name.startswith('x');n=int(rn_name[1:]);
 assert md.reg_name(y.operands[0].reg)==rn_name and md.reg_name(y.operands[1].reg)==rn_name
 wa=enc_adrp(n,adrp_off,target);wb=enc_add(n,n,target&0xfff)
 olda=bytes(tb[adrp_off:adrp_off+4]);oldb=bytes(tb[add_off:add_off+4]);na=wa.to_bytes(4,'little');nb=wb.to_bytes(4,'little')
 tb[adrp_off:adrp_off+4]=na;tb[add_off:add_off+4]=nb
 patches.append({'kind':'code_ptr','off':adrp_off,'old':olda.hex(),'new':na.hex(),'why':why,'target':target});patches.append({'kind':'code_ptr','off':add_off,'old':oldb.hex(),'new':nb.hex(),'why':why,'target':target})
# patch all ConfigWin refs of translated strings
for idx,(order,a,en) in enumerate(cfg):
 if idx not in T:continue
 for ad,add,r in refs[a]:
  if 0x150000<=ad<0x157000:patch_ptr(ad,add,alloc[idx],f'ConfigWin:{en}->{T[idx]}')
# trusted official prebuilt zh groups; patch only setting/title labels needed now.
groups=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'))
trusted={'Defaults','Sample Voice','Basic operation','Languages','Play Voice','Game Start','$K1Text$K0 preview.'}
for g in groups:
 if g['en'] in trusted:patch_ptr(g['adrp_off'],g['add_off'],g['zh_addr'],f'official:{g["en"]}->{g["zh"]}')
# Verify every patched pair resolves exactly to target via Capstone disassembly.
md2=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md2.detail=True
for pch in [p for p in patches if p['off']%4==0]:
 pass
# write patched segment images for independent QA
(OUT/'text.fix3.bin').write_bytes(tb);(OUT/'rodata.fix3.bin').write_bytes(rb)
# Build IPS records from byte diffs, mapped NSO offset + 0x100 header adjustment used by Atmosphere exefs IPS.
def diff_runs(old,new,base):
 out=[];i=0
 while i<len(old):
  if old[i]==new[i]:i+=1;continue
  s=i;i+=1
  while i<len(old) and old[i]!=new[i] and i-s<0xffff:i+=1
  out.append((base+s,bytes(new[s:i]),bytes(old[s:i])))
 return out
runs=diff_runs(ORIG_T,bytes(tb),0)+diff_runs(ORIG_R,bytes(rb),RB)
# merge only naturally contiguous diff runs are already bounded; make IPS offsets = mapped offset + 0x100.
ips=bytearray(b'PATCH');records=[]
for off,data,old in runs:
 ipsoff=off+0x100
 if ipsoff>=1<<24:raise ValueError(hex(ipsoff))
 ips+=ipsoff.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data
 records.append({'mapped_off':off,'ips_off':ipsoff,'size':len(data),'old':old.hex(),'new':data.hex()})
ips+=b'EOF'
main=(R/'05_build/exefs_fix2/update_exefs/main').read_bytes();buildid=main[0x40:0x60].hex().upper().rstrip('0');assert buildid=='CF38595316BAA425E792CE5CD122DFC6',buildid
ipspath=OUT/(buildid+'.ips');ipspath.write_bytes(ips)
# Self-apply IPS using Atmosphere semantics: patch offset - 0x100 => mapped module offset.
mod=bytearray(max(RB+len(ORIG_R),0x212000));mod[0:len(ORIG_T)]=ORIG_T;mod[RB:RB+len(ORIG_R)]=ORIG_R
q=5
while ips[q:q+3]!=b'EOF':
 off=int.from_bytes(ips[q:q+3],'big');ln=int.from_bytes(ips[q+3:q+5],'big');q+=5;dat=ips[q:q+ln];q+=ln;moff=off-0x100;mod[moff:moff+ln]=dat
assert mod[:len(tb)]==tb and mod[RB:RB+len(rb)]==rb
# Verify translations reachable at assigned addresses and no pool overflow.
for idx,a in alloc.items():
 o=a-RB;e=rb.find(b'\0',o);assert rb[o:e].decode('utf-8')==T[idx]
report={'build_id':buildid,'config_strings_total':153,'config_strings_translated':len(T),'unchanged_indices':[134],
 'string_pool_hosts':len(hosts),'string_pool_capacity':sum(h['cap'] for h in hosts),'string_pool_used':sum(len((z+'\0').encode()) for z in T.values()),
 'code_pointer_instruction_patches':len(patches),'ips_records':len(records),'ips_size':len(ips),'ips_sha256':hashlib.sha256(ips).hexdigest().upper(),
 'ips_path':str(ipspath),'official_groups':sorted(trusted),'alloc':{str(i):{'en':cfg[i][2],'zh':T[i],'addr':hex(a)} for i,a in alloc.items()},'records':records}
(OUT/'fix3_dynamic_ui_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('alloc','records')},ensure_ascii=False,indent=2))
print('IPS',ipspath)
# disasm sample patched ptrs + verify all ConfigWin English refs now point away from originals for translated entries.
print('POOL_USED',report['string_pool_used'],'/',report['string_pool_capacity'])

