from pathlib import Path
import zipfile,hashlib,re,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作');src=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix3';z=R/'05_build/CLANNAD_CHS_LayeredFS_v1.0.7_fix3.zip'
def shab(b):return hashlib.sha256(b).hexdigest().upper()
def shaf(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest().upper()
with zipfile.ZipFile(z,'r') as q:
 bad=q.testzip();names=q.namelist();dups=len(names)-len(set(names));mismatch=[]
 for n in names:
  sf=src/Path(n)
  if not sf.exists():mismatch.append([n,'missing_source']);continue
  zh=shab(q.read(n));fh=shaf(sf)
  if zh!=fh:mismatch.append([n,fh,zh])
 sha_text=q.read('SHA256SUMS.txt').decode('utf-8')
 sum_bad=[]
 for line in sha_text.splitlines():
  if not line.strip():continue
  m=re.match(r'^([0-9A-F]{64})  (.+)  \((\d+) bytes\)$',line)
  if not m:sum_bad.append([line,'parse']);continue
  h,n,s=m.groups()
  if n not in names:sum_bad.append([n,'not_in_zip']);continue
  data=q.read(n)
  if shab(data)!=h or len(data)!=int(s):sum_bad.append([n,'hash_or_size'])
 ips=[n for n in names if n.endswith('.ips')]
 full='CF38595316BAA425E792CE5CD122DFC600000000000000000000000000000000'
 ips_name_ok=(ips==[f'atmosphere/exefs_patches/CLANNAD_CHS_v1.0.7_fix3/{full}.ips'])
 romfs=[n for n in names if '/romfs/' in n and n.endswith('.PAK')]
 expected_paks=sorted(['FONT.PAK','MANUAL.PAK','OTHCG.PAK','PARTS.PAK','PARTS2.PAK','SCRIPT.PAK','SYSCG.PAK'])
 pak_names=sorted(Path(n).name for n in romfs)
rep={'zip_path':str(z),'zip_size':z.stat().st_size,'zip_sha256':shaf(z),'zip_test_bad':bad,'entries':len(names),'duplicate_entries':dups,'source_zip_mismatches':mismatch,'sha256sums_bad':sum_bad,'ips_entries':ips,'ips_name_ok':ips_name_ok,'romfs_paks':pak_names,'romfs_paks_ok':pak_names==expected_paks,'old_release_name_hits':[n for n in names if 'fix1' in n.lower() or 'fix2' in n.lower()]}
rep['total_bad']=(0 if bad is None else 1)+dups+len(mismatch)+len(sum_bad)+(0 if ips_name_ok else 1)+(0 if rep['romfs_paks_ok'] else 1)+len(rep['old_release_name_hits'])
(R/'05_build/FINAL_RELEASE_QA_fix3.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rep,ensure_ascii=False,indent=2))
raise SystemExit(1 if rep['total_bad'] else 0)
