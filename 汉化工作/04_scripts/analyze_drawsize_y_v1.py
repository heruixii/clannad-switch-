from pathlib import Path
import struct,csv,collections,statistics
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
def parse(p):
 b=p.read_bytes(); fs,bs,third=struct.unpack_from('<HHH',b,0); cnt=struct.unpack_from('<H',b,6)[0] if third==100 else third; head=8 if third==100 else 6
 ds=[tuple(b[head+i*3:head+i*3+3]) for i in range(cnt)]
 pos=head+cnt*3; idx=['\0']*cnt
 for cp in range(65536):
  i=struct.unpack_from('<H',b,pos+cp*2)[0]
  if i<cnt and (i!=0 or cp==32):idx[i]=chr(cp)
 return fs,bs,cnt,ds,idx
orig=parse(R/'03_text/switch_work/paks/FONT.PAK_unpacked/info24'); new=parse(R/'05_build/font_package/FONT.PAK_unpacked/info24')
for label,x in [('orig',orig),('new',new)]:
 ys=[]
 for i,ch in enumerate(x[4]):
  if ch!='\0' and (0x3000<=ord(ch)<=0x9fff or 0xff00<=ord(ch)<=0xffef): ys.append(x[3][i][2])
 print(label,'Y mode',collections.Counter(ys).most_common(20),'min',min(ys),'max',max(ys))
rows=list(csv.DictReader((R/'05_build/font_patch_plan/slot_map_v2.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
print('new slots y distribution',collections.Counter(new[3][int(r['index'])][2] for r in rows).most_common(30))
print('sample')
for r in rows[:40]:
 i=int(r['index']); print(i,r['new_char'],'origXYW',orig[3][i],'newXYW',new[3][i])
