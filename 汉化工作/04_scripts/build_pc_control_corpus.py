from pathlib import Path
import sys,csv,collections,json,re
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene,map_segments
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_text/matched/pc_control_parallel_v1';OUT.mkdir(parents=True,exist_ok=True)

def kind(s):
    s=s.strip(' "')
    return 'dialogue' if s.startswith('【') else 'narration'

def speaker(s):
    s=s.strip(' "')
    m=re.match(r'^【([^】]+)】',s)
    return m.group(1) if m else ''

def clean_zh(s):
    s=s.strip()
    # compiler-inserted extra ASCII quotes around Chinese strings; safe to strip only outer quote chars
    while len(s)>=2 and s[0]=='"' and s[-1]=='"': s=s[1:-1]
    return s

def standalone_name_match(jt,zt):
    jm=re.fullmatch(r'【([^】]+)】', jt.strip(' "'))
    if not jm: return False
    z=zt.strip(' "')
    zm=re.fullmatch(r'【([^】]+)】',z)
    if zm: z=zm.group(1).strip(' "')
    else: z=z.strip(' "')
    return z==jm.group(1).strip(' "')

allrows=[]; summaries=[]; total=collections.Counter()
for p in sorted((ROOT/'03_text/pc_jp/raw').glob('SEEN*.TXT')):
    sc=p.stem[4:];J,Z,A=scene(ROOT,sc);M,C=map_segments(J,Z,A); rows=[]; counts=collections.Counter(); seg=0
    for i,j,st in M:
        if i is not None and j is not None:
            jt=J[i]['text']; zt=clean_zh(Z[j]['text']); jk=kind(jt); zk=kind(zt)
            status=st
            reason=''
            if any(ch in zt for ch in '亂亃仏俛俙'):
                status='review-decode-garbage'; reason='implausible-decoded-codepoints'
            elif jk!=zk:
                # RealLive occasionally emits a standalone speaker-name event.
                # If JP is exactly 【name】 and ZH is the same name with compiler quotes only,
                # treat it as a structural name event rather than narration/dialogue conflict.
                if standalone_name_match(jt,zt):
                    status='name-event'; reason='standalone-speaker-name'
                else:
                    status='review-type-mismatch'; reason=f'{jk}!={zk}'
            row={'scene':'SEEN'+sc,'segment':seg,'jp_event_index':i,'zh_event_index':j,'status':status,'reason':reason,
                 'jp_text_id':J[i]['text_id'],'zh_text_id':Z[j]['text_id'],'jp_kidoku_id':J[i]['kidoku_id'],'zh_kidoku_id':Z[j]['kidoku_id'],
                 'jp_offset':J[i]['text_offset'],'zh_offset':Z[j]['text_offset'],'jp_kind':jk,'zh_kind':zk,'jp_speaker':speaker(jt),'zh_speaker':speaker(zt),'jp_text':jt,'zh_text':zt}
        elif i is not None:
            row={'scene':'SEEN'+sc,'segment':seg,'jp_event_index':i,'zh_event_index':'','status':'review-jp','reason':'unequal-control-segment',
                 'jp_text_id':J[i]['text_id'],'zh_text_id':'','jp_kidoku_id':J[i]['kidoku_id'],'zh_kidoku_id':'','jp_offset':J[i]['text_offset'],'zh_offset':'','jp_kind':kind(J[i]['text']),'zh_kind':'','jp_speaker':speaker(J[i]['text']),'zh_speaker':'','jp_text':J[i]['text'],'zh_text':''}
        else:
            row={'scene':'SEEN'+sc,'segment':seg,'jp_event_index':'','zh_event_index':j,'status':'review-zh','reason':'unequal-control-segment',
                 'jp_text_id':'','zh_text_id':Z[j]['text_id'],'jp_kidoku_id':'','zh_kidoku_id':Z[j]['kidoku_id'],'jp_offset':'','zh_offset':Z[j]['text_offset'],'jp_kind':'','zh_kind':kind(clean_zh(Z[j]['text'])),'jp_speaker':'','zh_speaker':speaker(clean_zh(Z[j]['text'])),'jp_text':'','zh_text':clean_zh(Z[j]['text'])}
        counts[row['status']]+=1;total[row['status']]+=1;rows.append(row);allrows.append(row);seg+=1
    fields=list(rows[0].keys()) if rows else []
    with open(OUT/f'SEEN{sc}.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(rows)
    summaries.append({'scene':'SEEN'+sc,'jp_rows':len(J),'zh_rows':len(Z),'anchors':len(A),**counts})
fields=['scene','segment','jp_event_index','zh_event_index','status','reason','jp_text_id','zh_text_id','jp_kidoku_id','zh_kidoku_id','jp_offset','zh_offset','jp_kind','zh_kind','jp_speaker','zh_speaker','jp_text','zh_text']
with open(OUT/'all.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(allrows)
sfields=['scene','jp_rows','zh_rows','anchors','anchor','equal-segment','name-event','source-unusable','review-decode-garbage','review-type-mismatch','review-jp','review-zh']
with open(OUT/'summary.tsv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=sfields,delimiter='\t');w.writeheader();w.writerows([{k:r.get(k,0) for k in sfields} for r in summaries])
safe=total['anchor']+total['equal-segment']+total['name-event'];print('scenes',len(summaries));print('status',json.dumps(total,ensure_ascii=False,sort_keys=True));print('safe',safe,'safe_pct_jp',round(100*safe/sum(r['jp_rows'] for r in summaries),3));print('out',OUT)


