from pathlib import Path
import csv,json,difflib,collections,re
ROOT=Path(__file__).resolve().parents[1]
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'
PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
OUTDIR=ROOT/'03_text/matched/switch_pc_v2'
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]')
STYLE=re.compile(r'\$S(?:U)?\d{3}')

def read_tsv(path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))

def sw_norm(s):
    s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
    if s.startswith('`'):
        at=s.find('@',1)
        if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
    s=RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)
    s=STYLE.sub('',s).replace('$W','')
    return s

def pc_norm(s):return (s or '').replace('\r','')
def safe_pc(r):return bool(r.get('zh_text')) and bool(r.get('jp_text')) and not (r.get('status') or '').startswith('review')

def main():
    sw=read_tsv(SW); pc0=read_tsv(PC)
    pc=[r for r in pc0 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text')]
    sw_by=collections.defaultdict(list);pc_by=collections.defaultdict(list)
    for r in sw:sw_by[r['scene']].append(r)
    for r in pc:pc_by[r['scene']].append(r)
    for v in sw_by.values():v.sort(key=lambda r:int(r['code_index']))
    for v in pc_by.values():v.sort(key=lambda r:int(r['jp_event_index']))
    matched=[];unmatched=[];scene_stats=[];statusc=collections.Counter();equal_pairs=safe_pairs=0
    for scene,srows in sorted(sw_by.items()):
        prows=pc_by.get(scene,[])
        if not prows:
            for sr in srows:u=dict(sr);u['reason']='no-pc-scene';unmatched.append(u)
            scene_stats.append({'scene':scene,'sw':len(srows),'pc':0,'equal_pairs':0,'safe_pairs':0});continue
        a=[sw_norm(r['jp_text']) for r in srows];b=[pc_norm(r['jp_text']) for r in prows]
        sm=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
        exactmap={}
        for block in sm.get_matching_blocks():
            for k in range(block.size):exactmap[block.a+k]=block.b+k
        sp=0
        for si,sr in enumerate(srows):
            if si not in exactmap:
                u=dict(sr);u['reason']='jp-not-exact-in-sequence';unmatched.append(u);continue
            equal_pairs+=1;pr=prows[exactmap[si]]
            if safe_pc(pr):
                matched.append({'scene':scene,'sw_code_index':sr['code_index'],'sw_info_data':sr['info_data'],'sw_trailing_hex':sr['trailing_hex'],'sw_jp_text':sr['jp_text'],'sw_jp_norm':a[si],'sw_en_text':sr['en_text'],'pc_event_index':pr['jp_event_index'],'pc_status':pr['status'],'pc_jp_text':pr['jp_text'],'pc_zh_text':pr['zh_text'],'match_kind':'exact-sequence-v2'})
                safe_pairs+=1;sp+=1;statusc[pr['status']]+=1
            else:
                u=dict(sr);u['reason']='pc-match-not-safe';unmatched.append(u)
        scene_stats.append({'scene':scene,'sw':len(srows),'pc':len(prows),'equal_pairs':len(exactmap),'safe_pairs':sp})
    OUTDIR.mkdir(parents=True,exist_ok=True)
    mf=OUTDIR/'safe_matches.tsv';fields=['scene','sw_code_index','sw_info_data','sw_trailing_hex','sw_jp_text','sw_jp_norm','sw_en_text','pc_event_index','pc_status','pc_jp_text','pc_zh_text','match_kind']
    with mf.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(matched)
    uf=OUTDIR/'unmatched.tsv';ufields=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex','reason']
    with uf.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=ufields,delimiter='\t');w.writeheader();w.writerows(unmatched)
    sf=OUTDIR/'scene_stats.tsv'
    with sf.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['scene','sw','pc','equal_pairs','safe_pairs'],delimiter='\t');w.writeheader();w.writerows(scene_stats)
    summ={'switch_messages':len(sw),'pc_total_rows':len(pc0),'pc_jp_rows_used':len(pc),'switch_scenes':len(sw_by),'pc_scenes':len(pc_by),'scene_intersection':len(set(sw_by)&set(pc_by)),'switch_only_scenes':sorted(set(sw_by)-set(pc_by)),'exact_sequence_pairs':equal_pairs,'safe_pc_mappings':safe_pairs,'exact_pair_coverage_all_switch':round(equal_pairs/len(sw)*100,3),'safe_mapping_coverage_all_switch':round(safe_pairs/len(sw)*100,3),'unmatched_or_unsafe':len(unmatched),'by_pc_status':dict(statusc)}
    (OUTDIR/'summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summ,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
