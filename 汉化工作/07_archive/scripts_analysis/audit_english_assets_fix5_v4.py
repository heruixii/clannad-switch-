from pathlib import Path
import csv,hashlib,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
rows=list(csv.DictReader((R/'05_build/ui_fullscan_english.tsv').open(encoding='utf-8-sig'),delimiter='\t'))
assets={}
for r in rows:
    if r.get('text','').strip():assets.setdefault(r['pak'],set()).add(r['asset'])
roots={
 'PARTS':(R/'03_text/ui_work/PARTS.PAK_unpacked',R/'05_build/ui_packages_fix4/PARTS.PAK_unpacked'),
 'SYSCG':(R/'03_text/ui_work/SYSCG.PAK_unpacked',R/'05_build/ui_packages_v1/SYSCG.PAK_unpacked'),
 'MANUAL':(R/'03_text/ui_work/MANUAL.PAK_unpacked',R/'05_build/ui_packages_v1/MANUAL.PAK_unpacked'),
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
rep=[]
for pak,names in assets.items():
 if pak not in roots:continue
 orig,fin=roots[pak]
 for n in sorted(names):
  a=orig/n;b=fin/n
  if not a.exists() or not b.exists():continue
  same=a.read_bytes()==b.read_bytes()
  texts=sorted(set(r['text'].strip() for r in rows if r['pak']==pak and r['asset']==n and r['text'].strip()))
  rep.append({'pak':pak,'asset':n,'same_orig_fix4':same,'texts':texts,'orig_size':a.stat().st_size,'fix4_size':b.stat().st_size})
for x in rep:
 if x['same_orig_fix4']:
  print(x['pak'],x['asset'],'UNCHANGED',repr(x['texts'][:30]))
(R/'05_build/english_asset_change_audit_fix5.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL',len(rep),'UNCHANGED',sum(x['same_orig_fix4'] for x in rep))
