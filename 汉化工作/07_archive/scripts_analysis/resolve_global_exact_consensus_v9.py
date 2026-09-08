from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); U=ROOT/'03_text/matched/switch_pc_v9/unmatched.tsv'; PC=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'; OUT=ROOT/'03_text/matched/switch_pc_v9/global_exact_consensus.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'};SUPS=[ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_forced.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_equal_strict.tsv',ROOT/'03_text/matched/pc_control_parallel_v4/review_signature_manual_accept.tsv']
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
pc=rd(PC);trusted={};jp={}
for r in pc:
 if (r.get('jp_event_index') or '').isdigit() and r.get('jp_text'):
  k=(r['scene'],int(r['jp_event_index']));jp[k]=r['jp_text']
  if r['status'] in SAFE and r.get('zh_text'):trusted[k]=(r['zh_text'],r['status'])
for p in SUPS:
 for r in rd(p):
  if 'accepted' in r and r['accepted'] not in ('1',''):continue
  k=(r['scene'],int(r['jp_event_index']))
  if r.get('zh_text'):trusted.setdefault(k,(r['zh_text'],r.get('status','supp')))
idx=collections.defaultdict(list)
for k,(zh,st) in trusted.items():idx[pn(jp[k])].append((k,zh,st))
out=[];stats=collections.Counter()
for r in rd(U):
 t=sn(r['jp_text']);c=idx.get(t,[])
 if not c:continue
 zhs={x[1] for x in c}
 if len(c)==1 or len(zhs)==1:
  k,zh,st=c[0];kind='global-exact-unique' if len(c)==1 else 'global-exact-consensus'
  out.append({'scene':r['scene'],'sw_code_index':r['code_index'],'sw_jp_text':r['jp_text'],'sw_en_text':r['en_text'],'pc_scene':k[0],'pc_event_index':k[1],'pc_status':st,'pc_jp_text':jp[k],'pc_zh_text':zh,'match_kind':kind,'candidate_count':len(c)});stats[kind]+=1
 else:stats['conflicting_multi']+=1
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 fields=list(out[0]) if out else [];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps(dict(stats),indent=2));print('rows',len(out));print(OUT)
