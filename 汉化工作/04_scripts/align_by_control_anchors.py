from pathlib import Path
import sys,collections,bisect,csv,json
sys.path.insert(0,str(Path(__file__).parent))
from analyze_control_fingerprints import events

# LIS over (jp_index, zh_index) unique fingerprint anchors
def lis_pairs(pairs):
    tails=[]; tails_idx=[]; prev=[-1]*len(pairs)
    for k,(i,j,fp) in enumerate(pairs):
        pos=bisect.bisect_left(tails,j)
        if pos==len(tails): tails.append(j); tails_idx.append(k)
        else: tails[pos]=j; tails_idx[pos]=k
        if pos: prev[k]=tails_idx[pos-1]
    if not tails_idx:return []
    k=tails_idx[-1]; out=[]
    while k>=0:
        out.append(pairs[k]); k=prev[k]
    return out[::-1]

def scene(root,sc):
    J=events(root/f'03_text/pc_jp/raw/SEEN{sc}.TXT','jp')
    zraw=root/f'03_text/pc_zh/raw/SEEN{sc}.TXT'
    zrec=root/f'03_text/pc_zh/recovered/SEEN{sc}.TXT'
    Z=events(zrec if zrec.exists() else zraw,'zh')
    jc=collections.Counter(r['fp'] for r in J); zc=collections.Counter(r['fp'] for r in Z)
    zpos={r['fp']:i for i,r in enumerate(Z) if zc[r['fp']]==1}
    pairs=[(i,zpos[r['fp']],r['fp']) for i,r in enumerate(J) if jc[r['fp']]==1 and r['fp'] in zpos]
    anchors=lis_pairs(pairs)
    return J,Z,anchors

def map_segments(J,Z,A):
    # Sentinels; anchor rows themselves are structural exact matches.
    pts=[(-1,-1,None)]+A+[(len(J),len(Z),None)]
    rows=[]; counts=collections.Counter()
    for q in range(len(pts)-1):
        ai,az,_=pts[q]; bi,bz,_=pts[q+1]
        # map anchor itself except sentinel
        if q>0:
            rows.append((ai,az,'anchor'));counts['anchor']+=1
        js=list(range(ai+1,bi)); zs=list(range(az+1,bz))
        if len(js)==len(zs):
            for x,y in zip(js,zs): rows.append((x,y,'equal-segment'));counts['equal-segment']+=1
        else:
            # do not guess inside unequal segments
            for x in js: rows.append((x,None,'review-jp'));counts['review-jp']+=1
            for y in zs: rows.append((None,y,'review-zh'));counts['review-zh']+=1
            counts['unequal-segments']+=1
    return rows,counts

if __name__=='__main__':
    root=Path(sys.argv[1]); sc=sys.argv[2]
    J,Z,A=scene(root,sc); M,C=map_segments(J,Z,A)
    print('scene',sc,'J',len(J),'Z',len(Z),'anchors',len(A),'counts',dict(C))
    # print first mapped sample
    n=0
    for i,j,st in M:
        if i is not None and j is not None:
            print(st,i,j,'tid',J[i]['text_id'],Z[j]['text_id'],J[i]['text'].encode('unicode_escape').decode()[:100],'=>',Z[j]['text'].encode('unicode_escape').decode()[:100]);n+=1
            if n>=60:break

