from pathlib import Path
import json,struct,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');O=R/'05_build/keyword_fix6';O.mkdir(parents=True,exist_ok=True)
orig=json.loads((R/'05_build/keyword_fix5/keyword_en.json').read_text(encoding='utf-8'))
zh=json.loads((R/'05_build/keyword_fix5/keyword_zh_full.json').read_text(encoding='utf-8'))
Z={r['index']:r for r in zh}
def ps(s):
 raw=s.encode('utf-16le');return struct.pack('<H',len(raw)//2)+raw+b'\0\0'
chunks=[];rows=[]
for r in orig:
 idx=r['index'];z=Z[idx];sort_key=r['title'];title=z['title'];desc=z['description']
 display=f'$C[960000]{title}$C[000000]';body=f'$C[960000]{title}$C[000000]$d{desc}'
 fields=[sort_key,display,body,body]
 payload=b''.join(ps(x) for x in fields);size=10+len(payload)
 chunks.append(struct.pack('<5H',size,r['total'],r['zero'],r['magic'],idx)+payload)
 rows.append({'index':idx,'sort_key':sort_key,'visible_title':title,'description':desc,'record_size':size})
out=b''.join(chunks);dst=O/'_KEYWORD_CHS';dst.write_bytes(out)
# independent parse + grouping simulation copied from game behavior: strip leading The, case-fold ASCII, split after 6 same-initial entries.
def parse(b):
 off=0;rr=[]
 while off<len(b):
  st=off;size,total,z,magic,idx=struct.unpack_from('<5H',b,off);off+=10;ss=[]
  for _ in range(4):
   n=struct.unpack_from('<H',b,off)[0];off+=2;s=b[off:off+n*2].decode('utf-16le');off+=n*2;term=struct.unpack_from('<H',b,off)[0];off+=2;assert term==0;ss.append(s)
  assert off-st==size;rr.append((idx,total,z,magic,ss))
 return rr
rr=parse(out);bad=[]
for idx,total,zero,magic,ss in rr:
 zrow=Z[idx];exp0=orig[idx-1]['title'];exp1=f"$C[960000]{zrow['title']}$C[000000]";expb=f"$C[960000]{zrow['title']}$C[000000]$d{zrow['description']}"
 if (total,zero,magic)!=(357,0,27) or ss != [exp0,exp1,expb,expb]:bad.append(idx)
def initial(s):
 if s.lower().startswith('the ') and len(s)>4:s=s[4:]
 c=s[0] if s else ''
 return c.upper() if 'a'<=c<='z' or 'A'<=c<='Z' else c
groups=[];prev=None;cnt=0
for r in orig:
 k=initial(r['title'])
 if k!=prev or cnt==6:groups.append(k);prev=k;cnt=1
 else:cnt+=1
# compare original grouping exactly because sort keys restored
origgroups=list(groups)
# visible English residue only fields1/2/3: reject exact old titles/descriptions
res=[]
for (idx,_,_,_,ss),o in zip(rr,orig):
 olddesc=o['body1'].split('$d',1)[1] if '$d' in o['body1'] else o['body1']
 if o['title'] in ss[1] or olddesc.strip() in ss[2]:res.append(idx)
rep={'records':len(rr),'size':len(out),'sha256':hashlib.sha256(out).hexdigest().upper(),'parse_bad':bad,'visible_old_english_residue':res,'sort_keys_restored':all(rr[i][4][0]==orig[i]['title'] for i in range(71)),'directory_groups':len(groups),'directory_group_keys':groups}
(O/'keyword_fix6_qa.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));raise SystemExit(1 if bad or res or len(groups)>30 else 0)
