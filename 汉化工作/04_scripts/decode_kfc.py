from pathlib import Path
import sys

def decode_kfc(raw:bytes)->str:
    out=bytearray(); i=0
    special={0x8175:(0xa1,0xb8),0x8177:(0xa1,0xba),0x8169:(0xa3,0xa8),0x8153:(0xbb,0xa2),0x8252:(0xdd,0xa2),0x8253:(0xb5,0xa2)}
    while i<len(raw):
        a1=raw[i]
        if a1<=0x7f:
            out.append(a1); i+=1; continue
        if not (((0x81<=a1<=0x9f) or (0xe0<=a1<=0xef) or (0xf0<=a1<=0xfc)) and i+1<len(raw)):
            raise ValueError(f'malformed at {i}: {a1:02x}')
        a2=raw[i+1]; pair=(a1<<8)|a2
        if pair in special: g1,g2=special[pair]
        else:
            c2=((a1-0x40 if a1>0xdf else a1)-0x81)*2
            c1=(a2-1 if a2>=0x80 else a2)-0x40
            x=c1//2; y=c2+(c1%2)
            g1=x+0xa1;g2=y+0xa1
        out.extend((g1,g2)); i+=2
    return out.decode('gbk')
if __name__=='__main__': print(decode_kfc(bytes.fromhex(sys.argv[1])))
