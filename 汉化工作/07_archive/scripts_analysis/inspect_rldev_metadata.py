from pathlib import Path
import sys,struct,collections
sys.path.insert(0,str(Path(__file__).parent))
from decompress_reallive import decompress_blob

def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def meta(path):
    dec,h=decompress_blob(Path(path).read_bytes());doff=h[1]
    dp_end=u32(dec,0x14)+u32(dec,0x1c)
    if dp_end==doff:return {'transform':0,'name':'','dp_end':dp_end,'doff':doff,'meta':False}
    if dp_end+8>len(dec):return {'transform':-1,'name':'bad','dp_end':dp_end,'doff':doff,'meta':True}
    ml=u32(dec,dp_end); il=u32(dec,dp_end+4)+1; idx2=dp_end+8+il
    name=dec[dp_end+8:dp_end+8+il].split(b'\0',1)[0].decode('ascii','replace')
    tr=dec[idx2+8] if idx2+8<len(dec) else -1
    return {'transform':tr,'name':name,'dp_end':dp_end,'doff':doff,'meta_len':ml,'meta':True}
if __name__=='__main__':
    for p in map(Path,sys.argv[1:]): print(p.stem,meta(p))
