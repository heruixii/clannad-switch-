from pathlib import Path
import csv,json,difflib,collections,re,bisect
ROOT=Path(__file__).resolve().parents[1]
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; OUTDIR=ROOT/'03_text/matched/switch_pc_v3'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]'); STYLE=re.compile(r'\$S(?:U)?\d{3}')
def read_tsv(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sw_norm(s):
    s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
    if s.startswith('`'):
        at=s.find('@',1)
        if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
    s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s); s=STYLE.sub('',s).replace('$W','')
    return s
def pc_norm(s):return (s or '').replace('\r','')
def safe_pc(r):return bool(r.get('zh_text')) and bool(r.get('jp_text')) and not (r.get('status') or '').startswith('review')
def monotonic_ok(si,pj,mapping,n_sw,n_pc):
    if si in mapping:return mapping[si]==pj
    ks=sorted(mapping)
    pos=bisect.bisect_left(ks,si)
    if pos>0 and mapping[ks[pos-1]]>=pj:return False
    if pos<len(ks) and mapping[ks[pos]]<=pj:return False
    return True

def main():
    sw=read_tsv(SW);pc0=read_tsv(PC);pc=[r for r in pc0 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text')]
    sw_by=collections.defaultdict(list);pc_by=collections.defaultdict(list)
    for r in sw:sw_by[r['scene']].append(r)
    for r in pc:pc_by[r['scene']].append(r)
    for v in sw_by.values():v.sort(key=lambda r:int(r['code_index']))
    for v in pc_by.values():v.sort(key=lambda r:int(r['jp_event_index']))
    matched=[];unmatched=[];scene_stats=[];kinds=collections.Counter();statusc=collections.Counter();total_exact=total_safe=0
    for scene,srows in sorted(sw_by.items()):
        prows=pc_by.get(scene,[])
        if not prows:
            for sr in srows:u=dict(sr);u['reason']='no-pc-scene';unmatched.append(u)
            scene_stats.append({'scene':scene,'sw':len(srows),'pc':0,'exact_pairs':0,'safe_pairs':0,'seq':0,'unique':0,'repeat':0});continue
        a=[sw_norm(r['jp_text']) for r in srows];b=[pc_norm(r['jp_text']) for r in prows]
        sm=difflib.SequenceMatcher(a=a,b=b,autojunk=False);mapping={};mk={}
        for block in sm.get_matching_blocks():
            for k in range(block.size):mapping[block.a+k]=block.b+k;mk[block.a+k]='sequence'
        seqn=len(mapping)
        sw_occ=collections.defaultdict(list);pc_occ=collections.defaultdict(list)
        for i,t in enumerate(a):sw_occ[t].append(i)
        for j,t in enumerate(b):pc_occ[t].append(j)
        # unique exact text, constrained by established monotonic anchors
        changed=True;un=0
        while changed:
            changed=False
            for t,sis in sw_occ.items():
                pjs=pc_occ.get(t,[])
                if len(sis)==1 and len(pjs)==1:
                    si,pj=sis[0],pjs[0]
                    if si not in mapping and monotonic_ok(si,pj,mapping,len(a),len(b)):
                        mapping[si]=pj;mk[si]='unique-monotonic';un+=1;changed=True
        # repeated exact text only if occurrence counts are equal and each nth pair remains monotonic
        rn=0
        for t,sis in sorted(sw_occ.items(), key=lambda kv:min(kv[1])):
            pjs=pc_occ.get(t,[])
            if len(sis)>=2 and len(sis)==len(pjs) and len(sis)<=32:
                for si,pj in zip(sis,pjs):
                    if si in mapping:continue
                    if monotonic_ok(si,pj,mapping,len(a),len(b)):
                        mapping[si]=pj;mk[si]='repeat-equal-monotonic';rn+=1
        # final monotonic sanity
        pairs=sorted(mapping.items());last=-1;bad=[]
        for si,pj in pairs:
            if pj<=last:bad.append(si)
            else:last=pj
        for si in bad:mapping.pop(si,None);mk.pop(si,None)
        sp=0
        for si,sr in enumerate(srows):
            if si not in mapping:
                u=dict(sr);u['reason']='no-safe-exact-monotonic';unmatched.append(u);continue
            total_exact+=1;pr=prows[mapping[si]]
            if safe_pc(pr):
                kind=mk[si];matched.append({'scene':scene,'sw_code_index':sr['code_index'],'sw_info_data':sr['info_data'],'sw_trailing_hex':sr['trailing_hex'],'sw_jp_text':sr['jp_text'],'sw_jp_norm':a[si],'sw_en_text':sr['en_text'],'pc_event_index':pr['jp_event_index'],'pc_status':pr['status'],'pc_jp_text':pr['jp_text'],'pc_zh_text':pr['zh_text'],'match_kind':kind});total_safe+=1;sp+=1;kinds[kind]+=1;statusc[pr['status']]+=1
            else:
                u=dict(sr);u['reason']='pc-match-not-safe';unmatched.append(u)
        scene_stats.append({'scene':scene,'sw':len(srows),'pc':len(prows),'exact_pairs':len(mapping),'safe_pairs':sp,'seq':seqn,'unique':un,'repeat':rn})
    OUTDIR.mkdir(parents=True,exist_ok=True)
    fields=['scene','sw_code_index','sw_info_data','sw_trailing_hex','sw_jp_text','sw_jp_norm','sw_en_text','pc_event_index','pc_status','pc_jp_text','pc_zh_text','match_kind']
    with (OUTDIR/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(matched)
    uflds=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex','reason']
    with (OUTDIR/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=uflds,delimiter='\t');w.writeheader();w.writerows(unmatched)
    sflds=['scene','sw','pc','exact_pairs','safe_pairs','seq','unique','repeat']
    with (OUTDIR/'scene_stats.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=sflds,delimiter='\t');w.writeheader();w.writerows(scene_stats)
    summ={'switch_messages':len(sw),'pc_jp_rows_used':len(pc),'scene_intersection':len(set(sw_by)&set(pc_by)),'exact_monotonic_pairs':total_exact,'safe_pc_mappings':total_safe,'exact_pair_coverage_all_switch':round(100*total_exact/len(sw),3),'safe_mapping_coverage_all_switch':round(100*total_safe/len(sw),3),'unmatched_or_unsafe':len(unmatched),'match_kinds':dict(kinds),'by_pc_status':dict(statusc)}
    (OUTDIR/'summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summ,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
