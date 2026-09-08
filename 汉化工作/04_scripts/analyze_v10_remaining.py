from pathlib import Path
import csv,collections,re,json,difflib
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
U=ROOT/'03_text/matched/switch_pc_v10/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
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
u=rd(U); pc=rd(PC)
pc_all=collections.defaultdict(list);pc_scene=collections.defaultdict(lambda:collections.defaultdict(list))
for r in pc:
    if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
        t=pn(r['jp_text']);pc_all[t].append(r);pc_scene[r['scene']][t].append(r)
counts=collections.Counter(); scenes=collections.Counter(); samples=collections.defaultdict(list)
for r in u:
    t=sn(r['jp_text']); same=pc_scene[r['scene']].get(t,[]); glob=pc_all.get(t,[])
    ss=[x for x in same if safe(x)]; gs=[x for x in glob if safe(x)]
    if same and ss: cat='same-scene-safe-exact-leftover'
    elif same: cat='same-scene-exact-unsafe-only'
    elif len(gs)==1: cat='global-unique-safe-exact'
    elif gs: cat='global-multi-safe-exact'
    elif glob: cat='global-exact-unsafe-only'
    else: cat='no-exact-pc-jp'
    counts[cat]+=1; scenes[(r['scene'],cat)]+=1
    if len(samples[cat])<12:samples[cat].append({'scene':r['scene'],'code':r['code_index'],'jp':r['jp_text'],'en':r['en_text'][:120]})
print(json.dumps({'remaining':len(u),'categories':dict(counts),'top_scene_category':[{'scene':s,'cat':c,'n':n} for (s,c),n in scenes.most_common(60)],'samples':samples},ensure_ascii=False,indent=2))




