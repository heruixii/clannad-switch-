from pathlib import Path
import json,csv,struct,collections,hashlib
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
RT=ROOT/'03_text/switch_inject/roundtrip_json'; ORIG=ROOT/'03_text/switch_export/script_json'
def raw(c):
 b=bytearray()
 for x in c.get('paramDatas',[]):
  v=str(x.get('value',''))
  if v.startswith('0x'):b.extend(bytes.fromhex(v[2:].replace(' ','')))
 return bytes(b)
def lp(b,p):
 if p+2>len(b):raise ValueError('len')
 n=struct.unpack_from('<H',b,p)[0];p+=2;e=p+2*n
 if e+2>len(b):raise ValueError('short')
 s=b[p:e].decode('utf-16le');assert b[e:e+2]==b'\0\0';return s,e+2
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
M={(r['scene'],int(r['code_index'])):r for r in rd(ROOT/'03_text/translated/message_targets_complete_v12.tsv')}
S={(r['scene'],int(r['code_index'])):r for r in rd(ROOT/'03_text/translated/select_targets_complete_v2.tsv')}
st=collections.Counter();errs=[];seenM=set();seenS=set();files=sorted(RT.glob('SEEN*.json'))
for fp in files:
 sc=fp.stem;op=ORIG/fp.name
 if not op.exists():errs.append((sc,'missing_orig'));continue
 d=json.loads(fp.read_text(encoding='utf-8-sig'));o=json.loads(op.read_text(encoding='utf-8-sig'))
 if len(d.get('codes',[]))!=len(o.get('codes',[])):errs.append((sc,'code_count',len(d['codes']),len(o['codes'])));continue
 st['scenes']+=1;st['codes']+=len(d['codes'])
 for i,(c,oc) in enumerate(zip(d['codes'],o['codes'])):
  if c.get('opcode')!=oc.get('opcode'):errs.append((sc,i,'opcode',oc.get('opcode'),c.get('opcode')));continue
  st['opcode_equal']+=1
  if c.get('opcode')=='MESSAGE':
   b=raw(c);j,p=lp(b,0);z,p=lp(b,p); ob=raw(oc);oj,q=lp(ob,0);oe,q=lp(ob,q);k=(sc,i)
   st['message']+=1;seenM.add(k)
   if j!=oj:errs.append((sc,i,'message_jp_changed',oj,j))
   else:st['message_jp_exact']+=1
   target=M[k]['zh_text'].replace('\\n','\n').replace('\\r','\r').replace('\\t','\t')
   if z!=target:errs.append((sc,i,'message_zh_mismatch',target,z))
   else:st['message_zh_exact']+=1
  elif c.get('opcode')=='SELECT':
   b=raw(c);j,p=lp(b,8);z,p=lp(b,p);ob=raw(oc);oj,q=lp(ob,8);oe,q=lp(ob,q);k=(sc,i)
   st['select']+=1;seenS.add(k)
   if j!=oj:errs.append((sc,i,'select_jp_changed',oj,j))
   else:st['select_jp_exact']+=1
   target=S[k]['zh_text'].replace('\\n','\n').replace('\\r','\r').replace('\\t','\t')
   if z!=target:errs.append((sc,i,'select_zh_mismatch',target,z))
   else:st['select_zh_exact']+=1
st['missing_message_targets']=len(set(M)-seenM);st['missing_select_targets']=len(set(S)-seenS)
summary={'files':len(files),**dict(st),'errors':len(errs)}
print(json.dumps(summary,ensure_ascii=False,indent=2));print('ERRS',errs[:20])
assert not errs and seenM==set(M) and seenS==set(S)
(ROOT/'03_text/switch_inject/full_roundtrip_qa.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
