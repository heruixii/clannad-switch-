from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SAFE=ROOT/'03_text/matched/switch_pc_v11/safe_matches.tsv'; SW=ROOT/'03_text/switch_extracted/switch_messages.tsv'; D=ROOT/'03_text/translated/manual_batches_v11'; OUT=ROOT/'03_text/translated/message_targets_complete_v12.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def clean(s):return (s or '').replace('"','').replace('\r','').strip('\ufeff')
def pcparts(s):
 s=clean(s)
 if s.startswith('`') and '@' in s:return s[1:s.find('@')],s[s.find('@')+1:]
 m=re.match(r'^【([^】]+)】(.*)$',s,re.S)
 return (m.group(1),m.group(2)) if m else ('',s)
def swsp(s):return s[1:s.find('@')] if s.startswith('`') and '@' in s else ''
# learn speaker translation from safe PC text
safe=rd(SAFE); spcnt=collections.defaultdict(collections.Counter)
for r in safe:
 j=swsp(r['sw_jp_text']);z,_=pcparts(r['pc_zh_text'])
 if j and z:spcnt[j][z]+=1
spmap={j:c.most_common(1)[0][0] for j,c in spcnt.items()}
spmap.update({'ようへい':'阳平','風…':'风…','％Ｂ':'％Ｂ','クラスメイトたち':'同班同学们','勝平':'胜平','勝平・＊Ｂ':'胜平・＊Ｂ'})
rows=[];keys=set();stats=collections.Counter()
for r in safe:
 k=(r['scene'],r['sw_code_index']);j=swsp(r['sw_jp_text']);zsp,body=pcparts(r['pc_zh_text'])
 if j:
  zsp=zsp or spmap.get(j,j)
  target='`'+zsp+'@'+body
 else:target=body
 rows.append({'scene':k[0],'code_index':k[1],'source':'pc-safe:'+r['match_kind'],'jp_text':r['sw_jp_text'],'en_text':r['sw_en_text'],'zh_text':target});keys.add(k);stats['safe']+=1
# manual targets
for n in range(1,25):
 src=rd(D/f'source_{n:02d}.tsv'); tgt=rd(D/f'target_{n:02d}.tsv'); assert len(src)==len(tgt)
 for s,t in zip(src,tgt):
  assert (s['scene'],s['code_index'])==(t['scene'],t['code_index'])
  k=(s['scene'],s['code_index']); assert k not in keys
  zsp=s['speaker_zh'] or ''
  if zsp=='ようへい':zsp='阳平'
  if zsp=='風…':zsp='风…'
  # map composite pieces when possible
  if zsp:
   zsp='・'.join(spmap.get(x,x) for x in zsp.split('・'))
   target='`'+zsp+'@'+t['zh_body']
  else:target=t['zh_body']
  # TSV stores literal backslash escapes, exactly as extraction does
  rows.append({'scene':k[0],'code_index':k[1],'source':f'new-translation-b{n:02d}','jp_text':s['body_jp'] if not s['speaker_jp'] else '`'+s['speaker_jp']+'@'+s['body_jp'],'en_text':s['en_text'],'zh_text':target});keys.add(k);stats['manual']+=1
sw=rd(SW);swkeys={(r['scene'],r['code_index']) for r in sw}
missing=swkeys-keys;extra=keys-swkeys
assert not missing and not extra and len(rows)==len(sw)==len(keys),(len(rows),len(sw),len(keys),len(missing),len(extra))
rows.sort(key=lambda r:(r['scene'],int(r['code_index'])))
OUT.parent.mkdir(parents=True,exist_ok=True)
with OUT.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
print(json.dumps({'rows':len(rows),'unique_keys':len(keys),'safe':stats['safe'],'new_translation':stats['manual'],'missing':0,'extra':0,'speaker_map':len(spmap)},ensure_ascii=False,indent=2));print(OUT)
