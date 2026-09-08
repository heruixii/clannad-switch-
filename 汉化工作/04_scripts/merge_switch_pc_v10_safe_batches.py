from pathlib import Path
import csv,json,collections
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
BASE=ROOT/'03_text/matched/switch_pc_v9/safe_matches.tsv'
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'
G=ROOT/'03_text/matched/switch_pc_v9/global_exact_consensus.tsv'
F=ROOT/'03_text/matched/switch_pc_v9/fuzzy_between_anchors.tsv'
O2=ROOT/'03_text/matched/switch_pc_v9/one_switch_two_pc.tsv'
OUT=ROOT/'03_text/matched/switch_pc_v10'

def rd(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def addrow(rows,keys,sm,a,kind,pc_scene='',pc_event='',pc_status='',pc_jp='',zh=''):
    k=(a['scene'],str(a.get('sw_code_index',a.get('code_index',''))))
    if k in keys:return False
    s=sm.get(k)
    if s is None:raise RuntimeError(f'missing switch key {k}')
    rows.append({
      'scene':k[0],'sw_code_index':k[1],'sw_info_data':s['info_data'],'sw_trailing_hex':s['trailing_hex'],
      'sw_jp_text':s['jp_text'],'sw_jp_norm':s['jp_text'],'sw_en_text':s['en_text'],
      'pc_scene':pc_scene,'pc_event_index':str(pc_event),'pc_status':pc_status,'pc_jp_text':pc_jp,
      'pc_zh_text':zh,'match_kind':kind})
    keys.add(k);return True

base=rd(BASE);sw=rd(SW);sm={(r['scene'],r['code_index']):r for r in sw}
rows=list(base); keys={(r['scene'],r['sw_code_index']) for r in rows}; stats=collections.Counter()
# 1) exact global unique/consensus
for a in rd(G):
    if addrow(rows,keys,sm,a,a['match_kind'],a['pc_scene'],a['pc_event_index'],a['pc_status'],a['pc_jp_text'],a['pc_zh_text']):stats[a['match_kind']]+=1
# 2) only extremely close fuzzy >= .96
for a in rd(F):
    if float(a['similarity']) < .96:continue
    if addrow(rows,keys,sm,a,'fuzzy-between-anchors-ge096',a['pc_scene'],a['pc_event_index'],a['pc_status'],a['pc_jp_text'],a['pc_zh_text']):stats['fuzzy-ge096']+=1
# 3) one Switch row equals two consecutive trusted PC rows (currently one verified narration row)
for a in rd(O2):
    zh=(a['zh1'] or '')+(a['zh2'] or '')
    pcjp=(a['pc_jp1'] or '')+(a['pc_jp2'] or '')
    if addrow(rows,keys,sm,a,'one-switch-two-pc-exact',a['pc_scene'],a['pc_e1']+'+'+a['pc_e2'],'two-pc-exact',pcjp,zh):stats['one-switch-two-pc']+=1
# 4) non-verbal / punctuation / blank: preserve the visible JP token exactly; it contains no Japanese lexical content
# Classification criterion is Unicode lexical chars absent after stripping formatting; copy only a hardcoded safe form set observed in audit.
safe_nonverbal={'','\u3000','＿','………。','……。','…。','「………」','………','…','」','～～～','『………』','!!!','\u3000～～～～!?!','\u3000～～～～～!!!!」','～～','!!」','～!!」','………………。','`？@「？」','`？@「??」','`？@「???」','`？@「……………」','`？@「！','?!','?!」','`？？@「………」'}
for s in sw:
    k=(s['scene'],s['code_index'])
    if k in keys or s['jp_text'] not in safe_nonverbal:continue
    a={'scene':s['scene'],'code_index':s['code_index']}
    if addrow(rows,keys,sm,a,'nonverbal-preserved',zh=s['jp_text']):stats['nonverbal']+=1

# integrity
if len(keys)!=len(rows):raise RuntimeError('duplicate switch key after merge')
rows.sort(key=lambda r:(r['scene'],int(r['sw_code_index'])))
OUT.mkdir(parents=True,exist_ok=True)
fields=list(base[0].keys())
with (OUT/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
un=[r for r in sw if (r['scene'],r['code_index']) not in keys]
un.sort(key=lambda r:(r['scene'],int(r['code_index'])))
with (OUT/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(un[0].keys()),delimiter='\t');w.writeheader();w.writerows(un)
summary={'switch_messages':len(sw),'safe_total':len(rows),'coverage':round(100*len(rows)/len(sw),3),'added':dict(stats),'remaining':len(un)}
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
