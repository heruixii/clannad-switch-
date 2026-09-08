from pathlib import Path
import shutil,subprocess,csv,json,re,sys,collections
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'02_romfs/base'; UPDATE=ROOT/'02_romfs/update'; MERGED=ROOT/'02_romfs/merged-v1.0.7'
WORK=ROOT/'03_text/switch_work'; EXPORT=ROOT/'03_text/switch_export'; INV=ROOT/'03_text/switch_inventory'
LUCA=ROOT/'tools/LucaSystemTools/LucaSystemTools/LucaSystemTools/bin/Release/net8.0/LucaSystemTools.exe'
LUCA_CWD=LUCA.parent

def copytree_overlay(src,dst):
    if not src.exists(): return 0
    n=0
    for p in src.rglob('*'):
        if not p.is_file(): continue
        q=dst/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);n+=1
    return n

def run(cmd):
    return subprocess.run(cmd,cwd=LUCA_CWD,text=True,encoding='utf-8',errors='replace',capture_output=True)

def unpack_paks(root):
    out=[]
    for p in root.rglob('*.pak'):
        rel=p.relative_to(root); cp=WORK/'paks'/rel;cp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,cp)
        r=run([str(LUCA),'-t','pak','-m','export','-f',str(cp),'-o',str(cp.parent)])
        out.append({'source':str(rel),'copy':str(cp),'returncode':r.returncode,'stdout':r.stdout[-3000:],'stderr':r.stderr[-3000:]})
    return out

def export_scripts(roots):
    logs=[]; seen=set()
    for srcroot,label in roots:
        if not srcroot.exists():continue
        for p in srcroot.rglob('*.scr'):
            rp=str(p.resolve()).lower()
            if rp in seen:continue
            seen.add(rp)
            try: rel=p.relative_to(srcroot)
            except ValueError: rel=Path(p.name)
            outbase=EXPORT/label/rel; outbase.parent.mkdir(parents=True,exist_ok=True)
            r=run([str(LUCA),'-t','scr','-m','export','-f',str(p),'-o',str(outbase),'-opcode','CL','-json','-ot','translate'])
            logs.append({'root':label,'source':str(p),'relative':str(rel),'returncode':r.returncode,'stdout':r.stdout[-3000:],'stderr':r.stderr[-3000:]})
    return logs

def collect_strings():
    rows=[]
    pat=re.compile(r'^[○●](\d{5})\|(\d{8})[○●]\s?(.*)$')
    for p in EXPORT.rglob('*.string.txt'):
        rel=p.relative_to(EXPORT); pair={}
        for line in p.read_text(encoding='utf-8-sig',errors='replace').splitlines():
            m=pat.match(line)
            if not m:continue
            code,index,text=m.groups();key=(code,index)
            d=pair.setdefault(key,{'source':'','target':''})
            if line.startswith('○'):d['source']=text
            elif line.startswith('●'):d['target']=text
        for (code,index),d in pair.items():
            rows.append({'file':str(rel),'code_index':code,'param_index':index,'source_text':d['source'],'target_text':d['target']})
    out=ROOT/'03_text/switch_extracted/all_strings.tsv';out.parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['file','code_index','param_index','source_text','target_text'],delimiter='\t');w.writeheader();w.writerows(rows)
    return out,rows

def main():
    for d in (BASE,UPDATE,WORK,EXPORT,INV):d.mkdir(parents=True,exist_ok=True)
    bf=sum(1 for p in BASE.rglob('*') if p.is_file()); uf=sum(1 for p in UPDATE.rglob('*') if p.is_file())
    if bf==0 and uf==0:
        print(json.dumps({'status':'blocked-no-romfs','base_files':0,'update_files':0,'expected_input':[str(BASE),str(UPDATE)]},ensure_ascii=False,indent=2));return 2
    if MERGED.exists():shutil.rmtree(MERGED)
    MERGED.mkdir(parents=True)
    bcop=copytree_overlay(BASE,MERGED); ucop=copytree_overlay(UPDATE,MERGED)
    ext=collections.Counter((p.suffix.lower() or '<noext>') for p in MERGED.rglob('*') if p.is_file())
    paks=unpack_paks(MERGED)
    unpack_roots=[]
    for x in (WORK/'paks').rglob('*_unpacked'):
        if x.is_dir():unpack_roots.append((x,'pak_'+x.name))
    logs=export_scripts([(MERGED,'merged')]+unpack_roots)
    out,rows=collect_strings()
    summary={'status':'ok','base_files':bf,'update_files':uf,'copied_base':bcop,'copied_update':ucop,'merged_files':sum(ext.values()),'extensions':dict(ext),'paks':len(paks),'script_exports':len(logs),'script_export_ok':sum(x['returncode']==0 for x in logs),'string_rows':len(rows),'strings_tsv':str(out)}
    INV.mkdir(parents=True,exist_ok=True);(INV/'pipeline-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (INV/'pak-log.json').write_text(json.dumps(paks,ensure_ascii=False,indent=2),encoding='utf-8');(INV/'script-export-log.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
