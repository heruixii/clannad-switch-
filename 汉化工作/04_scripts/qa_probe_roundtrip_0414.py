from pathlib import Path
import json,csv,struct
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
P=ROOT/'03_text/switch_inject/probe/SEEN0414.roundtrip.json'; O=ROOT/'03_text/switch_export/script_json/SEEN0414.json'
def raw(c):
 b=bytearray()
 for x in c.get('paramDatas',[]):
  v=str(x.get('value',''))
  if v.startswith('0x'):b.extend(bytes.fromhex(v[2:].replace(' ','')))
 return bytes(b)
def lp(b,p):
 n=struct.unpack_from('<H',b,p)[0];p+=2;s=b[p:p+2*n].decode('utf-16le');p+=2*n;assert b[p:p+2]==b'\0\0';return s,p+2
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
M={(r['scene'],int(r['code_index'])):r for r in rd(ROOT/'03_text/translated/message_targets_complete_v12.tsv')}
S={(r['scene'],int(r['code_index'])):r for r in rd(ROOT/'03_text/translated/select_targets_complete_v2.tsv')}
d=json.loads(P.read_text(encoding='utf-8-sig'));orig=json.loads(O.read_text(encoding='utf-8-sig'))
assert len(d['codes'])==len(orig['codes'])
opdiff=sum(a.get('opcode')!=b.get('opcode') for a,b in zip(d['codes'],orig['codes']))
mc=ms=mj=se=ss=sj=0;errs=[]
for i,(c,oc) in enumerate(zip(d['codes'],orig['codes'])):
 if c.get('opcode')=='MESSAGE':
  b=raw(c);j,p=lp(b,0);z,p=lp(b,p);ob=raw(oc);oj,op=lp(ob,0);oe,op=lp(ob,op);mc+=1
  target=M[('SEEN0414',i)]['zh_text'].replace('\\n','\n').replace('\\r','\r').replace('\\t','\t')
  mj+=j==oj;ms+=z==target
  if j!=oj or z!=target:errs.append(('M',i,j==oj,z==target,z,target))
 if c.get('opcode')=='SELECT':
  b=raw(c);j,p=lp(b,8);z,p=lp(b,p);ob=raw(oc);oj,op=lp(ob,8);oe,op=lp(ob,op);se+=1
  target=S[('SEEN0414',i)]['zh_text']
  sj+=j==oj;ss+=z==target
  if j!=oj or z!=target:errs.append(('S',i,j==oj,z==target,z,target))
print({'codes':len(d['codes']),'opcode_diff':opdiff,'messages':mc,'jp_exact':mj,'message_target_exact':ms,'selects':se,'select_jp_exact':sj,'select_target_exact':ss,'errors':len(errs)})
print(errs[:5])
