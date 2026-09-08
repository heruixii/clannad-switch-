from pathlib import Path
import sys,csv,re,collections,json,unicodedata
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
BLOCKS=ROOT/'03_text/matched/pc_control_parallel_v1/review_blocks.tsv'

def trim(s): return s.strip(' \t"')
def kind(s): return 'dialogue' if trim(s).startswith('【') else 'narration'
def speaker(s):
    m=re.match(r'^【([^】]+)】',trim(s)); return m.group(1) if m else ''

def norm_sp(s):
    s=s.strip('" ')
    mp={'声':'VOICE','声音':'VOICE','女の子':'GIRL','女孩':'GIRL','男':'MAN','男人':'MAN','教師':'TEACHER','教师':'TEACHER','先生':'TEACHER','？？':'UNKNOWN','？？？':'UNKNOWN'}
    if s in mp:return mp[s]
    if s.startswith('＊') or s.startswith('*'):return s.replace('*','＊')
    return s

def sp_compatible(a,b):
    a=norm_sp(a);b=norm_sp(b)
    if not a or not b:return True
    if a==b:return True
    # ordinary Japanese proper names often survive unchanged; differing named speakers are unsafe
    return False

def pair_valid(j,z):
    if kind(j['text'])!=kind(z['text']):return False
    if kind(j['text'])=='dialogue' and not sp_compatible(speaker(j['text']),speaker(z['text'])):return False
    return True

def pair_score(j,z):
    # lower is better. Validity is already mandatory.
    score=0
    if j['fp']==z['fp']: score-=4
    js,zs=norm_sp(speaker(j['text'])),norm_sp(speaker(z['text']))
    if js and zs and js==zs:score-=2
    # relative text-id deltas are handled at sequence level later
    return score

def try_skip(J,Z,jidx,zidx):
    cand=[]
    if len(zidx)==len(jidx)+1:
      for skip in range(len(zidx)):
        pairs=[];ok=True;score=0
        for n,ji in enumerate(jidx):
          zi=zidx[n if n<skip else n+1]
          if not pair_valid(J[ji],Z[zi]):ok=False;break
          pairs.append((ji,zi));score+=pair_score(J[ji],Z[zi])
        if ok:
          # reward locally similar text-id delta patterns without relying on absolute IDs
          jd=[J[pairs[k+1][0]]['text_id']-J[pairs[k][0]]['text_id'] for k in range(len(pairs)-1)]
          zd=[Z[pairs[k+1][1]]['text_id']-Z[pairs[k][1]]['text_id'] for k in range(len(pairs)-1)]
          score+=sum(0 if a==b else min(abs(a-b),3)*0.25 for a,b in zip(jd,zd))
          cand.append(('skip-zh',skip,pairs,zidx[skip],score))
    elif len(jidx)==len(zidx)+1:
      for skip in range(len(jidx)):
        pairs=[];ok=True;score=0
        for n,zi in enumerate(zidx):
          ji=jidx[n if n<skip else n+1]
          if not pair_valid(J[ji],Z[zi]):ok=False;break
          pairs.append((ji,zi));score+=pair_score(J[ji],Z[zi])
        if ok:
          jd=[J[pairs[k+1][0]]['text_id']-J[pairs[k][0]]['text_id'] for k in range(len(pairs)-1)]
          zd=[Z[pairs[k+1][1]]['text_id']-Z[pairs[k][1]]['text_id'] for k in range(len(pairs)-1)]
          score+=sum(0 if a==b else min(abs(a-b),3)*0.25 for a,b in zip(jd,zd))
          cand.append(('skip-jp',skip,pairs,jidx[skip],score))
    return sorted(cand,key=lambda x:x[4])

def main():
    blocks=list(csv.DictReader(open(BLOCKS,encoding='utf-8-sig'),delimiter='\t'))
    out=[];stats=collections.Counter()
    for b in blocks:
      nj,nz=int(b['jp_count']),int(b['zh_count'])
      if abs(nj-nz)!=1 or max(nj,nz)>12:continue
      J,Z,A=scene(ROOT,b['scene'][4:])
      jidx=list(range(int(b['jp_start']),int(b['jp_end'])+1)) if b['jp_start'] else []
      zidx=list(range(int(b['zh_start']),int(b['zh_end'])+1)) if b['zh_start'] else []
      cand=try_skip(J,Z,jidx,zidx)
      # strict acceptance: exactly one structurally valid skip OR best score beats second by >= 2.0
      decision='unresolved'; chosen=None
      if len(cand)==1: decision='unique-structural';chosen=cand[0]
      elif len(cand)>=2 and cand[1][4]-cand[0][4]>=2.0: decision='score-margin';chosen=cand[0]
      stats[(decision,nj,nz)]+=1
      row={**b,'candidate_count':len(cand),'decision':decision,'skip_side':'','skip_local_index':'','skip_event_index':'','best_score':'','second_score':''}
      if chosen:
        row.update(skip_side=chosen[0],skip_local_index=chosen[1],skip_event_index=chosen[3],best_score=round(chosen[4],3),second_score=round(cand[1][4],3) if len(cand)>1 else '')
      out.append(row)
    outf=ROOT/'03_text/matched/pc_control_parallel_v1/review_gap_candidates_v1.tsv'
    fields=list(out[0].keys())
    with open(outf,'w',encoding='utf-8-sig',newline='') as f:
      w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
    print('eligible_blocks',len(out));print('resolved',sum(r['decision']!='unresolved' for r in out),'unique',sum(r['decision']=='unique-structural' for r in out),'margin',sum(r['decision']=='score-margin' for r in out));print('unresolved',sum(r['decision']=='unresolved' for r in out));print('stats',json.dumps({str(k):v for k,v in stats.items()},ensure_ascii=False,sort_keys=True));print('out',outf)
if __name__=='__main__':main()
