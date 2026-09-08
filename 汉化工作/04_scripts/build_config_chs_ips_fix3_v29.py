from pathlib import Path
from capstone import *
from capstone.arm64 import *
import re,json,struct,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed'
tb=(D/'text.bin').read_bytes();rb=(D/'rodata.bin').read_bytes();RB=0x1A3000
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM);md.detail=True;md.skipdata=True;ins=list(md.disasm(tb,0))
def cstr(a):
 if not RB<=a<RB+len(rb):return None
 o=a-RB;e=rb.find(b'\0',o,min(len(rb),o+3000))
 if e<0:return None
 try:return rb[o:e].decode('utf-8')
 except:return None
def has_cjk(s):return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') for c in s)
refs={}
for i,x in enumerate(ins):
 if not(0x14F000<=x.address<0x15C000):continue
 if x.mnemonic!='adrp' or len(x.operands)<2 or x.operands[0].type!=ARM64_OP_REG or x.operands[1].type!=ARM64_OP_IMM:continue
 r=x.operands[0].reg;pg=x.operands[1].imm
 for j in range(i+1,min(i+5,len(ins))):
  y=ins[j]
  if y.mnemonic=='add' and len(y.operands)>=3 and y.operands[0].type==ARM64_OP_REG and y.operands[1].type==ARM64_OP_REG and y.operands[0].reg==r and y.operands[1].reg==r and y.operands[2].type==ARM64_OP_IMM:
   a=pg+y.operands[2].imm;s=cstr(a)
   if s and len(re.findall(r'[A-Za-z]',s))>=2 and not has_cjk(s): refs.setdefault(s,{'addr':a,'refs':[]})['refs'].append((x.address,y.address))
   break
# Explicit config UI translation map. Resource identifiers / C++ symbols are intentionally excluded.
T={
'Skip':'快进','Read Only':'仅已读','All':'全部','Center':'中央','Bottom':'底部','Position of Choices':'选项位置','Stop on New Page':'翻页时停止','   Continue   ':'继续','Voice':'语音','Display date':'显示日期','Off':'关','On':'开','Rumble feature':'震动强度','MAX':'最大','MID':'中等','MIN':'最小','OFF':'关闭','Auto-Sleep':'自动休眠','Disable':'禁用','Do not disable':'不禁用',
'【Voice】If you select ❝Continue❞, voice will continue to flow even if you send a page during voice playback.\n$S040$C[606060]（It stops if there is voice on the next page）':'【语音】选择“继续”后，即使在语音播放中翻页，语音也会继续播放。\n$S040$C[606060]（若下一页有语音则停止）',
'【Auto-Sleep】Selecting "Disable" will disable auto-sleep during AUTO MODE and cutscenes that automatically progress such as movies and Music Mode (during music playback).':'【自动休眠】选择“禁用”后，在自动模式、影片及音乐模式播放等自动推进场景中禁用自动休眠。',
'R Button(Skip)':'R键（快进）','While pressed':'按住时','Start/Cancel':'开始/解除','L Button(Rewind)':'L键（快退）','ZR Button (Skip)':'ZR键（快进）','ZL Button (Rewind)':'ZL键（快退）','− Button':'−键','Quick Load':'快速读取','AUTO MODE':'自动模式','Select Language':'切换语言','Cursor Control':'光标移动','Left Stick + Directional Buttons':'左摇杆＋方向键',' Directional Buttons ':'方向键','ZR Button':'ZR键','Rewind':'快退','Press and hold the A Button':'长按A键',' for AUTO MODE':'进入自动模式','1.5 sec':'1.5秒','2.5 sec':'2.5秒','1 sec':'1秒','2 sec':'2秒','3 sec':'3秒','Jump (forward)':'跳转（前进）','Forward Once':'前进一次','Right Stick (Right)':'右摇杆（右）','Right Stick (Left)':'右摇杆（左）','Rewind Once':'后退一次','Jump (backward)':'跳转（后退）','Joy-Con Rumble':'Joy-Con震动','  Both  ':'两者','Joy-Con(L)':'Joy-Con(L)','Joy-Con(R)':'Joy-Con(R)',
'Adjust the settings for when you detach the Joy-Con from the console.':'设置将Joy-Con从主机取下时的操作。',
"The ZR Button's Skip will be set to the ZR Button for Button1.\n$C[AD002D]The current setting is (While pressed).":'【ZR键】快进同“按键1”的ZR键设置。\n$C[AD002D]当前：按住时。',
"The ZR Button's Skip will be set to the ZR Button for Button1.\n$C[AD002D]The current setting is (Start/Cancel).":'【ZR键】快进同“按键1”的ZR键设置。\n$C[AD002D]当前：开始/解除。',
"The ZR Button's Skip will be set to the ZR Button for Button1.\n$C[AD002D]The current setting is (Disable).":'【ZR键】快进同“按键1”的ZR键设置。\n$C[AD002D]当前：禁用。',
"The ZR Button's Rewind will be set to the L Button for Button1.\n$C[AD002D]The current setting is (While pressed).":'【ZR键】快退同“按键1”的L键设置。\n$C[AD002D]当前：按住时。',
"The ZR Button's Rewind will be set to the L Button for Button1.\n$C[AD002D]The current setting is (Start/Cancel).":'【ZR键】快退同“按键1”的L键设置。\n$C[AD002D]当前：开始/解除。',
'Jump Forward':'向前跳转','Jump Back':'向后跳转','Hide Window':'隐藏窗口','Two finger tap':'双指轻触',
'Drag in the message window to Skip.\nAuto skip by swiping (unlock by tapping).':'在消息窗口内拖动可快进。\n滑动自动快进（轻触解除）。',
'Drag in the message window to Rewind.\nAuto rewind by swiping (unlock by tapping).':'在消息窗口内拖动可快退。\n滑动可自动快退（轻触解除）。',
'Swipe outside the message window jumps to next choice or chapter, or the end of previously read text.':'在消息窗口外滑动，可跳至下一个选项/章节或已读部分末尾。',
'Swipe outside the message window to jump to previous choice or chapter.':'在消息窗口外滑动，可跳至上一个选项/章节。',
'Swipe outside the message window jumps to next choice, or the end of previously read text.':'在消息窗口外滑动，可跳至下一个选项或已读部分末尾。',
'Swipe outside the message window to jump to previous choice.':'在消息窗口外滑动，可跳至上一个选项。',
'Swipe outside the message window jumps to next chapter, or the end of previously read text.':'在消息窗口外滑动，可跳至下一章节或已读部分末尾。',
'Swipe outside the message window to jump to previous chapter.':'在消息窗口外滑动，可跳至上一章节。',
'Language':'语言','English':'简体中文','Français':'法语','Font':'字体','Gothic1':'黑体','Gothic2':'圆黑体','Gothic3':'粗圆黑体','Mincho':'明朝体','Modern':'现代体','Window\u3000\u3000\u3000\u3000\u3000':'窗口','\u3000\u3000Transparency':'透明度','Color of Read Text':'已读文字颜色','Only choices':'仅选项','Dangopedia Keyword':'团子百科关键词','Green':'绿','Color':'颜色','Purple':'紫','Yellow':'黄','Blue':'蓝','Red':'红',
'【Wait Time Per Character】In auto mode, this sets the wait time until the next message is displayed based on the number of characters in text.':'【每字等待时间】自动模式下，根据文本字数设置显示下一条消息前的等待时间。',
'【Base Wait Time】You can set a Base Wait Time to add to ❝Wait Time Per Character❞.':'【基础等待时间】可在“每字等待时间”之外追加固定等待时间。',
'Text Speed':'文字速度','Slow':'慢','Fast':'快','Wait Time\u3000  \u3000':'等待时间','  \u3000Per Character':'每字','0 sec/char':'0秒/字','0.1 sec/char':'0.1秒/字','Base Wait Time':'基础等待时间','0 sec':'0秒','Master Volume':'主音量','BGM':'BGM','SFX':'音效','System sounds':'系统音效','Voice output':'语音输出','Surround sound(5.1ch)':'环绕声(5.1ch)','Sound source':'音源','Stereo sound(2ch)':'立体声(2ch)','Surround sound is only available in TV mode.':'环绕声仅可在电视模式下使用。',
'Nagisa':'渚','Fuko':'风子','Tomoyo':'智代','Kyou':'杏','Kotomi':'琴美','Yukine':'有纪宁','Ryou':'椋','Misae':'美佐枝','Mei':'芽衣','Kouko':'公子','Sanae':'早苗','Akio':'秋生','Sunohara':'春原','Yoshino':'芳野','Kappei':'胜平','Naoyuki':'直幸','Ushio':'汐','Koumura':'幸村','Botan':'牡丹','Other':'其他','Strong':'强','Weak':'弱','Soft Filter':'柔化滤镜','Color Adjustment':'色彩调整','Custom':'自定义','Saturation':'饱和度','Contrast':'对比度','Red Level':'红色','Green Level':'绿色','Blue Level':'蓝色','Picture quality adjustment of the touch screen on the console.':'调整主机触摸屏的画质。',
'【Soft Filter】Reduces jaggedness and grunge on the screen.':'【柔化滤镜】降低画面的锯齿和杂点。','【Color Adjustment】Adjusts hue on the screen.':'【色彩调整】调整画面色调。','【Saturation】Increases or decreases vividness.':'【饱和度】提高或降低色彩鲜艳度。','【Contrast】Increases or decreases the difference between dark and light.':'【对比度】调整画面的明暗差异。','【Red Level】The picture gets redder if you increase it. If you decrease it, the picture gets bluer.':'【红色】数值越高画面越偏红，越低越偏蓝。','【Green Level】The picture gets greener if you increase it. If you decrease it, the picture gets pinker.':'【绿色】数值越高画面越偏绿，越低越偏粉。','【Blue Level】The picture gets bluer if you increase it. If you decrease it, the picture gets yellower.':'【蓝色】数值越高画面越偏蓝，越低越偏黄。','This function is not available in TV mode.':'电视模式下无法使用此功能。'
}
exclude={'PARTS/VOICE_ICON'}
ui={s:v for s,v in refs.items() if not s.startswith('ZN4task') and s not in exclude}
missing=sorted(set(ui)-set(T)); extra=sorted(set(T)-set(ui))
print('UI',len(ui),'T',len(T),'MISSING',missing,'EXTRA',extra)
assert not missing
# allocate own slots first, then overflow translations into leftover bytes after own in-place translation.
placements={};writes=[];free=[];overflow=[]
for s,v in sorted(ui.items(),key=lambda kv:kv[1]['addr']):
 tr=T[s].encode('utf-8')+b'\0'; cap=len(s.encode('utf-8'))+1; a=v['addr']
 if len(tr)<=cap:
  placements[s]=a; writes.append((a,tr,s,'own'))
  if cap-len(tr)>=4: free.append([a+len(tr),cap-len(tr),s])
 else: overflow.append((s,tr))
# best-fit free ranges, allowing multiple strings in one donor tail
for s,tr in sorted(overflow,key=lambda x:len(x[1]),reverse=True):
 cand=[(sz,i) for i,(a,sz,d) in enumerate(free) if sz>=len(tr)]
 if not cand: raise RuntimeError(f'no pool for {s!r} need {len(tr)}')
 _,i=min(cand);a,sz,d=free[i];placements[s]=a;writes.append((a,tr,s,'overflow:'+d));free[i]=[a+len(tr),sz-len(tr),d]
# encode code pointer redirects only where placement moved away from original address
def enc_adrp(pc,target,rd):
 imm=((target&~0xfff)-(pc&~0xfff))>>12
 if not(-(1<<20)<=imm<(1<<20)):raise ValueError('adrp range')
 u=imm&((1<<21)-1);return 0x90000000|((u&3)<<29)|((u>>2)<<5)|rd
def enc_add(target,rd):return 0x91000000|((target&0xfff)<<10)|(rd<<5)|rd
codepatch=[]
for s,v in ui.items():
 na=placements[s]
 if na==v['addr']:continue
 for aa,ab in v['refs']:
  x=list(md.disasm(tb[aa:aa+4],aa))[0];rd=x.operands[0].reg-ARM64_REG_X0
  # capstone enum x0..x28 is contiguous on this build; verify name explicitly
  name=md.reg_name(x.operands[0].reg);assert name.startswith('x');rd=int(name[1:])
  w1=enc_adrp(aa,na,rd);w2=enc_add(na,rd);b1=w1.to_bytes(4,'little');b2=w2.to_bytes(4,'little')
  q1=list(md.disasm(b1,aa))[0];q2=list(md.disasm(b2,ab))[0]
  # reconstruct target from decoded operands
  assert q1.mnemonic=='adrp' and q2.mnemonic=='add'
  got=q1.operands[1].imm+q2.operands[2].imm;assert got==na,(s,hex(got),hex(na),q1.op_str,q2.op_str)
  codepatch += [(aa,b1,f'{s}:adrp'),(ab,b2,f'{s}:add')]
# validate writes non-overlap and in rodata ranges
wr=sorted(writes);last=0
for a,b,s,k in wr:
 assert RB<=a and a+len(b)<=RB+len(rb)
 assert a>=last,(hex(a),hex(last),s);last=a+len(b)
# IPS records: offset = mapped NSO offset + 0x100 per Atmosphere exefs patch convention.
records=[]
for a,b,s,k in writes:records.append((a+0x100,b,f'str:{s}'))
for a,b,n in codepatch:records.append((a+0x100,b,'code:'+n))
records.sort(key=lambda x:x[0])
# merge only exactly contiguous records; avoid duplicate/overlap
merged=[]
for off,b,n in records:
 if merged and off==merged[-1][0]+len(merged[-1][1]): merged[-1]=(merged[-1][0],merged[-1][1]+b,merged[-1][2]+'|'+n)
 else:
  if merged and off<merged[-1][0]+len(merged[-1][1]):raise RuntimeError(('record overlap',hex(off),n,hex(merged[-1][0]),merged[-1][2]))
  merged.append((off,b,n))
out=bytearray(b'PATCH')
for off,b,n in merged:
 assert off<0x1000000 and len(b)<=0xffff
 out+=off.to_bytes(3,'big')+len(b).to_bytes(2,'big')+b
out+=b'EOF'
O=R/'05_build/fix3_exefs';O.mkdir(parents=True,exist_ok=True);ips=O/'config_chs_v1.ips';ips.write_bytes(out)
rep={'ui_strings':len(ui),'in_place':len(ui)-len(overflow),'overflow':len(overflow),'string_writes':len(writes),'code_instruction_writes':len(codepatch),'ips_records':len(merged),'ips_size':len(out),'ips_sha256':hashlib.sha256(out).hexdigest().upper(),'placements':{s:{'old':hex(ui[s]['addr']),'new':hex(placements[s]),'zh':T[s],'moved':placements[s]!=ui[s]['addr']} for s in sorted(ui)},'free_tail_bytes':sum(x[1] for x in free)}
(O/'config_chs_v1_report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in rep.items() if k!='placements'},ensure_ascii=False,indent=2))
print('IPS',ips)
for s in sorted(ui):
 if placements[s]!=ui[s]['addr']:print('REDIRECT',repr(s),'->',repr(T[s]),hex(ui[s]['addr']),'to',hex(placements[s]),'refs',len(ui[s]['refs']))
