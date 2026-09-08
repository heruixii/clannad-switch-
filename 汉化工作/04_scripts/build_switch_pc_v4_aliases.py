from pathlib import Path
import csv,json,collections,re,difflib
ROOT=Path(__file__).resolve().parents[1]
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'
PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
BASE=ROOT/'03_text/matched/switch_pc_v3/safe_matches.tsv'
OUT=ROOT/'03_text/matched/switch_pc_v4'
ALIASES={
 'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800',
 'SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400',
 'SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802',
 'SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100',
}
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]'); STYLE=re.compile(r'\$S(?:U)?\d{3}')
def rd(p):
    with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sn(s):
    s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
    if s.startswith('`'):
        at=s.find('@',1)
        if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
    return STYLE.sub('',RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)).replace('$W','')
def pn(s):return (s or '').replace('\r','')
def safe(r):return bool(r.get('zh_text')) and bool(r.get('jp_text')) and (r.get('jp_event_index') or '').isdigit() and not (r.get('status') or '').startswith('review')
def main():
    sw=rd(SW); pc=rd(PC); base=rd(BASE)
    sw_by=collections.defaultdict(list); pc_by=collections.defaultdict(list)
    for r in sw:sw_by[r['scene']].append(r)
    for r in pc:
        if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):pc_by[r['scene']].append(r)
    for v in sw_by.values():v.sort(key=lambda r:int(r['code_index']))
    for v in pc_by.values():v.sort(key=lambda r:int(r['jp_event_index']))
    used={(r['scene'],r['sw_code_index']) for r in base}
    additions=[]; stats=[]; statusc=collections.Counter()
    for ss,ps in ALIASES.items():
        sr=sw_by.get(ss,[]); pr=pc_by.get(ps,[])
        # exact normalized text occurrence maps; only use unique-in-parent text for strictness,
        # or same multiplicity/order when occurrence counts equal.
        so=collections.defaultdict(list); po=collections.defaultdict(list)
        for i,r in enumerate(sr):so[sn(r['jp_text'])].append((i,r))
        for j,r in enumerate(pr):po[pn(r['jp_text'])].append((j,r))
        exact=0; safeadd=0; unique=0; repeat=0
        candidates=[]
        for t,slist in so.items():
            plist=po.get(t,[])
            if not plist:continue
            if len(slist)==1 and len(plist)==1:
                candidates.append((slist[0],plist[0],'alias-unique'));unique+=1
            elif len(slist)==len(plist) and len(slist)<=64:
                for a,b in zip(slist,plist):candidates.append((a,b,'alias-repeat-order'));repeat+=1
        # enforce monotonic pc index over switch order; do not accept crossings
        candidates.sort(key=lambda x:x[0][0])
        last=-1
        for (si,s),(pj,p),kind in candidates:
            if pj<=last:continue
            last=pj;exact+=1
            key=(ss,s['code_index'])
            if key in used or not safe(p):continue
            additions.append({'scene':ss,'sw_code_index':s['code_index'],'sw_info_data':s['info_data'],'sw_trailing_hex':s['trailing_hex'],'sw_jp_text':s['jp_text'],'sw_jp_norm':sn(s['jp_text']),'sw_en_text':s['en_text'],'pc_event_index':p['jp_event_index'],'pc_status':p['status'],'pc_jp_text':p['jp_text'],'pc_zh_text':p['zh_text'],'match_kind':kind,'pc_scene':ps})
            used.add(key);safeadd+=1;statusc[p['status']]+=1
        stats.append({'switch_scene':ss,'pc_scene':ps,'sw_messages':len(sr),'pc_messages':len(pr),'exact_monotonic':exact,'safe_added':safeadd,'unique_candidates':unique,'repeat_candidates':repeat})
    # normalize base rows to output schema, add pc_scene same as scene
    rows=[]
    for r in base:
        x=dict(r);x['pc_scene']=r['scene'];rows.append(x)
    rows.extend(additions);rows.sort(key=lambda r:(r['scene'],int(r['sw_code_index'])))
    OUT.mkdir(parents=True,exist_ok=True)
    fields=['scene','sw_code_index','sw_info_data','sw_trailing_hex','sw_jp_text','sw_jp_norm','sw_en_text','pc_scene','pc_event_index','pc_status','pc_jp_text','pc_zh_text','match_kind']
    with (OUT/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(rows)
    with (OUT/'alias_stats.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(stats[0]),delimiter='\t');w.writeheader();w.writerows(stats)
    # unmatched against all switch messages
    allkeys={(r['scene'],r['code_index']) for r in sw}; matchedkeys={(r['scene'],r['sw_code_index']) for r in rows}
    swmap={(r['scene'],r['code_index']):r for r in sw}; un=[]
    for k in sorted(allkeys-matchedkeys,key=lambda x:(x[0],int(x[1]))):un.append(swmap[k])
    with (OUT/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:
        fs=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex'];w=csv.DictWriter(f,fieldnames=fs,delimiter='\t');w.writeheader();w.writerows(un)
    summ={'base_v3_safe':len(base),'alias_safe_added':len(additions),'v4_safe_total':len(rows),'switch_messages':len(sw),'safe_coverage':round(100*len(rows)/len(sw),3),'remaining_unmatched':len(un),'alias_stats':stats,'added_by_status':dict(statusc)}
    (OUT/'summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summ,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
