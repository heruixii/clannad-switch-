from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');D=ROOT/'03_text/translated/manual_batches_v11'
CTRL=re.compile(r'\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|\$d|\\n|[＊％][Ａ-ＺA-Z]')
LAT=re.compile(r'[A-Za-z]{2,}')
KANA=re.compile(r'[ぁ-んァ-ヶ]')
ALLOW_LAT={'RPG','GAMEOVER','THE','END','You','Are','Dead','COMING','SOON','LET','STAR','START'}
issues=[];stats=collections.Counter();total=0
for n in range(1,25):
 src=list(csv.DictReader((D/f'source_{n:02d}.tsv').open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
 tgt=list(csv.DictReader((D/f'target_{n:02d}.tsv').open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
 assert len(src)==len(tgt)
 for s,t in zip(src,tgt):
  total+=1; z=t['zh_body']; jp=s['body_jp']
  kinds=[]
  if not z.strip():kinds.append('empty')
  if '\ufffd' in z or any(0xE000<=ord(c)<=0xF8FF for c in z):kinds.append('garbage')
  if KANA.search(z):kinds.append('kana')
  words=set(LAT.findall(z))
  # Source-native title/logo string; JP and EN are both literally K&M Ich.
  if s['scene']=='SEEN4513' and s['code_index']=='1923': words=set()
  badlat=[w for w in words if w not in ALLOW_LAT and not w.startswith('S')]
  if badlat:kinds.append('latin:'+','.join(sorted(badlat)[:5]))
  sc=CTRL.findall(jp);tc=CTRL.findall(z)
  # variables and control tokens must not disappear; newline literal count too
  miss=[]
  for x in set(sc):
   if tc.count(x)<sc.count(x):miss.append(x)
  if miss:kinds.append('control-missing:'+','.join(miss))
  # grossly tiny translation of lexical source
  jpvis=CTRL.sub('',jp); zvis=CTRL.sub('',z)
  if len(re.findall(r'[ぁ-んァ-ヶ一-龯]',jpvis))>=12 and len(re.findall(r'[一-龯]',zvis))<=2:kinds.append('too-short')
  if kinds:
   issues.append({'batch':n,'scene':s['scene'],'code':s['code_index'],'kinds':'|'.join(kinds),'jp':jp,'en':s['en_text'],'zh':z});
   for k in kinds:stats[k.split(':')[0]]+=1
print(json.dumps({'total':total,'issue_rows':len(issues),'stats':dict(stats)},ensure_ascii=False,indent=2))
out=D/'qa_issues.tsv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(issues[0]),delimiter='\t');w.writeheader();w.writerows(issues)
print(out)

