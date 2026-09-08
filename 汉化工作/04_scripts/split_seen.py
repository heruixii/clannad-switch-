from pathlib import Path
import struct, sys, hashlib

def split(src: Path, out: Path):
    data=src.read_bytes()
    out.mkdir(parents=True, exist_ok=True)
    rows=[]
    for i in range(10000):
        off,ln=struct.unpack_from('<II',data,i*8)
        if off==0 and ln==0: continue
        if off < 80000 or off+ln > len(data):
            raise ValueError(f'bad index {i}: {off:#x}+{ln:#x} / {len(data):#x}')
        blob=data[off:off+ln]
        p=out/f'SEEN{i:04d}.TXT'
        p.write_bytes(blob)
        rows.append((i,off,ln,hashlib.sha256(blob).hexdigest()))
    return rows

if __name__=='__main__':
    src=Path(sys.argv[1]); out=Path(sys.argv[2])
    rows=split(src,out)
    print('source',src)
    print('files',len(rows),'total_payload',sum(r[2] for r in rows))
    print('first',rows[:10]); print('last',rows[-10:])
