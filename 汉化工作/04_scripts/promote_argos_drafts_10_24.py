from pathlib import Path
import csv,re,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
D=ROOT/'03_text/translated/manual_batches_v11'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def strip_controls_start(s):
 # controls that may appear before opening punctuation
 m=re.match(r'^((?:\$S(?:U)?\d{3}(?:,\d+)?|\$W(?:\([^)]*\))?|\$w|\\n|[\u3000\s])*)',s)
 return m.group(1),s[len(m.group(1)):]
def fix_structure(jp,z):
 z=z.strip()
 pre,rest=strip_controls_start(jp)
 # preserve leading controls if draft translator did not already carry them
 if pre and not z.startswith(pre): z=pre+z
 # dialogue / thought brackets are semantically meaningful in JP slot and PC Chinese style
 # determine first visible punctuation after leading controls
 _,jr=strip_controls_start(jp)
 if jr.startswith('「') and '「' not in z[:len(pre)+2]:
  # insert after controls
  zp,zr=strip_controls_start(z); z=zp+'「'+zr
 if jr.startswith('（') and '（' not in z[:len(pre)+2] and '(' not in z[:len(pre)+2]:
  zp,zr=strip_controls_start(z); z=zp+'（'+zr
 if jp.rstrip().endswith('」') and not z.rstrip().endswith('」'): z=z.rstrip(' .。')+'」'
 if jp.rstrip().endswith('）') and not (z.rstrip().endswith('）') or z.rstrip().endswith(')')): z=z.rstrip(' .。')+'）'
 # normalize common English residue that is intentional screen gag separately; otherwise punctuation
 z=z.replace('，', '，').replace('?', '？').replace('!', '！')
 z=z.replace(' . . . . . . .', '…').replace('. . . . .', '…').replace('. . . .', '…')
 return z
stats={}
for n in range(10,25):
 src=rd(D/f'source_{n:02d}.tsv'); dr=rd(D/f'draft_{n:02d}.tsv'); assert len(src)==len(dr)
 out=[]
 for s,d in zip(src,dr):
  assert (s['scene'],s['code_index'])==(d['scene'],d['code_index'])
  out.append({'scene':s['scene'],'code_index':s['code_index'],'zh_body':fix_structure(s['body_jp'],d['zh_body'])})
 with (D/f'target_{n:02d}.tsv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['scene','code_index','zh_body'],delimiter='\t');w.writeheader();w.writerows(out)
 stats[f'{n:02d}']=len(out)
print(json.dumps(stats,indent=2))
