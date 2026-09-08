from pathlib import Path
import sys, struct, csv, unicodedata
from decompress_reallive import decompress_blob

def is_cjk_text(s):
    return any(('\u3040'<=c<='\u30ff') or ('\u3400'<=c<='\u9fff') or ('\uf900'<=c<='\ufaff') for c in s)

def ok_char(c):
    o=ord(c)
    if c in '\r\n\t\x00': return False
    if c.isprintable() and not (0x80 <= o <= 0x9f): return True
    return False

def decode_pair(data,i,enc):
    # try 2-byte character first
    if i+1 < len(data):
        for n in (2,1):
            try:
                s=data[i:i+n].decode(enc,'strict')
            except Exception:
                continue
            if s and all(ok_char(c) for c in s):
                # one-byte ASCII only accepted for visible punctuation/alnum; high half for jp kana
                if n==1 and data[i] < 0x20: continue
                return n,s
    else:
        try:
            s=data[i:i+1].decode(enc,'strict')
            if s and all(ok_char(c) for c in s) and data[i]>=0x20: return 1,s
        except: pass
    return 0,''

def extract(blob,enc):
    _,h=decompress_blob(blob)
    _,doff,usize,_=h
    data=decompress_blob(blob)[0][doff:]
    runs=[]; i=0
    while i<len(data):
        start=i; chars=[]; raw=bytearray(); j=i
        while j<len(data):
            n,s=decode_pair(data,j,enc)
            if not n: break
            # raw byte values used by bytecode punctuation often decode to ASCII. Keep only if near real text.
            raw += data[j:j+n]; chars.append(s); j+=n
        if j>i:
            text=''.join(chars).strip()
            # remove obviously opcode-like ASCII prefixes/suffixes, preserving text core
            if is_cjk_text(text):
                # require at least 1 CJK and reject very control-ish garbage
                runs.append((doff+i,bytes(raw),text))
            i=j
        else:
            i+=1
    # Merge runs separated by tiny opcode punctuation only when both are text and offsets close
    return runs

def main(src,enc,out):
    rows=extract(Path(src).read_bytes(),enc)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['idx','offset','rawhex','text'])
        for k,(off,raw,text) in enumerate(rows): w.writerow([k,off,raw.hex(),text])
    print(Path(src).name,'runs',len(rows));
    for x in rows[:30]: print(hex(x[0]),repr(x[2]))
if __name__=='__main__': main(sys.argv[1],sys.argv[2],sys.argv[3])
