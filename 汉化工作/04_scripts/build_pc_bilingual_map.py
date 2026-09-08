from pathlib import Path
import sys,csv,json,time
sys.path.insert(0,str(Path(__file__).parent))
from extract_text_islands import extract
from align_pc_parallel import align,clean,cls,unit_cost,speakers_compatible

ROOT=Path(__file__).resolve().parents[1]
JP=ROOT/'03_text/pc_jp/raw'; ZH=ROOT/'03_text/pc_zh/raw'; OUT=ROOT/'03_text/matched/pc_parallel_v1'
OUT.mkdir(parents=True,exist_ok=True)

def status(t,c,jtxt,ztxt):
    if t!='1:1': return 'review-structure'
    cj,sj=cls(jtxt); cz,sz=cls(ztxt)
    if cj!=cz: return 'review-type'
    if cj=='dialogue' and not speakers_compatible(sj,sz):
        return 'review-speaker'
    if c<=0.58: return 'high'
    if c<=0.95: return 'review-score'
    return 'review-low'

def main():
    allrows=[]; summaries=[]; t0=time.time()
    files=sorted(JP.glob('SEEN*.TXT'))
    for ix,jp in enumerate(files,1):
        zh=ZH/jp.name
        J=extract(jp.read_bytes(),'jp'); Z=extract(zh.read_bytes(),'zh')
        A=[x[2] for x in J]; B=[x[2] for x in Z]
        ops,score=align(A,B)
        counts={}
        rows=[]
        for a,b,c,d,t,cost in ops:
            jt=' / '.join(clean(J[k][2]) for k in range(a,b)); zt=' / '.join(clean(Z[k][2]) for k in range(c,d))
            st=status(t,cost,jt,zt); counts[st]=counts.get(st,0)+1
            row=[jp.stem,a,b,c,d,t,f'{cost:.4f}',st,jt,zt]
            rows.append(row); allrows.append(row)
        summaries.append([jp.stem,len(J),len(Z),len(ops),counts.get('high',0),sum(v for k,v in counts.items() if k!='high'),score])
        with open(OUT/f'{jp.stem}.tsv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,delimiter='\t');w.writerow(['scene','jp_start','jp_end','zh_start','zh_end','op','cost','status','jp_text','zh_text']);w.writerows(rows)
        if ix%20==0 or ix==len(files): print('progress',ix,'/',len(files),'elapsed',round(time.time()-t0,1))
    with open(ROOT/'03_text/matched/pc-parallel-v1.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['scene','jp_start','jp_end','zh_start','zh_end','op','cost','status','jp_text','zh_text']);w.writerows(allrows)
    with open(ROOT/'03_text/matched/pc-parallel-summary-v1.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['scene','jp_rows','zh_rows','ops','high','review','score']);w.writerows(summaries)
    print('scenes',len(summaries),'ops',len(allrows),'high',sum(r[4] for r in summaries),'review',sum(r[5] for r in summaries))
    print('jp_rows',sum(r[1] for r in summaries),'zh_rows',sum(r[2] for r in summaries))
    print('high_ratio',round(sum(r[4] for r in summaries)/max(1,sum(r[1] for r in summaries))*100,3))
if __name__=='__main__':main()


