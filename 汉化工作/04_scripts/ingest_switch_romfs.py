from pathlib import Path
import argparse,collections,csv,json,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
LUCA=ROOT/'tools/LucaSystemTools/LucaSystemTools/LucaSystemTools/bin/Release/net8.0/LucaSystemTools.exe'
LUCA_CWD=LUCA.parent

def inventory(root:Path):
    files=[p for p in root.rglob('*') if p.is_file()]
    ext=collections.Counter((p.suffix.lower() or '<noext>') for p in files)
    direct=[]; containers=[]; hints=[]
    for p in files:
        rel=p.relative_to(root)
        low=str(rel).lower()
        if p.suffix.lower()=='.scr': direct.append(p)
        if p.suffix.lower()=='.pak': containers.append(p)
        if ('script' in low or 'scenario' in low) and p not in direct: hints.append(p)
    return files,ext,direct,containers,hints

def export_scr(src:Path,outbase:Path):
    outbase.parent.mkdir(parents=True,exist_ok=True)
    cmd=[str(LUCA),'-t','scr','-m','export','-f',str(src),'-o',str(outbase),'-opcode','CL','-json','-ot','review']
    cp=subprocess.run(cmd,cwd=LUCA_CWD,text=True,encoding='utf-8',errors='replace',capture_output=True)
    return cp.returncode,cp.stdout,cp.stderr

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--execute',action='store_true',help='actually export .scr candidates; default is inventory only')
    a=ap.parse_args()
    report=ROOT/'03_text/switch_inventory';report.mkdir(parents=True,exist_ok=True)
    grand={}
    for label in ('base','update'):
        src=ROOT/'02_romfs'/label
        src.mkdir(parents=True,exist_ok=True)
        files,ext,direct,containers,hints=inventory(src)
        grand[label]={'files':len(files),'extensions':dict(ext),'scr':len(direct),'pak':len(containers),'hints':len(hints)}
        with open(report/f'{label}-files.tsv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,delimiter='\t');w.writerow(['relative_path','size','extension','candidate'])
            for p in files:
                rel=p.relative_to(src); low=str(rel).lower(); typ=''
                if p in direct:typ='scr'
                elif p in containers:typ='pak'
                elif p in hints:typ='script-path-hint'
                w.writerow([rel,p.stat().st_size,p.suffix.lower(),typ])
        if a.execute and direct:
            outroot=ROOT/'03_text/switch_export'/label
            log=[]
            for p in direct:
                rel=p.relative_to(src); out=outroot/rel
                rc,so,se=export_scr(p,out)
                log.append({'file':str(rel),'returncode':rc,'stdout':so[-2000:],'stderr':se[-2000:]})
            (report/f'{label}-export-log.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    (report/'summary.json').write_text(json.dumps(grand,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(grand,ensure_ascii=False,indent=2))
    print('luca_exists',LUCA.exists(),LUCA)
    if not a.execute:print('mode=inventory-only (use --execute only after real .scr files are found)')
if __name__=='__main__':main()
