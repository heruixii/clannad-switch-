from pathlib import Path
import csv,collections,re,json
ROOT=Path(__file__).resolve().parents[1]
U=ROOT/'03_text/matched/switch_pc_v3/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]'); STYLE=re.compile(r'\$S(?:U)?\d{3}')
def rd(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sn(s):
    s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
    if s.startswith('`'):
        at=s.find('@',1)
        if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
    return STYLE.sub('',RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)).replace('$W','')
def pn(s):return (s or '').replace('\r','')
def safe(r):return bool(r.get('zh_text')) and not (r.get('status') or '').startswith('review') and (r.get('jp_event_index') or '').isdigit()
u=rd(U); pc=[r for r in rd(PC) if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text')]
pcocc=collections.defaultdict(list);swocc=collections.Counter()
for r in pc:pcocc[pn(r['jp_text'])].append(r)
for r in u:swocc[sn(r['jp_text'])]+=1
unique=[];anyexact=0;scenepairs=collections.Counter();safeany=0
for r in u:
    n=sn(r['jp_text']); ps=pcocc.get(n,[])
    if ps:anyexact+=1
    safes=[x for x in ps if safe(x)]
    if safes:safeany+=1
    if swocc[n]==1 and len(ps)==1 and safe(ps[0]):
        p0=ps[0];unique.append((r,p0));scenepairs[(r['scene'],p0['scene'])]+=1
print(json.dumps({'unmatched':len(u),'has_any_exact_pc_text':anyexact,'has_any_safe_exact_pc_text':safeany,'strict_global_unique_safe':len(unique),'top_scene_pairs':[{'sw':a,'pc':b,'count':c} for (a,b),c in scenepairs.most_common(40)]},ensure_ascii=False,indent=2))
