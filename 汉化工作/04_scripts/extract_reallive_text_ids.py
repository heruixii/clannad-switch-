from pathlib import Path
import sys,csv,collections,re,json
sys.path.insert(0,str(Path(__file__).parent))
from extract_text_islands import extract
from decompress_reallive import decompress_blob

def text_id(dec,off,doff,window=24):
    pre=dec[max(doff,off-window):off]
    # RealLive text marker observed in CLANNAD FV: 0x40 + little-endian UInt16 text index.
    # Use nearest occurrence to the text start.
    hits=[]
    for i in range(len(pre)-2):
        if pre[i]==0x40:
            hits.append((i,pre[i+1]|(pre[i+2]<<8)))
    return hits[-1][1] if hits else None

def rows(path,lang):
    blob=Path(path).read_bytes(); dec,h=decompress_blob(blob); doff=h[1]
    out=[]
    for idx,(off,raw,text) in enumerate(extract(blob,lang)):
        out.append({'run_idx':idx,'offset':off,'text_id':text_id(dec,off,doff),'text':text})
    return out

def main(path,lang,out):
    rs=rows(path,lang); Path(out).parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['run_idx','offset','text_id','text'],delimiter='\t');w.writeheader();w.writerows(rs)
    ids=[r['text_id'] for r in rs if r['text_id'] is not None]
    c=collections.Counter(ids)
    print(Path(path).name,lang,'runs',len(rs),'with_id',len(ids),'unique',len(c),'dupe_ids',sum(v>1 for v in c.values()),'none',sum(r['text_id'] is None for r in rs))
if __name__=='__main__':main(*sys.argv[1:4])
