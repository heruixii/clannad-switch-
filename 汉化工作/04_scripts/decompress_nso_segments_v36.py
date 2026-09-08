from pathlib import Path
import struct,hashlib,json

def lz4_block(src,out_size):
    ip=0; out=bytearray(); n=len(src)
    while ip<n and len(out)<out_size:
        token=src[ip]; ip+=1
        lit=token>>4
        if lit==15:
            while True:
                if ip>=n: raise ValueError('lit eof')
                x=src[ip];ip+=1;lit+=x
                if x!=255:break
        if ip+lit>n: raise ValueError('literal overrun')
        out.extend(src[ip:ip+lit]);ip+=lit
        if ip>=n:break
        if ip+2>n:raise ValueError('offset eof')
        off=src[ip]|(src[ip+1]<<8);ip+=2
        if off==0 or off>len(out):raise ValueError(('bad off',off,len(out),ip))
        ml=token&15
        if ml==15:
            while True:
                if ip>=n:raise ValueError('match eof')
                x=src[ip];ip+=1;ml+=x
                if x!=255:break
        ml+=4
        start=len(out)-off
        for _ in range(ml): out.append(out[start]);start+=1
    if len(out)!=out_size:raise ValueError(('size',len(out),out_size,ip,n))
    return bytes(out)
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\exefs_fix2\update_exefs\main');O=P.parent/'main_decompressed';O.mkdir(exist_ok=True)
b=P.read_bytes();flags=struct.unpack_from('<I',b,0x0c)[0];segs=[]
for i,(name,foff_off,memoff_off,size_off,comp_off,hash_off) in enumerate([
 ('text',0x10,0x14,0x18,0x60,0xA0),('rodata',0x20,0x24,0x28,0x64,0xC0),('data',0x30,0x34,0x38,0x68,0xE0)]):
 foff=struct.unpack_from('<I',b,foff_off)[0];memoff=struct.unpack_from('<I',b,memoff_off)[0];size=struct.unpack_from('<I',b,size_off)[0];comp=struct.unpack_from('<I',b,comp_off)[0];raw=b[foff:foff+comp];compressed=bool(flags&(1<<i));out=lz4_block(raw,size) if compressed else raw[:size]
 sha=hashlib.sha256(out).digest(); hdrhash=b[hash_off:hash_off+32]; q=O/(name+'.bin');q.write_bytes(out)
 segs.append({'name':name,'file_offset':foff,'memory_offset':memoff,'size':size,'compressed_size':comp,'compressed':compressed,'sha256':sha.hex().upper(),'header_hash_matches':sha==hdrhash})
print(json.dumps({'flags':hex(flags),'segments':segs},indent=2));(O/'segments.json').write_text(json.dumps(segs,indent=2),encoding='utf-8')
