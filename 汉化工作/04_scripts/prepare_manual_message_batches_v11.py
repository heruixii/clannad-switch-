from pathlib import Path
import csv,re,collections,json,math
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
U=ROOT/'03_text/matched/switch_pc_v11/unmatched.tsv'; T=ROOT/'03_text/translated/message_targets_v10.tsv'; OUT=ROOT/'03_text/translated/manual_batches_v11'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sp(s):return s[1:s.find('@')] if s.startswith('`') and '@' in s else ''
def body(s):return s.split('@',1)[1] if s.startswith('`') and '@' in s else s
spcnt=collections.defaultdict(collections.Counter)
for r in rd(T):
 a,b=sp(r['jp_text']),sp(r['zh_text'])
 if a and b:spcnt[a][b]+=1
spmap={a:c.most_common(1)[0][0] for a,c in spcnt.items()}
spmap.update({'％Ｂ':'％Ｂ','クラスメイトたち':'同班同学们','勝平・＊Ｂ':'胜平・＊Ｂ','春原・渚':'春原・渚','杏・＊Ｂ':'杏・＊Ｂ','＊Ｂ・杏':'＊Ｂ・杏'})
def mapsp(a):
 if not a:return ''
 if a in spmap:return spmap[a]
 parts=a.split('・')
 if len(parts)>1:return '・'.join(spmap.get(x,x) for x in parts)
 return a
rows=rd(U);OUT.mkdir(parents=True,exist_ok=True);bs=120;stats=collections.Counter();unknown=collections.Counter();ctrl=re.compile(r'\$S|\$W|\$w|\$\[')
for i in range(0,len(rows),bs):
 chunk=rows[i:i+bs];out=[]
 for r in chunk:
  a=sp(r['jp_text']);z=mapsp(a)
  if a and z==a and re.search(r'[\u3040-\u30ff]',a):unknown[a]+=1
  b=body(r['jp_text']);stats['dialogue' if a else 'narration']+=1;stats['controls']+=bool(ctrl.search(b))
  out.append({'scene':r['scene'],'code_index':r['code_index'],'speaker_jp':a,'speaker_zh':z,'body_jp':b,'en_text':r['en_text']})
 p=OUT/f'source_{i//bs+1:02d}.tsv'
 with p.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
print(json.dumps({'rows':len(rows),'batch_size':bs,'batches':math.ceil(len(rows)/bs),'stats':dict(stats),'unknown_speakers':dict(unknown)},ensure_ascii=False,indent=2));print(OUT)
