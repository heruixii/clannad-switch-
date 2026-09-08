from pathlib import Path
import csv,re,unicodedata,collections,json,difflib
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
U=ROOT/'03_text/matched/switch_pc_v10/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*)')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def base(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s);return CTRL.sub('',s)
def bare(s):
 s=unicodedata.normalize('NFKC',base(s));return ''.join(ch for ch in s if ch.isalnum() or '\u3040'<=ch<='\u30ff' or '\u3400'<=ch<='\u9fff' or ch in '＊％')
pc=rd(PC); by=collections.defaultdict(list)
for r in pc:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  t=bare(r['jp_text'])
  if t:by[r['scene']].append((int(r['jp_event_index']),t,r['jp_text'],r.get('zh_text',''),r.get('status','')))
counts=collections.Counter();out=[]
for r in rd(U):
 t=bare(r['jp_text']); c=[]
 for e,pb,pj,zh,st in by.get(r['scene'],[]):
  if len(t)>=2 and (t in pb or pb in t):
   rel='sw-in-pc' if t in pb and t!=pb else ('pc-in-sw' if pb in t and t!=pb else 'equal')
   if rel!='equal':c.append((rel,e,pb,pj,zh,st))
 if len(c)==1:
  rel,e,pb,pj,zh,st=c[0];counts['unique-'+rel]+=1
  if len(out)<200:out.append({'scene':r['scene'],'code':r['code_index'],'rel':rel,'sw':r['jp_text'],'pc_event':e,'pc':pj,'status':st,'zh':zh})
 elif len(c)>1:counts['multi-substring']+=1
 else:counts['none']+=1
print(json.dumps({'counts':dict(counts),'examples':out},ensure_ascii=False,indent=2))
