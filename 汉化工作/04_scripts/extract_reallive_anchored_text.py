from pathlib import Path
import sys,csv,collections,re,json
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob
from extract_text_islands import cp932_unit,gbk_unit,lang_stats
STOP={0x00,0x0a,0x23,0x24,0x40}

def decode_after(data,start,lang,maxlen=2048):
    unit=cp932_unit if lang=='jp' else gbk_unit
    j=start; chars=[]; raw=bytearray()
    # Some Chinese-compiled CLANNAD rows preserve RealLive/CP932 name brackets
    # (0x8179/0x817A) around otherwise-GBK speaker text. Decode only those
    # structural punctuation pairs specially; do not treat the whole row as CP932.
    zh_cp932_struct={b'\x81\x79':'【', b'\x81\x7a':'】'}
    while j<len(data) and j-start<maxlen:
        if lang=='zh' and j+1<len(data):
            pair=bytes(data[j:j+2])
            if pair in zh_cp932_struct:
                raw += data[j:j+2]; chars.append(zh_cp932_struct[pair]); j+=2; continue
        n,ch=unit(data,j)
        if not n: break
        raw += data[j:j+n]; chars.append(ch); j+=n
    return bytes(raw),''.join(chars)

def plausible(text,lang):
    s=text.strip(' \t,()[]{}<>"\'\\')
    if not s:return False
    kana,han,latin=lang_stats(s)
    # anchored runs can legitimately be one CJK char or punctuation-heavy dialogue.
    if lang=='jp': return kana+han>=1
    return han>=1

def rows(path,lang):
    blob=Path(path).read_bytes(); dec,h=decompress_blob(blob); doff=h[1]; data=dec
    out=[]
    # Strong CLANNAD marker pattern: 0x40 + UInt16 ID immediately followed by a textout run.
    for p in range(doff+3,len(data)-3):
        # Strong control signature: 0A <kidoku:u16> 40 <text_id:u16>
        if not (data[p]==0x40 and data[p-3]==0x0a): continue
        tid=data[p+1]|(data[p+2]<<8)
        raw,text=decode_after(data,p+3,lang)
        if not raw or not plausible(text,lang): continue
        # reject marker bytes occurring inside an already-decoded text region by requiring the byte before 0x40
        # to look like control/parameter material rather than a legal trail byte sequence. Duplicates are retained for QA.
        kid=data[p-2]|(data[p-1]<<8)
        out.append({'kidoku_id':kid,'text_id':tid,'marker_offset':p,'text_offset':p+3,'rawhex':raw.hex(),'text':text})
    return out

def main(path,lang,out):
    rs=rows(path,lang);Path(out).parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['kidoku_id','text_id','marker_offset','text_offset','rawhex','text'],delimiter='\t');w.writeheader();w.writerows(rs)
    c=collections.Counter(r['text_id'] for r in rs)
    print(Path(path).name,lang,'rows',len(rs),'unique_ids',len(c),'dupe_ids',sum(v>1 for v in c.values()))
    for r in rs[:40]: print(r['text_id'],hex(r['text_offset']),r['text'].encode('unicode_escape').decode()[:160])
if __name__=='__main__':main(*sys.argv[1:4])


