from pathlib import Path
import csv,re,random
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'03_text/matched/pc_control_parallel_v3/strict_anchor_candidates.tsv'
OUT=ROOT/'03_text/matched/pc_control_parallel_v3/highconf_anchor_candidates.tsv'
R=list(csv.DictReader(open(SRC,encoding='utf-8-sig'),delimiter='\t'))
def body(s):
    s=s.strip(' \t\"');s=re.sub(r'^【[^】]+】','',s);return s.strip(' \t\"「」（）()')
def hans(s):return {c for c in body(s) if '\u3400'<=c<='\u9fff'}
def vars_(s):return set(re.findall(r'[＊%％][Ａ-ＺA-Z]|\d+',body(s)))
out=[]
for r in R:
    if r['reason']!='strict-anchor':continue
    sh=len(hans(r['jp_text'])&hans(r['zh_text']));vm=int(bool(vars_(r['jp_text'])&vars_(r['zh_text'])));fc=int(r['fp_pair_count']);jt=int(r['jp_fp_total']);fr=fc/max(jt,1)
    rare=(jt<=500 and fc>=3 and fr>=.5)
    high=bool(vm or rare or sh>=6)
    if high:
        q=dict(r);q.update(shared_han=sh,var_match=vm,fp_ratio=f'{fr:.6f}',high_reason='var' if vm else ('rare-fp' if rare else 'shared-han>=6'));out.append(q)
fields=list(out[0].keys()) if out else []
with open(OUT,'w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print('highconf',len(out),'blocks',len(set((r['scene'],r['block_id']) for r in out)),'var',sum(r['high_reason']=='var' for r in out),'rare',sum(r['high_reason']=='rare-fp' for r in out),'han6',sum(r['high_reason']=='shared-han>=6' for r in out));print('trap1516',[(r['jp_event_index'],r['zh_event_index']) for r in out if r['scene']=='SEEN1516' and r['jp_event_index'] in ('152','153')]);print('trap6502',[(r['jp_event_index'],r['zh_event_index']) for r in out if r['scene']=='SEEN6502' and r['jp_event_index'] in ('75','76')]);print('out',OUT)
rng=random.Random(20260914);rng.shuffle(out)
for n,r in enumerate(out[:55],1):
    print(f"[{n}] {r['scene']} b{r['block_id']} {r['high_reason']} {r['jp_event_index']}->{r['zh_event_index']} sh={r['shared_han']} fp={r['fp_pair_count']}/{r['jp_fp_total']}")
    print(' JP:',r['jp_text']);print(' ZH:',r['zh_text'])
