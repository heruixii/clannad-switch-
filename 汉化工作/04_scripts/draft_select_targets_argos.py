from pathlib import Path
import csv,re,collections,json
from argostranslate import translate
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); S=ROOT/'03_text/switch_extracted/switch_selects.tsv'; U=ROOT/'03_text/translated/select_unique_drafts.tsv'; O=ROOT/'03_text/translated/select_targets_draft.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
names={'Fuko-chan':'小风','Fu-chan':'小风','Fuko':'风子','Sunohara':'春原','Nagisa':'渚','Furukawa':'古河','Tomoyo':'智代','Kyou':'杏','Ryou':'椋','Sanae':'早苗','Akio':'秋生','Kouko':'公子','Yusuke':'祐介','Yoshino':'芳野','Misae':'美佐枝','Ibuki':'伊吹','Mei':'芽衣','Kappei':'胜平','Yukine':'有纪宁','Kotomi':'琴美','Koumura':'幸村','Botan':'牡丹'}
name_pat='|'.join(re.escape(x) for x in sorted(names,key=len,reverse=True))
PROT=re.compile(r'([＊％][Ａ-ＺA-Z]|'+name_pat+r')')
cache={}
def trseg(s):
 s=s.strip()
 if not s:return s
 # normalize player honorifics
 s=re.sub(r'([＊％][Ａ-ＺA-Z])-(?:san|kun|chan|sensei)',r'\1',s,flags=re.I)
 parts=[];pos=0
 for m in PROT.finditer(s):
  pre=s[pos:m.start()]
  if pre:
   if pre not in cache:
    try:cache[pre]=translate.translate(pre,'en','zh')
    except Exception:cache[pre]=pre
   parts.append(cache[pre])
  tok=m.group(0);parts.append(names.get(tok,tok));pos=m.end()
 tail=s[pos:]
 if tail:
  if tail not in cache:
   try:cache[tail]=translate.translate(tail,'en','zh')
   except Exception:cache[tail]=tail
  parts.append(cache[tail])
 z=''.join(parts).strip().replace('“','「').replace('”','」').replace('❝','「').replace('❞','」')
 return z
rows=rd(S); seen={}; unique=[]
for r in rows:
 if r['jp_text'] in seen:continue
 ja=r['jp_text'].split('$d'); en=r['en_text'].split('$d')
 if len(ja)!=len(en):raise RuntimeError((r['scene'],r['code_index'],len(ja),len(en),r['jp_text'],r['en_text']))
 zh=[trseg(x) for x in en]
 rec={'id':len(unique)+1,'jp_text':r['jp_text'],'en_text':r['en_text'],'zh_text':'$d'.join(zh),'option_count':len(ja),'first_scene':r['scene'],'first_code_index':r['code_index']}
 unique.append(rec);seen[r['jp_text']]=rec
U.parent.mkdir(parents=True,exist_ok=True)
with U.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(unique[0]),delimiter='\t');w.writeheader();w.writerows(unique)
out=[]
for r in rows:
 x=seen[r['jp_text']];out.append({'scene':r['scene'],'code_index':r['code_index'],'jp_text':r['jp_text'],'en_text':r['en_text'],'zh_text':x['zh_text']})
with O.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'rows':len(rows),'unique':len(unique),'segments':sum(int(x['option_count']) for x in unique),'cache':len(cache)},ensure_ascii=False,indent=2));print(U);print(O)
