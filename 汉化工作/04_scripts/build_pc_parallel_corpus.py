from pathlib import Path
import csv,sys,math,re,json
sys.path.insert(0,str(Path(__file__).parent))
from align_pc_parallel import scene,clean,cls,cjklen

ROOT=Path(__file__).resolve().parents[1]
JP=ROOT/'03_text/pc_jp/raw'; ZH=ROOT/'03_text/pc_zh/raw'
OUT=ROOT/'03_text/matched/pc_parallel_v1'
OUT.mkdir(parents=True,exist_ok=True)

# Conservative policy: auto only clean 1:1 rows with low structural cost.
# Short Japanese utterances can be valid, but if Chinese side is absent they stay review/missing.
def category(op,cost,jtxt,ztxt):
    if op=='1:1':
        jc,jsp=cls(jtxt); zc,zsp=cls(ztxt)
        # resource names / date-like metadata are not story auto-transfer
        if jc=='resource' or zc=='resource': return 'review-resource'
        if cost <= 0.55 and cjklen(jtxt)>=2 and cjklen(ztxt)>=2:
            return 'auto'
        return 'review'
    if op=='1:0': return 'missing-zh'
    if op=='0:1': return 'zh-only'
    return 'review-splitmerge'

allrows=[]; stats={}
for jp in sorted(JP.glob('SEEN*.TXT')):
    zh=ZH/jp.name
    J,Z,ops,score=scene(jp,zh)
    rows=[]; counts={}
    for a,b,c,d,op,cost in ops:
        jt=' / '.join(clean(J[k][2]) for k in range(a,b))
        zt=' / '.join(clean(Z[k][2]) for k in range(c,d))
        cat=category(op,cost,jt,zt)
        counts[cat]=counts.get(cat,0)+1
        row={
          'scene':jp.stem,'jp_start':a,'jp_end':b,'zh_start':c,'zh_end':d,
          'op':op,'cost':round(cost,4),'status':cat,
          'jp_text':jt,'zh_text':zt
        }
        rows.append(row); allrows.append(row)
    stats[jp.stem]={'jp':len(J),'zh':len(Z),'ops':len(ops),'score':round(score,3),**counts}
    with open(OUT/f'{jp.stem}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()) if rows else ['scene'],delimiter='\t'); w.writeheader(); w.writerows(rows)

fields=['scene','jp_start','jp_end','zh_start','zh_end','op','cost','status','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t'); w.writeheader(); w.writerows(allrows)
with open(OUT/'summary.tsv','w',encoding='utf-8-sig',newline='') as f:
    cats=sorted({k for s in stats.values() for k in s if k not in ('jp','zh','ops','score')})
    w=csv.writer(f,delimiter='\t'); w.writerow(['scene','jp','zh','ops','score',*cats])
    for k,v in sorted(stats.items()): w.writerow([k,v['jp'],v['zh'],v['ops'],v['score'],*[v.get(c,0) for c in cats]])

tot={}
for r in allrows: tot[r['status']]=tot.get(r['status'],0)+1
print('scenes',len(stats),'rows',len(allrows)); print('status',json.dumps(tot,ensure_ascii=False,sort_keys=True))
print('auto_pct',round(100*tot.get('auto',0)/max(1,len(allrows)),2))
print('outputs',OUT)
