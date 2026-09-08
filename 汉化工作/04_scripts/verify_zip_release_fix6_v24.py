from pathlib import Path
import zipfile,hashlib,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');src=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix6';z=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix6.zip'
def shab(b):return hashlib.sha256(b).hexdigest().upper()
def shaf(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest().upper()
with zipfile.ZipFile(z,'r') as q:
 names=q.namelist();bad=q.testzip();dups=len(names)-len(set(names));mismatch=[]
 for n in names:
  f=src/Path(n)
  if not f.exists():mismatch.append([n,'missing_source']);continue
  if shab(q.read(n))!=shaf(f):mismatch.append([n,'hash'])
 sums=q.read('SHA256SUMS.txt').decode('utf-8');sbad=[]
 for line in sums.splitlines():
  if not line.strip():continue
  m=re.match(r'^([0-9A-F]{64})  (.+)  \((\d+) bytes\)$',line)
  if not m:sbad.append([line,'parse']);continue
  h,n,s=m.groups()
  if n not in names:sbad.append([n,'missing']);continue
  d=q.read(n)
  if shab(d)!=h or len(d)!=int(s):sbad.append([n,'hash_size'])
 full='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000';ips=[n for n in names if n.endswith('.ips')];expected_ips=f'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix6/{full}.ips'
 paks=sorted(Path(n).name for n in names if '/romfs/' in n and n.endswith('.PAK'));exp=sorted(['FONT.PAK','MANUAL.PAK','OTHCG.PAK','PARTS.PAK','PARTS2.PAK','SCRIPT.PAK','SYSCG.PAK'])
 old=[n for n in names if any(x in n.lower() for x in ['fix1','fix2','fix3','fix4','fix5'])]
 rep={'zip_path':str(z),'zip_size':z.stat().st_size,'zip_sha256':shaf(z),'zip_test_bad':bad,'entries':len(names),'duplicate_entries':dups,'source_zip_mismatches':mismatch,'sha256sums_bad':sbad,'ips_entries':ips,'ips_name_ok':ips==[expected_ips],'romfs_paks':paks,'romfs_paks_ok':paks==exp,'old_release_path_hits':old}
 rep['total_bad']=(0 if bad is None else 1)+dups+len(mismatch)+len(sbad)+(0 if rep['ips_name_ok'] else 1)+(0 if rep['romfs_paks_ok'] else 1)+len(old)
 (R/'05_build/FINAL_RELEASE_QA_fix6.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rep,ensure_ascii=False,indent=2));raise SystemExit(1 if rep['total_bad'] else 0)
