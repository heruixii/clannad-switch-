from pathlib import Path
import sys,csv,re,collections,time
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
from extract_text_islands import extract

ROOT=Path(__file__).resolve().parents[1]
JP=ROOT/'03_text/pc_jp/raw'
ZH=ROOT/'03_text/pc_zh/raw'
OUT=ROOT/'03_text/matched/pc_kidoku_v1'
OUT.mkdir(parents=True,exist_ok=True)

def canon_zh(s):
    s=s.strip()
    while len(s)>=2 and s[0]=='"' and s[-1]=='"':
        s=s[1:-1].strip()
    s=re.sub(r'【"([^"\r\n]+)"】',r'【\1】',s)
    s=s.replace('】"「','】「').replace('】"（','】（').replace('】"(','】(')
    s=re.sub(r'"([＊％][A-Za-zＡ-Ｚ])"',r'\1',s)
    while s.startswith('"'):s=s[1:]
    while s.endswith('"'):s=s[:-1]
    return s

def keyed_rows(path,lang):
    raw=path.read_bytes(); dec,h=decompress_blob(raw); rows=extract(raw,lang)
    out=[]
    for idx,(off,b,text) in enumerate(rows):
        kidoku=None
        if off>=3 and dec[off-3]==0x40:
            kidoku=int.from_bytes(dec[off-2:off],'little')
        out.append({'idx':idx,'off':off,'raw':b,'text':text,'kidoku':kidoku})
    return out

def groups(rows):
    d=collections.defaultdict(list)
    for r in rows:
        if r['kidoku'] is not None:d[r['kidoku']].append(r)
    return d

def main():
    allrows=[]; sums=[]; t0=time.time()
    files=sorted(JP.glob('SEEN*.TXT'))
    for n,jpfile in enumerate(files,1):
        scene=jpfile.stem; zfile=ZH/jpfile.name
        J=keyed_rows(jpfile,'jp'); Z=keyed_rows(zfile,'zh')
        JG=groups(J); ZG=groups(Z)
        consumed_z=set(); rows=[]; counts=collections.Counter()
        for j in J:
            kid=j['kidoku']; z=None
            if kid is None:
                status='review-unkeyed-jp'
            elif len(JG[kid])!=1:
                status='review-jp-duplicate-key'
            elif kid not in ZG:
                status='missing-zh-key'
            elif len(ZG[kid])!=1:
                status='review-zh-duplicate-key'
            else:
                status='kidoku-exact'; z=ZG[kid][0]; consumed_z.add(z['idx'])
            counts[status]+=1
            row=[scene,status,'' if kid is None else kid,j['idx'],'' if z is None else z['idx'],j['off'],'' if z is None else z['off'],j['text'],'' if z is None else z['text'],'' if z is None else canon_zh(z['text'])]
            rows.append(row);allrows.append(row)
        # retain Chinese-only/unkeyed material for audit, but never auto-attach it to a JP line.
        for z in Z:
            if z['idx'] in consumed_z:continue
            kid=z['kidoku']
            if kid is None: status='review-unkeyed-zh'
            elif kid not in JG: status='zh-only-key'
            elif len(JG[kid])!=1: status='review-jp-duplicate-key'
            elif len(ZG[kid])!=1: status='review-zh-duplicate-key'
            else:
                # same key should have been consumed above; reaching here is an invariant failure.
                status='internal-unconsumed-match'
            counts[status]+=1
            row=[scene,status,'' if kid is None else kid,'',z['idx'],'',z['off'],'',z['text'],canon_zh(z['text'])]
            rows.append(row);allrows.append(row)
        header=['scene','status','kidoku_id','jp_idx','zh_idx','jp_offset','zh_offset','jp_text','zh_raw','zh_canonical']
        with open(OUT/f'{scene}.tsv','w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f,delimiter='\t');w.writerow(header);w.writerows(rows)
        sums.append([scene,len(J),len(Z),counts['kidoku-exact'],counts['missing-zh-key'],counts['zh-only-key'],counts['review-unkeyed-jp'],counts['review-unkeyed-zh'],counts['review-jp-duplicate-key']+counts['review-zh-duplicate-key'],counts['internal-unconsumed-match']])
        if n%30==0 or n==len(files):print('progress',n,'/',len(files),'elapsed',round(time.time()-t0,1),flush=True)
    header=['scene','status','kidoku_id','jp_idx','zh_idx','jp_offset','zh_offset','jp_text','zh_raw','zh_canonical']
    with open(ROOT/'03_text/matched/pc-kidoku-map-v1.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(header);w.writerows(allrows)
    with open(ROOT/'03_text/matched/pc-kidoku-summary-v1.tsv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['scene','jp_rows','zh_rows','exact','missing_zh','zh_only','unkeyed_jp','unkeyed_zh','duplicate_key_rows','internal_errors']);w.writerows(sums)
    total=[sum(r[i] for r in sums) for i in range(1,10)]
    print('scenes',len(sums))
    print('jp_rows zh_rows exact missing_zh zh_only unkeyed_jp unkeyed_zh duplicate_key_rows internal_errors')
    print(*total)
    print('exact_vs_jp_pct',round(total[2]/max(1,total[0])*100,3))
if __name__=='__main__':main()
