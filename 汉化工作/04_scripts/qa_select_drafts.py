from pathlib import Path
import csv,re,collections,json
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\translated\select_unique_drafts.tsv');O=P.with_name('select_qa_issues.tsv')
rows=list(csv.DictReader(P.open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
KANA=re.compile(r'[ぁ-んァ-ヶ]'); LAT=re.compile(r'[A-Za-z]{2,}'); VAR=re.compile(r'[＊％][Ａ-ＺA-Z]')
allow={'RPG','CG','BGM','TV','OK','NO'};issues=[];st=collections.Counter()
for r in rows:
 z=r['zh_text']; jp=r['jp_text'];ks=[]
 if z.count('$d')!=jp.count('$d'):ks.append('delimiter')
 if '\ufffd' in z or any(0xE000<=ord(c)<=0xF8FF for c in z):ks.append('garbage')
 if KANA.search(z):ks.append('kana')
 bad=[w for w in set(LAT.findall(z)) if w.upper() not in allow]
 if bad:ks.append('latin:'+','.join(sorted(bad)[:5]))
 for v in set(VAR.findall(jp)):
  if z.count(v)<jp.count(v):ks.append('var:'+v)
 # each option must not be empty
 if any(not x.strip() for x in z.split('$d')):ks.append('empty-option')
 if ks:
  issues.append({'id':r['id'],'kinds':'|'.join(ks),'jp':jp,'en':r['en_text'],'zh':z});
  for x in ks:st[x.split(':')[0]]+=1
print(json.dumps({'unique':len(rows),'issues':len(issues),'stats':dict(st)},ensure_ascii=False,indent=2))
with O.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['id','kinds','jp','en','zh'],delimiter='\t');w.writeheader();w.writerows(issues)
print(O)
