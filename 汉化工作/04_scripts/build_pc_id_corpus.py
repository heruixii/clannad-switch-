from pathlib import Path
import sys,csv,collections,json,re
sys.path.insert(0,str(Path(__file__).parent))
from extract_reallive_anchored_text import rows
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_text/matched/pc_id_parallel_v1';OUT.mkdir(parents=True,exist_ok=True)
allrows=[];summary=[]
for jp in sorted((ROOT/'03_text/pc_jp/raw').glob('SEEN*.TXT')):
    J=rows(jp,'jp'); Z=rows(ROOT/'03_text/pc_zh/raw'/jp.name,'zh')
    jm=collections.defaultdict(list); zm=collections.defaultdict(list)
    for r in J: jm[r['text_id']].append(r)
    for r in Z: zm[r['text_id']].append(r)
    scene=[]
    for tid in sorted(set(jm)|set(zm)):
        jr=jm.get(tid,[]); zr=zm.get(tid,[])
        if len(jr)==1 and len(zr)==1: status='mapped'
        elif len(jr)==1 and not zr: status='jp-only'
        elif len(zr)==1 and not jr: status='zh-only'
        else: status='review-duplicate'
        row={'scene':jp.stem,'text_id':tid,'status':status,
             'jp_offset':jr[0]['text_offset'] if len(jr)==1 else '',
             'zh_offset':zr[0]['text_offset'] if len(zr)==1 else '',
             'jp_text':jr[0]['text'] if len(jr)==1 else ' || '.join(x['text'] for x in jr),
             'zh_text':zr[0]['text'] if len(zr)==1 else ' || '.join(x['text'] for x in zr)}
        scene.append(row);allrows.append(row)
    c=collections.Counter(r['status'] for r in scene)
    summary.append({'scene':jp.stem,'jp_rows':len(J),'zh_rows':len(Z),**c})
    with open(OUT/f'{jp.stem}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['scene','text_id','status','jp_offset','zh_offset','jp_text','zh_text'],delimiter='\t');w.writeheader();w.writerows(scene)
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['scene','text_id','status','jp_offset','zh_offset','jp_text','zh_text'],delimiter='\t');w.writeheader();w.writerows(allrows)
sc=sum((collections.Counter({k:v for k,v in r.items() if k not in ('scene','jp_rows','zh_rows')}) for r in summary),collections.Counter())
with open(OUT/'summary.tsv','w',encoding='utf-8-sig',newline='') as f:
    fields=['scene','jp_rows','zh_rows','mapped','jp-only','zh-only','review-duplicate'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows([{k:r.get(k,0) for k in fields} for r in summary])
print('scenes',len(summary),'total_records',len(allrows));print('status',json.dumps(sc,ensure_ascii=False,sort_keys=True));print('out',OUT)
