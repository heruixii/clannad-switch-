from pathlib import Path
import csv,re,json,collections
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\translated\select_targets_complete_v2.tsv')
rows=list(csv.DictReader(P.open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
KANA=re.compile(r'[ぁ-んァ-ヶ]'); VAR=re.compile(r'[＊％][Ａ-ＺA-Z]');LAT=re.compile(r'[A-Za-z]{2,}')
allow={'RPG','CG','BGM','TV','OK','NO'};issues=[];st=collections.Counter()
for r in rows:
 jp,z=r['jp_text'],r['zh_text'];ks=[]
 if z.count('$d')!=jp.count('$d'):ks.append('delimiter')
 if '\ufffd' in z or any(0xE000<=ord(c)<=0xF8FF for c in z):ks.append('garbage')
 if KANA.search(z):ks.append('kana')
 for v in set(VAR.findall(jp)):
  if z.count(v)<jp.count(v):ks.append('var:'+v)
 bad=[w for w in set(LAT.findall(z)) if w.upper() not in allow]
 if bad:ks.append('latin:'+','.join(sorted(bad)))
 if any(not x.strip() for x in z.split('$d')):ks.append('empty')
 if ks:
  issues.append((r,ks));[st.update([x.split(':')[0]]) for x in ks]
print(json.dumps({'rows':len(rows),'issues':len(issues),'stats':dict(st),'sources':dict(collections.Counter(r['source'] for r in rows))},ensure_ascii=False,indent=2))
for r,ks in issues[:100]:print(r['scene'],r['code_index'],ks,'JP=',r['jp_text'],'ZH=',r['zh_text'])
