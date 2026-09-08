from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
U=ROOT/'03_text/matched/switch_pc_v10/unmatched.tsv'; T=ROOT/'03_text/translated/message_targets_v10.tsv'; O=ROOT/'03_text/translated/nonlexical_dialogue_v10.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def speaker(s):return s[1:s.find('@')] if s.startswith('`') and '@' in s else ''
def body(s):return s.split('@',1)[1] if s.startswith('`') and '@' in s else s
# learned JP->ZH speaker from already converted targets
spcnt=collections.defaultdict(collections.Counter)
for r in rd(T):
 a=speaker(r['jp_text']);b=speaker(r['zh_text'])
 if a and b:spcnt[a][b]+=1
spmap={a:c.most_common(1)[0][0] for a,c in spcnt.items()}
spmap['％Ｂ']='％Ｂ'
spmap.update({'クラスメイトたち':'同班同学们','勝平・＊Ｂ':'胜平・＊Ｂ','春原・渚':'春原・渚','杏・＊Ｂ':'杏・＊Ｂ','＊Ｂ・杏':'＊Ｂ・杏'})
# lexical JP if kana or CJK ideograph appears outside control/variables; punctuation/Latin/variables are safe
ruby=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]')
ctrl=re.compile(r'\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|[＊％][Ａ-ＺA-Z]|\\[nr]')
def has_jp_lexical(s):
 x=ruby.sub(lambda m:m.group(1),s);x=ctrl.sub('',x)
 # remove quote punctuation; any kana or CJK indicates actual lexical content
 return bool(re.search(r'[\u3040-\u30ff\u3400-\u9fff]',x))
out=[]
for r in rd(U):
 sp=speaker(r['jp_text'])
 if not sp:continue
 b=body(r['jp_text'])
 if has_jp_lexical(b):continue
 zsp=spmap.get(sp,sp)
 out.append({'scene':r['scene'],'code_index':r['code_index'],'source':'nonlexical-dialogue','jp_text':r['jp_text'],'en_text':r['en_text'],'zh_text':'`'+zsp+'@'+b})
with O.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'rows':len(out),'speaker_unmapped':sorted(set(speaker(r['jp_text']) for r in rd(U) if speaker(r['jp_text']) and not has_jp_lexical(body(r['jp_text'])) and speaker(r['jp_text']) not in spmap))},ensure_ascii=False,indent=2));print(O)

