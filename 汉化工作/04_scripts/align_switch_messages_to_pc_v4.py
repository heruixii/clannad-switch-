from pathlib import Path
import csv,json,difflib,collections,re
ROOT=Path(__file__).resolve().parents[1]
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'
PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
OUTDIR=ROOT/'03_text/matched/switch_pc_v1'

def read_tsv(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def sw_norm(s):
    s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
    if s.startswith('`'):
        at=s.find('@',1)
        if 1 < at <= 24:
            s='【'+s[1:at]+'】'+s[at+1:]
    return s

def pc_norm(s):
    return (s or '').replace('\r','')

def safe_pc(r):
    return bool(r.get('zh_text')) and bool(r.get('jp_text')) and not (r.get('status') or '').startswith('review')

def main():
    sw=read_tsv(SW); pc=read_tsv(PC)
    sw_by=collections.defaultdict(list); pc_by=collections.defaultdict(list)
    for r in sw: sw_by[r['scene']].append(r)
    for r in pc: pc_by[r['scene']].append(r)
    for rows in sw_by.values(): rows.sort(key=lambda r:int(r['code_index']))
    for rows in pc_by.values(): rows.sort(key=lambda r:int(r['jp_event_index']) if r.get('jp_event_index','').isdigit() else 10**9)
    matched=[]; unmatched=[]; scene_stats=[]; safe_pairs=0; equal_pairs=0
    match_by_status=collections.Counter(); kind_counts=collections.Counter()
    for scene,srows in sorted(sw_by.items()):
        prows=pc_by.get(scene,[])
        if not prows:
            for sr in srows:
                u=dict(sr); u['reason']='no-pc-scene'; unmatched.append(u)
            scene_stats.append({'scene':scene,'sw':len(srows),'pc':0,'equal_pairs':0,'safe_pairs':0})
            continue
        a=[sw_norm(r['jp_text']) for r in srows]
        b=[pc_norm(r['jp_text']) for r in prows]
        sm=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
        mapped_sw=set(); sp=0; ep=0
        for block in sm.get_matching_blocks():
            if block.size<=0: continue
            for k in range(block.size):
                si=block.a+k; pi=block.b+k; sr=srows[si]; pr=prows[pi]
                mapped_sw.add(si); ep+=1; equal_pairs+=1
                if safe_pc(pr):
                    row={
                        'scene':scene,'sw_code_index':sr['code_index'],'sw_info_data':sr['info_data'],
                        'sw_trailing_hex':sr['trailing_hex'],'sw_jp_text':sr['jp_text'],'sw_en_text':sr['en_text'],
                        'pc_event_index':pr['jp_event_index'],'pc_status':pr['status'],
                        'pc_jp_text':pr['jp_text'],'pc_zh_text':pr['zh_text'],'match_kind':'exact-sequence'
                    }
                    matched.append(row); sp+=1; safe_pairs+=1
                    match_by_status[pr['status']]+=1; kind_counts['exact-sequence']+=1
        for i,sr in enumerate(srows):
            if i not in mapped_sw:
                u=dict(sr); u['reason']='jp-not-exact-in-sequence'; unmatched.append(u)
            else:
                # exact JP exists but corresponding PC row may be unsafe/review
                # add to unmatched-for-translation only when no safe mapping was emitted
                # find via blocks compactly below
                pass
        # capture exact-mapped-to-unsafe separately
        safe_sw_codes={m['sw_code_index'] for m in matched if m['scene']==scene}
        exact_sw=set()
        for block in sm.get_matching_blocks():
            for k in range(block.size): exact_sw.add(block.a+k)
        for i in sorted(exact_sw):
            sr=srows[i]
            if sr['code_index'] not in safe_sw_codes:
                u=dict(sr); u['reason']='pc-match-not-safe'; unmatched.append(u)
        scene_stats.append({'scene':scene,'sw':len(srows),'pc':len(prows),'equal_pairs':ep,'safe_pairs':sp})
    OUTDIR.mkdir(parents=True,exist_ok=True)
    mf=OUTDIR/'safe_matches.tsv'
    fields=['scene','sw_code_index','sw_info_data','sw_trailing_hex','sw_jp_text','sw_en_text','pc_event_index','pc_status','pc_jp_text','pc_zh_text','match_kind']
    with mf.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(matched)
    # dedupe unmatched by scene/code because exact-but-unsafe pass and nonmatch are disjoint, but guard anyway
    uniq={}
    for r in unmatched: uniq[(r['scene'],r['code_index'])]=r
    unmatched=list(uniq.values()); unmatched.sort(key=lambda r:(r['scene'],int(r['code_index'])))
    uf=OUTDIR/'unmatched.tsv'
    ufields=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex','reason']
    with uf.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=ufields,delimiter='\t');w.writeheader();w.writerows(unmatched)
    sf=OUTDIR/'scene_stats.tsv'
    with sf.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['scene','sw','pc','equal_pairs','safe_pairs'],delimiter='\t');w.writeheader();w.writerows(scene_stats)
    summary={
        'switch_messages':len(sw),'pc_rows':len(pc),'switch_scenes':len(sw_by),'pc_scenes':len(pc_by),
        'scene_intersection':len(set(sw_by)&set(pc_by)),'switch_only_scenes':sorted(set(sw_by)-set(pc_by)),
        'exact_sequence_pairs':equal_pairs,'safe_pc_mappings':safe_pairs,
        'safe_mapping_coverage_all_switch':round(safe_pairs/len(sw)*100,3) if sw else 0,
        'unmatched_or_unsafe':len(unmatched),'by_pc_status':dict(match_by_status),
        'safe_matches':str(mf),'unmatched':str(uf)
    }
    (OUTDIR/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
