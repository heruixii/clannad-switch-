from pathlib import Path
import sys,csv,collections,bisect,json,re
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
BLOCKS=ROOT/'03_text/matched/pc_control_parallel_v1/review_blocks.tsv'

def trim(s): return s.strip(' \t\"')
def kind(s): return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker(s):
    m=re.match(r'^【([^】]+)】',trim(s)); return m.group(1) if m else ''
def norm_sp(s):
    s=s.strip(' \"')
    mp={'声':'VOICE','声音':'VOICE','女の子':'GIRL','女孩':'GIRL','男':'MAN','男人':'MAN','教師':'TEACHER','教师':'TEACHER','先生':'TEACHER','？？':'UNKNOWN','？？？':'UNKNOWN'}
    if s in mp:return mp[s]
    if s.startswith('＊') or s.startswith('*'):return s.replace('*','＊')
    return s

def compatible(j,z):
    if kind(j['text'])!=kind(z['text']): return False
    if kind(j['text'])=='dialogue':
        a,b=norm_sp(speaker(j['text'])),norm_sp(speaker(z['text']))
        if a and b and a!=b:return False
    return True

def lis(pairs):
    if not pairs:return []
    tails=[]; taili=[]; prev=[-1]*len(pairs)
    for k,(i,j) in enumerate(pairs):
        q=bisect.bisect_left(tails,j)
        if q==len(tails):tails.append(j);taili.append(k)
        else:tails[q]=j;taili[q]=k
        if q:prev[k]=taili[q-1]
    k=taili[-1];out=[]
    while k>=0:out.append(pairs[k]);k=prev[k]
    return out[::-1]

def unique_local_anchors(J,Z,js,zs):
    jc=collections.Counter(J[i]['fp'] for i in js); zc=collections.Counter(Z[i]['fp'] for i in zs)
    zp={Z[i]['fp']:i for i in zs if zc[Z[i]['fp']]==1}
    pairs=[(i,zp[J[i]['fp']]) for i in js if jc[J[i]['fp']]==1 and J[i]['fp'] in zp]
    return lis(pairs)

def resolve(J,Z,js,zs,depth=0):
    # returns safe pairs, unresolved jp, unresolved zh, anchor count
    if not js or not zs:return [],list(js),list(zs),0
    # equal-length region: only release if every pair is structurally compatible
    if len(js)==len(zs):
        pp=list(zip(js,zs))
        if all(compatible(J[a],Z[b]) for a,b in pp):return pp,[],[],0
    A=unique_local_anchors(J,Z,js,zs)
    # only anchors themselves are safe if compatible; incompatible anchors are ignored
    A=[p for p in A if compatible(J[p[0]],Z[p[1]])]
    if not A:return [],list(js),list(zs),0
    safe=[]; uj=[];uz=[]; prevj=js[0]-1;prevz=zs[0]-1
    jset=set(js);zset=set(zs)
    for aj,az in A:
        subjs=[i for i in js if prevj<i<aj]; subzs=[i for i in zs if prevz<i<az]
        s,a,b,_=resolve(J,Z,subjs,subzs,depth+1);safe+=s;uj+=a;uz+=b
        safe.append((aj,az));prevj,prevz=aj,az
    subjs=[i for i in js if i>prevj];subzs=[i for i in zs if i>prevz]
    s,a,b,_=resolve(J,Z,subjs,subzs,depth+1);safe+=s;uj+=a;uz+=b
    return safe,uj,uz,len(A)

def main():
    B=list(csv.DictReader(open(BLOCKS,encoding='utf-8-sig'),delimiter='\t'))
    rows=[];total=collections.Counter()
    for b in B:
        sc=b['scene'];J,Z,_=scene(ROOT,sc[4:]);
        js=list(range(int(b['jp_start']),int(b['jp_end'])+1)) if b['jp_start'] else []
        zs=list(range(int(b['zh_start']),int(b['zh_end'])+1)) if b['zh_start'] else []
        safe,uj,uz,na=resolve(J,Z,js,zs)
        # exclude pairs already part of equal-sized original blocks; this resolver targets unequal blocks
        if int(b['jp_count'])==int(b['zh_count']): safe=[];uj=js;uz=zs
        for ji,zi in safe:
            rows.append({'scene':sc,'block_id':b['block_id'],'jp_event_index':ji,'zh_event_index':zi,'status':'recursive-control','jp_fp':J[ji]['fp'],'zh_fp':Z[zi]['fp'],'jp_kind':kind(J[ji]['text']),'zh_kind':kind(Z[zi]['text']),'jp_speaker':speaker(J[ji]['text']),'zh_speaker':speaker(Z[zi]['text']),'jp_text':J[ji]['text'],'zh_text':Z[zi]['text']})
        total['safe']+=len(safe);total['unresolved_jp']+=len(uj);total['unresolved_zh']+=len(uz);total['blocks']+=1;total['blocks_with_safe']+=bool(safe)
    out=ROOT/'03_text/matched/pc_control_parallel_v1/recursive_control_candidates.tsv'
    fields=list(rows[0].keys()) if rows else []
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
    print(json.dumps(total,ensure_ascii=False));print('pairs',len(rows),'unique_jp',len(set((r['scene'],r['jp_event_index']) for r in rows)),'unique_zh',len(set((r['scene'],r['zh_event_index']) for r in rows)));print('type_mismatch',sum(r['jp_kind']!=r['zh_kind'] for r in rows));print('out',out)
if __name__=='__main__':main()
