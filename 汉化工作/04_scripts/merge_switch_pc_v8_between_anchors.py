from pathlib import Path
import csv,json,collections,re
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); BASE=ROOT/'03_text/matched/switch_pc_v8_base/safe_matches.tsv'; ADD=ROOT/'03_text/matched/switch_pc_v8_base/between_anchor_exact.tsv'; SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v8'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');STYLE=re.compile(r'\$S(?:U)?\d{3}')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sn(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 return STYLE.sub('',RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)).replace('$W','')
base=rd(BASE);add=rd(ADD);sw=rd(SW);rows=list(base);keys={(r['scene'],r['sw_code_index']) for r in rows}
for a in add:
 k=(a['scene'],a['sw_code_index'])
 if k in keys:continue
 rows.append({'scene':a['scene'],'sw_code_index':a['sw_code_index'],'sw_info_data':'','sw_trailing_hex':'','sw_jp_text':a['sw_jp_text'],'sw_jp_norm':sn(a['sw_jp_text']),'sw_en_text':a['sw_en_text'],'pc_scene':a['pc_scene'],'pc_event_index':a['pc_event_index'],'pc_status':a['pc_status'],'pc_jp_text':a['pc_jp_text'],'pc_zh_text':a['pc_zh_text'],'match_kind':a['match_kind']});keys.add(k)
# fill metadata from SW
sm={(r['scene'],r['code_index']):r for r in sw}
for r in rows:
 s=sm[(r['scene'],r['sw_code_index'])];r['sw_info_data']=s['info_data'];r['sw_trailing_hex']=s['trailing_hex'];r['sw_en_text']=s['en_text']
rows.sort(key=lambda r:(r['scene'],int(r['sw_code_index'])));OUT.mkdir(parents=True,exist_ok=True);fields=list(base[0])
with (OUT/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
un=[r for r in sw if (r['scene'],r['code_index']) not in keys];un.sort(key=lambda r:(r['scene'],int(r['code_index'])));uf=list(un[0])
with (OUT/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=uf,delimiter='\t');w.writeheader();w.writerows(un)
s={'switch_messages':len(sw),'safe_total':len(rows),'coverage':round(100*len(rows)/len(sw),3),'added_between_anchors':len(rows)-len(base),'remaining':len(un)};(OUT/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))

