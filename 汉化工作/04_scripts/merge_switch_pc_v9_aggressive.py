from pathlib import Path
import csv,json,re
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); BASE=ROOT/'03_text/matched/switch_pc_v8/safe_matches.tsv'; ADD=ROOT/'03_text/matched/switch_pc_v8/aggressive_between_anchors.tsv'; SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v9'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
base=rd(BASE);add=rd(ADD);sw=rd(SW);sm={(r['scene'],r['code_index']):r for r in sw};rows=list(base);keys={(r['scene'],r['sw_code_index']) for r in rows};fields=list(base[0])
for a in add:
 k=(a['scene'],a['sw_code_index'])
 if k in keys:continue
 s=sm[k]
 rows.append({'scene':a['scene'],'sw_code_index':a['sw_code_index'],'sw_info_data':s['info_data'],'sw_trailing_hex':s['trailing_hex'],'sw_jp_text':a['sw_jp_text'],'sw_jp_norm':a['sw_jp_text'],'sw_en_text':s['en_text'],'pc_scene':a['pc_scene'],'pc_event_index':a['pc_event_index'],'pc_status':a['pc_status'],'pc_jp_text':a['pc_jp_text'],'pc_zh_text':a['pc_zh_text'],'match_kind':a['match_kind']});keys.add(k)
rows.sort(key=lambda r:(r['scene'],int(r['sw_code_index'])));OUT.mkdir(parents=True,exist_ok=True)
with (OUT/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
un=[r for r in sw if (r['scene'],r['code_index']) not in keys];un.sort(key=lambda r:(r['scene'],int(r['code_index'])))
with (OUT/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(un[0]),delimiter='\t');w.writeheader();w.writerows(un)
s={'switch_messages':len(sw),'safe_total':len(rows),'coverage':round(100*len(rows)/len(sw),3),'aggressive_added':len(rows)-len(base),'remaining':len(un)};(OUT/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(s,ensure_ascii=False,indent=2))
