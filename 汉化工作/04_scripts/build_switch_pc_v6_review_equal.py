from pathlib import Path
import csv,json,collections,re,difflib
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'
PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
SUP=ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv'
SUP2=ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv'
OUT=ROOT/'03_text/matched/switch_pc_v6'
ALIASES={'SEEN7601':'SEEN7600','SEEN6810':'SEEN6800','SEEN6811':'SEEN6800','SEEN7401':'SEEN7400','SEEN7401_2':'SEEN7400','SEEN7401_3':'SEEN7400','SEEN7402':'SEEN7400','SEEN6800_1':'SEEN6800','SEEN6800_2':'SEEN6800','SEEN6802_1':'SEEN6802','SEEN7501':'SEEN7500','SEEN7102':'SEEN7100','SEEN7103':'SEEN7100'}
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
RUBY=re.compile(r'\$\[([^$\]]+)\$/([^$\]]+)\$\]');STYLE=re.compile(r'\$S(?:U)?\d{3}')
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sn(s):
 s=(s or '').replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
 if s.startswith('`'):
  at=s.find('@',1)
  if 1<at<=40:s='【'+s[1:at]+'】'+s[at+1:]
 return STYLE.sub('',RUBY.sub(lambda m:m.group(1)+'（'+m.group(2)+'）',s)).replace('$W','')
def pn(s):return (s or '').replace('\r','')

def main():
 sw=rd(SW); pc0=rd(PC); sup=rd(SUP); sup2=rd(SUP2)
 # pc event rows, one object per JP event. Start from all JP rows, attach Chinese when trusted.
 bykey={}
 for r in pc0:
  if not (r.get('jp_event_index') or '').isdigit() or not r.get('jp_text'):continue
  k=(r['scene'],int(r['jp_event_index']))
  e=bykey.setdefault(k,{'scene':r['scene'],'jp_event_index':int(r['jp_event_index']),'jp_text':r['jp_text'],'zh_text':'','status':''})
  if r['status'] in SAFE and r.get('zh_text'):
   e['zh_text']=r['zh_text'];e['status']=r['status']
 for r in sup:
  if r.get('accepted')!='1':continue
  k=(r['scene'],int(r['jp_event_index']))
  e=bykey.get(k)
  if e and not e['zh_text']:
   e['zh_text']=r['zh_text'];e['status']='review-forced'
 for r in sup2:
  k=(r['scene'],int(r['jp_event_index']))
  e=bykey.get(k)
  if e and not e['zh_text']:
   e['zh_text']=r['zh_text'];e['status']='review-equal-strict'
 pc_by=collections.defaultdict(list)
 for e in bykey.values():pc_by[e['scene']].append(e)
 for v in pc_by.values():v.sort(key=lambda x:x['jp_event_index'])
 sw_by=collections.defaultdict(list)
 for r in sw:sw_by[r['scene']].append(r)
 for v in sw_by.values():v.sort(key=lambda x:int(x['code_index']))
 matches=[]; stats=[]; kinds=collections.Counter(); statuses=collections.Counter()
 for ss,srows in sorted(sw_by.items()):
  ps=ALIASES.get(ss,ss);prows=pc_by.get(ps,[])
  if not prows:continue
  a=[sn(r['jp_text']) for r in srows]; b=[pn(r['jp_text']) for r in prows]
  mapping={};mk={}
  if ss not in ALIASES:
   sm=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
   for block in sm.get_matching_blocks():
    for k in range(block.size):mapping[block.a+k]=block.b+k;mk[block.a+k]='same-scene-sequence'
  else:
   so=collections.defaultdict(list);po=collections.defaultdict(list)
   for i,t in enumerate(a):so[t].append(i)
   for j,t in enumerate(b):po[t].append(j)
   cand=[]
   for t,sis in so.items():
    pjs=po.get(t,[])
    if len(sis)==1 and len(pjs)==1:cand.append((sis[0],pjs[0],'alias-unique'))
    elif len(sis)==len(pjs) and len(sis)<=64:
     cand.extend((si,pj,'alias-repeat-order') for si,pj in zip(sis,pjs))
   cand.sort();last=-1
   for si,pj,kd in cand:
    if pj<=last:continue
    mapping[si]=pj;mk[si]=kd;last=pj
  safe=0
  for si,pj in mapping.items():
   p=prows[pj]
   if not p['zh_text']:continue
   s=srows[si]
   matches.append({'scene':ss,'sw_code_index':s['code_index'],'sw_info_data':s['info_data'],'sw_trailing_hex':s['trailing_hex'],'sw_jp_text':s['jp_text'],'sw_jp_norm':a[si],'sw_en_text':s['en_text'],'pc_scene':ps,'pc_event_index':p['jp_event_index'],'pc_status':p['status'],'pc_jp_text':p['jp_text'],'pc_zh_text':p['zh_text'],'match_kind':mk[si]})
   safe+=1;kinds[mk[si]]+=1;statuses[p['status']]+=1
  stats.append({'scene':ss,'pc_scene':ps,'sw':len(srows),'pc':len(prows),'exact_mapped':len(mapping),'safe':safe})
 # unique switch key
 dup=[k for k,c in collections.Counter((r['scene'],r['sw_code_index']) for r in matches).items() if c>1]
 if dup:raise RuntimeError(f'duplicate switch keys {len(dup)}')
 OUT.mkdir(parents=True,exist_ok=True)
 fields=['scene','sw_code_index','sw_info_data','sw_trailing_hex','sw_jp_text','sw_jp_norm','sw_en_text','pc_scene','pc_event_index','pc_status','pc_jp_text','pc_zh_text','match_kind']
 matches.sort(key=lambda r:(r['scene'],int(r['sw_code_index'])))
 with (OUT/'safe_matches.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(matches)
 mkeys={(r['scene'],r['sw_code_index']) for r in matches};un=[r for r in sw if (r['scene'],r['code_index']) not in mkeys];un.sort(key=lambda r:(r['scene'],int(r['code_index'])))
 uf=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex']
 with (OUT/'unmatched.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=uf,delimiter='\t');w.writeheader();w.writerows(un)
 with (OUT/'scene_stats.tsv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(stats[0]),delimiter='\t');w.writeheader();w.writerows(stats)
 summ={'switch_messages':len(sw),'safe_total':len(matches),'safe_coverage':round(100*len(matches)/len(sw),3),'remaining':len(un),'review_forced_used':sum(1 for r in matches if r['pc_status']=='review-forced'),'review_equal_used':sum(1 for r in matches if r['pc_status']=='review-equal-strict'),'match_kinds':dict(kinds),'statuses':dict(statuses)}
 (OUT/'summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summ,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

