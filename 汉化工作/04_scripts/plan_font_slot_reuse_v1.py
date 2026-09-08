from pathlib import Path
import csv,struct,json,re,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
INFO=ROOT/'03_text/switch_work/paks/FONT.PAK_unpacked/info24'
MSG=ROOT/'03_text/switch_extracted/switch_messages.tsv'
SEL=ROOT/'03_text/switch_extracted/switch_selects.tsv'
TM=ROOT/'03_text/translated/message_targets_complete_v12.tsv'
TS=ROOT/'03_text/translated/select_targets_complete_v2.tsv'
UNPACK=ROOT/'03_text/switch_work/script_probe/SCRIPT.PAK_unpacked'
def rows(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def parse_info(p):
 b=p.read_bytes();fs,bs,third=struct.unpack_from('<HHH',b,0)
 if third==100:cnt=struct.unpack_from('<H',b,6)[0];head=8
 else:cnt=third;head=6
 pos=head+cnt*3; idx_to=['\0']*cnt
 for cp in range(65536):
  idx=struct.unpack_from('<H',b,pos+2*cp)[0]
  if idx<cnt and (idx!=0 or cp==32): idx_to[idx]=chr(cp)
 return fs,bs,cnt,idx_to
fs,bs,cnt,idx_to=parse_info(INFO)
# preserve all literal script JP+EN and final ZH
used=set()
for r in rows(MSG): used.update(r['jp_text']); used.update(r['en_text'])
for r in rows(SEL): used.update(r['jp_text']); used.update(r['en_text'])
zh=''.join(r['zh_text'] for r in rows(TM))+''.join(r['zh_text'] for r in rows(TS))
req=set(c for c in zh if ord(c)>=128)
# conservative: preserve all kana, ASCII/fullwidth punctuation blocks and chars that appear as UTF16LE code units anywhere in every script file
for cp in range(0x20,0x100): used.add(chr(cp))
for cp in range(0x3000,0x3100): used.add(chr(cp))
for cp in range(0x3040,0x3100): used.add(chr(cp))
for cp in range(0xFF00,0xFFF0): used.add(chr(cp))
raws=[p.read_bytes() for p in UNPACK.glob('*') if p.is_file()]
# only high-index candidate chars are raw-scanned to reduce work
raw_seen=set()
for ch in idx_to[max(0,cnt-2500):]:
 if not ch or ch=='\0':continue
 pat=ch.encode('utf-16le')
 if any(pat in b for b in raws): raw_seen.add(ch)
used |= raw_seen
missing=sorted(req-set(idx_to),key=ord)
# candidate slots: highest indexes first, mapped char not needed, not NUL; prefer CJK chars over symbols
cand=[]
for i in range(cnt-1,0,-1):
 ch=idx_to[i]
 if not ch or ch=='\0' or ch in used or ch in req: continue
 cand.append((i,ch))
selected=cand[:len(missing)]
print(json.dumps({'font_size':fs,'block_size':bs,'char_num':cnt,'required_nonascii':len(req),'missing':len(missing),'used_chars':len(used),'raw_seen_high':len(raw_seen),'candidates':len(cand),'selected':len(selected),'selected_min_index':min((i for i,_ in selected),default=None),'selected_max_index':max((i for i,_ in selected),default=None),'selected_old_preview':''.join(ch for _,ch in selected[:120]),'missing_preview':''.join(missing[:120])},ensure_ascii=False,indent=2))
out=ROOT/'05_build/font_patch_plan';out.mkdir(parents=True,exist_ok=True)
(out/'missing_chars.txt').write_text(''.join(missing),encoding='utf-8')
with (out/'slot_map.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['index','old_char','new_char','old_cp','new_cp'])
 for (i,old),new in zip(selected,missing):w.writerow([i,old,new,f'U+{ord(old):04X}',f'U+{ord(new):04X}'])
(out/'summary.json').write_text(json.dumps({'missing_count':len(missing),'candidate_count':len(cand),'selected_count':len(selected),'selected_min_index':min((i for i,_ in selected),default=None),'selected_max_index':max((i for i,_ in selected),default=None)},ensure_ascii=False,indent=2),encoding='utf-8')
if len(selected)<len(missing): raise SystemExit(2)
