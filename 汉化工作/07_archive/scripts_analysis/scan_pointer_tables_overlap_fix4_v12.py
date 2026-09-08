from pathlib import Path
import json,struct
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=R/'05_build/exefs_fix2/update_exefs/main_decompressed';rb=(D/'rodata.bin').read_bytes();db=(D/'data.bin').read_bytes();RB=0x1A3000;DB=0x212000
G=json.loads((D/'ui_lang_pointer_groups_v51.json').read_text(encoding='utf-8'));cfg=json.loads((R/'05_build/fix3_exefs/config_chs_v1_report.json').read_text(encoding='utf-8'))['placements']
items=[]
for s,v in cfg.items():
 if v['moved']:items.append(('cfg',s,int(v['old'],16),int(v['new'],16)))
for g in G:
 t=0x1e51f4 if g['en']=='Delete' else g['zh_addr'];items.append(('sys',g['en'],g['en_addr'],t))
for typ,s,old,new in items:
 pat=struct.pack('<Q',old);hits=[]
 for nm,b,base in [('rodata',rb,RB),('data',db,DB)]:
  st=0
  while True:
   o=b.find(pat,st)
   if o<0:break
   hits.append((nm,base+o));st=o+1
 if hits:print(typ,repr(s),hex(old),'->',hex(new),'qrefs',[(n,hex(a)) for n,a in hits])
