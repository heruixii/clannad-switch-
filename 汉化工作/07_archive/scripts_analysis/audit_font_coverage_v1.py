from pathlib import Path
import csv,struct,re,json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
F=ROOT/'03_text/switch_work/paks/FONT.PAK_unpacked'
M=ROOT/'03_text/translated/message_targets_complete_v12.tsv';S=ROOT/'03_text/translated/select_targets_complete_v2.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
text=''.join(r['zh_text'] for r in rd(M))+''.join(r['zh_text'] for r in rd(S))
# remove control language, variable markers remain because their displayed names come from runtime, not literal glyph names here.
# Required codepoints = all literal Unicode chars in targets excluding ASCII control syntax chars/Latin letters/digits.
chars=set(text)
# report all non-ASCII, since punctuation/fullwidth variables may render literally too
req={c for c in chars if ord(c)>=0x80 and c not in '\ufeff'}
# variable tokens ＊Ａ etc are literal fullwidth markers in bytecode and need their own glyphs if engine renders them; retain.

def parse_info(p):
 b=p.read_bytes(); fs,fs2,third=struct.unpack_from('<HHH',b,0)
 if third==100: unk=third;cnt=struct.unpack_from('<H',b,6)[0];head=8
 else:unk=0;cnt=third;head=6
 mapoff=head+cnt*3
 assert mapoff+131072<=len(b),(p,len(b),cnt,mapoff)
 cov=set(); idxs={}
 for cp in range(65536):
  idx=struct.unpack_from('<H',b,mapoff+cp*2)[0]
  if idx!=0:
   cov.add(chr(cp));idxs[cp]=idx
 # index0 might legitimately map space; treat based on known fontcount export behavior; all visible glyphs expected nonzero except blank.
 return {'fontsize':fs,'fontsize2':fs2,'unk':unk,'fontcount':cnt,'mapoff':mapoff,'coverage':cov,'idxs':idxs}
infos=[]
for p in sorted(F.glob('info*')):
 d=parse_info(p);miss=sorted(req-d['coverage'],key=ord)
 infos.append({'name':p.name,'fontsize':d['fontsize'],'fontcount':d['fontcount'],'coverage_nonzero':len(d['coverage']),'required_nonascii':len(req),'missing_count':len(miss),'missing':''.join(miss)})
print(json.dumps(infos,ensure_ascii=False,indent=2))
# union/intersection coverage
parsed=[parse_info(p) for p in sorted(F.glob('info*'))]
union=set().union(*(x['coverage'] for x in parsed));inter=set.intersection(*(x['coverage'] for x in parsed)) if parsed else set()
mu=sorted(req-union,key=ord);mi=sorted(req-inter,key=ord)
print('UNION_MISSING',len(mu),''.join(mu));print('INTERSECTION_MISSING',len(mi),''.join(mi))
# character frequency of missing union chars for prioritization
freq=collections.Counter(c for c in text if c in mu)
print('MISSING_FREQ',freq.most_common())
(ROOT/'03_text/translated/font_coverage_v1.json').write_text(json.dumps({'required_nonascii':len(req),'infos':infos,'union_missing':''.join(mu),'intersection_missing':''.join(mi),'missing_freq':freq.most_common()},ensure_ascii=False,indent=2),encoding='utf-8')
