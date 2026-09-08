from pathlib import Path
import csv,struct,json,statistics,unicodedata
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');mp=R/'05_build/font_patch_plan/slot_map_v2.tsv'
rows=list(csv.DictReader(mp.open(encoding='utf-8-sig'),delimiter='\t'));slots=[(int(r['index']),r['old_char'],r['new_char']) for r in rows]

def parse(p):
 b=p.read_bytes();fs,bs,cn=struct.unpack_from('<HHH',b,0);off=6
 if cn==100:
  cn2=struct.unpack_from('<H',b,6)[0];cn=cn2;off=8
 draw=[]
 for i in range(cn):draw.append(struct.unpack_from('<BBB',b,off+i*3))
 off+=cn*3
 ui=struct.unpack_from('<65536H',b,off);off+=65536*2
 us=[]
 for i in range(65536):us.append(struct.unpack_from('<BB',b,off+i*2))
 return fs,bs,cn,draw,ui,us
for name in ['info24','info32','info40','info57']:
 orig=R/'03_text/switch_work/paks/FONT.PAK_unpacked'/name;fix=R/'05_build/font_package_fix2/FONT.PAK_unpacked'/name
 fs,bs,cn,d0,u0,s0=parse(orig);_,_,_,d1,u1,s1=parse(fix)
 nw=[d1[idx][1] for idx,o,n in slots if ord(n)>127 and n not in '·—'];ow=[d0[idx][1] for idx,o,n in slots if ord(n)>127 and n not in '·—']
 # existing mapped CJK ideographs not reclaimed
 ex=[]
 for cp,idx in enumerate(u0):
  if idx and 0x4E00<=cp<=0x9FFF and all(idx!=s[0] for s in slots):ex.append(d0[idx][1])
 print('\n',name,'font',fs,'newW min/med/max',min(nw),statistics.median(nw),max(nw),'oldslot same?',nw==ow,'existing CJK min/med/max',min(ex),statistics.median(ex),max(ex),'unique new',sorted(set(nw))[:30],'unique existing',sorted(set(ex))[:30])
 print('new too narrow <0.75font',sum(w<fs*.75 for w in nw),'/',len(nw),'existing',sum(w<fs*.75 for w in ex),'/',len(ex))
