from pathlib import Path
import csv,re,json,time
from argostranslate import translate
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
D=ROOT/'03_text/translated/manual_batches_v11'
# protect controls, variables, literal newlines and recurring proper names before translation
names={
'Fuko-chan':'小风','Fu-chan':'小风','Fuko':'风子','Sunohara':'春原','Nagisa':'渚','Furukawa':'古河','Tomoyo':'智代','Kyou':'杏','Ryou':'椋','Sanae':'早苗','Akio':'秋生','Kouko':'公子','Yusuke':'祐介','Yoshino':'芳野','Misae':'美佐枝','Ibuki':'伊吹','Mei':'芽衣','Kappei':'胜平','Yukine':'有纪宁','Kotomi':'琴美','Koumura':'幸村','Botan':'牡丹','Sakagami':'坂上','Fujibayashi':'藤林','Miyazawa':'宫泽'
}
# Longest names first
name_pat='|'.join(re.escape(x) for x in sorted(names,key=len,reverse=True))
PROT=re.compile(r'(\\n|\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|\$d|[＊％][Ａ-ＺA-Z]|'+name_pat+r')')
cache={}
def trans_seg(s):
    if not s or not re.search(r'[A-Za-z]',s): return s
    if s in cache:return cache[s]
    try:z=translate.translate(s,'en','zh')
    except Exception:z=s
    cache[s]=z;return z

def tr(en):
    if en.startswith('`') and '@' in en: en=en.split('@',1)[1]
    # normalize honorific suffixes on player variables before split
    en=re.sub(r'([＊％][Ａ-ＺA-Z])-(?:san|kun|chan|sensei)',r'\1',en,flags=re.I)
    parts=[];pos=0
    for m in PROT.finditer(en):
        parts.append(trans_seg(en[pos:m.start()]))
        tok=m.group(0);parts.append(names.get(tok,tok));pos=m.end()
    parts.append(trans_seg(en[pos:]))
    z=''.join(parts)
    z=z.replace('“','「').replace('”','」').replace('❝','「').replace('❞','」')
    z=z.replace('...', '…')
    return z.strip()
for n in range(8,25):
    src=D/f'source_{n:02d}.tsv';out=D/f'draft_{n:02d}.tsv'
    rows=list(csv.DictReader(src.open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
    got=[]
    for r in rows:
        got.append({'scene':r['scene'],'code_index':r['code_index'],'zh_body':tr(r['en_text'])})
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['scene','code_index','zh_body'],delimiter='\t');w.writeheader();w.writerows(got)
    print(f'batch {n:02d}: {len(got)}',flush=True)
(ROOT/'03_text/translated/argos_cache_summary.json').write_text(json.dumps({'segments':len(cache)},ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE segments',len(cache),flush=True)
