from pathlib import Path
import sys,collections,hashlib,json
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
from extract_reallive_anchored_text import rows

def norm_block(b):
    b=bytearray(b)
    # normalize common RealLive marker operands: 0A xx xx and 40 xx xx
    i=0
    while i+2<len(b):
        if b[i] in (0x0a,0x40):
            b[i+1]=0; b[i+2]=0; i+=3
        else:i+=1
    return bytes(b)

def events(path,lang,cap=192):
    blob=Path(path).read_bytes();dec,h=decompress_blob(blob);rs=rows(path,lang)
    out=[];prev_end=h[1]
    for r in rs:
        start=r['marker_offset']-3 # include 0A kidoku 40 id
        block=dec[max(prev_end,start-cap):start+6]
        nb=norm_block(block)
        out.append({**r,'fp':hashlib.sha1(nb).hexdigest(),'block':nb,'block_len':len(nb)})
        prev_end=r['text_offset']+len(bytes.fromhex(r['rawhex']))
    return out

if __name__=='__main__':
    root=Path(sys.argv[1]);sc=sys.argv[2]
    J=events(root/f'03_text/pc_jp/raw/SEEN{sc}.TXT','jp');Z=events(root/f'03_text/pc_zh/raw/SEEN{sc}.TXT','zh')
    zm=collections.defaultdict(list)
    for i,r in enumerate(Z):zm[r['fp']].append((i,r))
    exact=[]
    for i,r in enumerate(J):
        c=zm.get(r['fp'],[])
        if len(c)==1:exact.append((i,c[0][0],r,c[0][1]))
    print('scene',sc,'J',len(J),'Z',len(Z),'unique_exact',len(exact))
    for a,b,j,z in exact[:80]:
        print(a,b,'tid',j['text_id'],z['text_id'],'kid',j['kidoku_id'],z['kidoku_id'],'len',j['block_len'],j['text'].encode('unicode_escape').decode()[:80],'=>',z['text'].encode('unicode_escape').decode()[:80])
