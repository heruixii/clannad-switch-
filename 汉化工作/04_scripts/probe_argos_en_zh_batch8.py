import csv,re
from pathlib import Path
from argostranslate import translate
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\translated\manual_batches_v11\source_08.tsv')
rows=list(csv.DictReader(p.open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))[:30]
# protect variables/controls and strip switch speaker prefix in English
pat=re.compile(r'(\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|[＊％][Ａ-ＺA-Z]|\$d|\\n)')
for r in rows:
    en=r['en_text']
    if en.startswith('`') and '@' in en: en=en.split('@',1)[1]
    toks=[]
    def sub(m):
        toks.append(m.group(0)); return f'ZXQ{len(toks)-1}QXZ'
    x=pat.sub(sub,en)
    z=translate.translate(x,'en','zh')
    for i,t in enumerate(toks): z=z.replace(f'ZXQ{i}QXZ',t)
    print(r['scene'],r['code_index'],'EN=',en,'ZH=',z,sep='\t')
