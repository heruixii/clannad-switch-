from pathlib import Path
import csv,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv'
REJECT={('SEEN4428',394,397),('SEEN6416',199,200)}
with SRC.open('r',encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
out=[]
for r in rows:
 if r['accepted']=='1': continue
 k=(r['scene'],int(r['jp_event_index']),int(r['zh_event_index']))
 if k in REJECT: continue
 x=dict(r);x['status']='review-forced-manual';x['manual_decision']='accepted-semantic-review';out.append(x)
fields=list(out[0])
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'low_control_total':sum(r['accepted']=='0' for r in rows),'manual_accepted':len(out),'manual_rejected':len(REJECT),'rejected':[list(x) for x in sorted(REJECT)]},ensure_ascii=False,indent=2));print(OUT)
