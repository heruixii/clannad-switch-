from pathlib import Path
import json, collections
w=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
a=w/'03_text/switch_work/script_probe/SCRIPT.PAK_unpacked/SEEN0414'
b=w/'03_text/switch_roundtrip/SEEN0414'
ba=a.read_bytes(); bb=b.read_bytes()
d=[i for i,(x,y) in enumerate(zip(ba,bb)) if x!=y]
print('binary_diff_bytes',len(d),'of',len(ba))
if d:
 print('first',d[:80]); print('last',d[-20:])
 runs=[]; s=p=d[0]
 for x in d[1:]:
  if x==p+1:p=x
  else:runs.append((s,p));s=p=x
 runs.append((s,p))
 print('diff_runs',len(runs)); print('first_runs',runs[:40])
 print('byte_pairs_top',collections.Counter((ba[i],bb[i]) for i in d).most_common(20))
j1=json.loads((w/'03_text/switch_export/script_json/SEEN0414.json').read_text(encoding='utf-8-sig'))
j2=json.loads((w/'03_text/switch_roundtrip/SEEN0414.reexport.json').read_text(encoding='utf-8-sig'))
print('json_equal',j1==j2)
print('code_counts',len(j1.get('codes',[])),len(j2.get('codes',[])))
def walk(x,y,path=''):
 if type(x)!=type(y): return [(path,repr(x)[:100],repr(y)[:100])]
 if isinstance(x,dict):
  out=[]
  for k in sorted(set(x)|set(y)):
   if k not in x or k not in y:out.append((path+'/'+k,repr(x.get(k,'<missing>'))[:100],repr(y.get(k,'<missing>'))[:100]))
   elif x[k]!=y[k]:out.extend(walk(x[k],y[k],path+'/'+k))
   if len(out)>=30:return out[:30]
  return out
 if isinstance(x,list):
  out=[]
  if len(x)!=len(y):out.append((path+'/len',str(len(x)),str(len(y))))
  for i,(u,v) in enumerate(zip(x,y)):
   if u!=v:out.extend(walk(u,v,f'{path}/{i}'))
   if len(out)>=30:return out[:30]
  return out
 return [(path,repr(x),repr(y))]
for row in walk(j1,j2)[:30]:print('JSON_DIFF\t'+'\t'.join(row))
