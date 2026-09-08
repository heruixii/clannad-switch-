from pathlib import Path
import csv,re,collections,unicodedata,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); U=ROOT/'03_text/matched/switch_pc_v9/unmatched.tsv'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s);return CTRL.sub('',s)
def aggr(s):
 s=unicodedata.normalize('NFKC',base(s));return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
with U.open('r',encoding='utf-8-sig',newline='') as f:r=list(csv.DictReader(f,delimiter='\t'))
empty=[x for x in r if not aggr(x['jp_text'])]
forms=collections.Counter(x['jp_text'] for x in empty)
print('remaining',len(r),'nonverbal',len(empty),'distinct',len(forms))
for s,n in forms.most_common(100):print(n,repr(s),'=>',repr(next(x['en_text'] for x in empty if x['jp_text']==s)))
