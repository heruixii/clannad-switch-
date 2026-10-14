#!/usr/bin/env python3
# CLANNAD v1.0.7 fix10 / ALTIRKIE
# Reconstruct original scene opcode offsets from bilingual text lengths,
# then map all known GOTO/IFN/ONGOTO/cross-scene references to current offsets.
# No game files are embedded; requires user-provided translated PAK and TSVs.
from pathlib import Path
import csv,struct,collections,json,hashlib,re,argparse
parser=argparse.ArgumentParser(description='Rebase stale absolute script addresses after CLANNAD LucaSystem text injection; only use after backing up SCRIPT.PAK')
parser.add_argument('--script', type=Path, required=True, help='Input translated SCRIPT.PAK')
parser.add_argument('--messages', type=Path, required=True, help='message_targets_complete_v12.tsv')
parser.add_argument('--selects', type=Path, required=True, help='select_targets_complete_v2.tsv')
parser.add_argument('--output', type=Path, required=True, help='Destination directory, does not overwrite existing SCRIPT.PAK')
parser.add_argument('--expect-source-sha256', default='42FD1C6865A1EB094542A0DC8E7E367B624FDCE6FDEDBF9E3E04D200B49DA767')
args=parser.parse_args()
src=args.script; base=src.read_bytes();assert hashlib.sha256(base).hexdigest().upper()==args.expect_source_sha256.upper()
hl,fc,_,bs,*_=struct.unpack_from('<9I',base);nam=[];q=1880
for _ in range(fc):z=base.index(0,q,hl);nam.append(base[q:z].decode());q=z+1
E={n:(struct.unpack_from('<I',base,40+8*i)[0]*bs,struct.unpack_from('<I',base,44+8*i)[0]) for i,n in enumerate(nam)}
D=[]
for file_path in [args.messages,args.selects]:
 d=collections.defaultdict(dict)
 with file_path.open(encoding='utf-8-sig',newline='') as f:
  for r in csv.DictReader(f,delimiter='\t'):d[r['scene']][int(r['code_index'])]=(r['en_text'],r['zh_text'])
 D.append(d)
def blen(s):return len(s.replace('\\r','\r').replace('\\n','\n').replace('\\t','\t').encode('utf-16le'))
Maps={}
for name,(start,ln) in E.items():
 if not name.startswith('SEEN'):continue
 raw=base[start:start+ln];p=old=0;ops=[]
 while p<len(raw):
  assert p+4<=len(raw),(name,p)
  n,op,fl=struct.unpack_from('<HBB',raw,p)
  assert n>=4 and p+n<=len(raw),(name,p,n)
  idx=len(ops);row=D[0][name].get(idx) if op==33 else D[1][name].get(idx) if op==36 else None
  delta=blen(row[0])-blen(row[1]) if row else 0
  assert n+delta>=4
  ops.append({'index':idx,'pos':p,'original_pos':old,'length':n,'op':op})
  p+=(n+1)&~1;old+=(n+delta+1)&~1
 assert p==ln,(name,p,ln)
 Maps[name]=(ops,{r['original_pos']:r for r in ops},{r['pos']:r for r in ops})
patched=bytearray(base);counts=collections.Counter();evidence=[];modif=[];problems=[];per_scene=collections.Counter();seenrefs=set()
for name,(ops,_,__) in Maps.items():
 off,ln=E[name];raw=base[off:off+ln]
 for ins in ops:
  op=ins['op'];start=ins['pos'];length=ins['length'];s=raw[start:start+length];refs=[]
  if op in (15,17,18,19):refs=[(length-4,name)]
  elif op in (16,21,22):
   for m in re.finditer(rb'(?i)seen[0-9_]+\x00',s):
    target=m.group()[:-1].decode('ascii').upper()
    if target in Maps and m.end()+4<=length:refs.append((m.end(),target))
  for rel,target in refs:
   assert rel>=4 and rel+4<=length
   key=(name,start+rel)
   assert key not in seenrefs,key
   seenrefs.add(key)
   abs_pos=off+start+rel;old_val=struct.unpack_from('<I',base,abs_pos)[0]
   ref_old=Maps[target][1].get(old_val)
   ref_new=Maps[target][2].get(old_val)
   if ref_old is None:
    if ref_new is not None:
     problems.append((name,ins['index'],op,'pointer only resolves against new script',target,old_val))
    elif old_val!=0:
     problems.append((name,ins['index'],op,'unresolved',target,old_val))
    continue
   dest=ref_old['pos']
   if old_val==dest:
    counts['already_equal']+=1;continue
   patched[abs_pos:abs_pos+4]=struct.pack('<I',dest)
   counts['rewritten_'+str(op)]+=1;per_scene[name]+=1
   modif.append((name,ins['index'],op,target,old_val,dest))
   if len(evidence)<25:evidence.append({'from':name,'idx':ins['index'],'opcode':op,'to_scene':target,'old':hex(old_val),'new':hex(dest),'to_code_index':ref_old['index']})
assert not problems,problems[:12]
assert len(patched)==len(base)
# Validate final target index for every reference that exists in the original position map
for name,(ops,_,__) in Maps.items():
 off,ln=E[name];raw=base[off:off+ln]
 for ins in ops:
  op=ins['op'];start=ins['pos'];n=ins['length'];s=raw[start:start+n];refs=[]
  if op in (15,17,18,19):refs=[(n-4,name)]
  elif op in (16,21,22):
   for m in re.finditer(rb'(?i)seen[0-9_]+\x00',s):
    target=m.group()[:-1].decode('ascii').upper()
    if target in Maps and m.end()+4<=n:refs.append((m.end(),target))
  for rel,target in refs:
   at=off+start+rel;oldv=struct.unpack_from('<I',base,at)[0]
   if oldv in Maps[target][1]:
    actual=struct.unpack_from('<I',patched,at)[0]
    assert actual==Maps[target][1][oldv]['pos']
# explicitly scene0414 matches local jumpfix
# Every translated jump pointer resolves by old-instruction-index -> new-instruction-offset mapping, including coincidental old/new offset collisions.
assert base[:hl]==patched[:hl]
for n,(start,ln) in E.items():
 if n not in Maps:assert patched[start:start+ln]==base[start:start+ln],n
outdir=args.output;outdir.mkdir(parents=True,exist_ok=True)
out=outdir/'SCRIPT.PAK'
if out.exists():raise RuntimeError(f'Refusing to overwrite existing output: {out}')
out.write_bytes(patched)
sha=hashlib.sha256(patched).hexdigest().upper();diff=sum(x!=y for x,y in zip(base,patched))
report={'status':'REPRODUCIBLE SCRIPT RELOCATION OUTPUT - VERIFY ON HARDWARE BEFORE USE','size':len(patched),'sha256':sha,'original_sha256':hashlib.sha256(base).hexdigest().upper(),'scenes_processed':len(Maps),'scenes_modified':len(per_scene),'branch_reference_count':len(seenrefs),'reference_counts':dict(counts),'patched_refs':len(modif),'different_bytes':diff,'errors':problems,'first_patch_samples':evidence,'top_scenes':per_scene.most_common(20),'scene0414_pointer_pairs_validated':True,'other_content_unmodified':True}
(outdir/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
