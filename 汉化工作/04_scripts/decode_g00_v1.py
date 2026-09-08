from pathlib import Path
import struct,sys
from PIL import Image

def u16(b,o):return struct.unpack_from('<H',b,o)[0]
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
def i32(b,o):return struct.unpack_from('<i',b,o)[0]
def lzss(src,outlen):
 out=bytearray();i=0;bit=256;flag=0
 while i<len(src) and len(out)<outlen:
  if bit==256:flag=src[i];i+=1;bit=1
  if flag & bit:
   out.append(src[i]);i+=1
  else:
   if i+1>=len(src):break
   c=src[i]|(src[i+1]<<8);i+=2;off=c>>4;n=(c&0xf)+2;rp=len(out)-off
   if rp<0:raise ValueError(('bad backref',len(out),off))
   for _ in range(n):
    if len(out)>=outlen:break
    out.append(out[rp]);rp+=1
  bit<<=1
 if len(out)!=outlen:raise ValueError(('decomp len',len(out),outlen))
 return bytes(out)
def decode(path):
 b=Path(path).read_bytes();fmt=b[0];w=u16(b,1);h=u16(b,3)
 if fmt!=2:raise NotImplementedError(fmt)
 rc=u32(b,5);regions=[]
 for j in range(rc):
  o=9+j*24;regions.append(tuple(i32(b,o+k*4) for k in range(6)))
 ho=rc*24+9;cs=u32(b,ho);us=u32(b,ho+4);data=lzss(b[ho+8:ho+cs],us)
 il=u32(data,0)
 if il!=rc:raise ValueError(('index',il,rc))
 rgba=bytearray(w*h*4)
 for j,r in enumerate(regions):
  off=u32(data,4+j*8);ln=i32(data,8+j*8)
  if ln<=0:continue
  block=data[off:off+ln]
  if u16(block,0)!=1:raise ValueError('block type')
  parts=u16(block,2);io=0x74
  for _ in range(parts):
   px=u16(block,io)+r[0];py=u16(block,io+2)+r[1];tr=u16(block,io+4);pw=u16(block,io+6)*4;ph=u16(block,io+8);io+=0x5c
   for ly in range(py,py+ph):
    dst=(px+ly*w)*4;rgba[dst:dst+pw]=block[io:io+pw];io+=pw
 return Image.frombytes('RGBA',(w,h),bytes(rgba))
if __name__=='__main__':
 im=decode(sys.argv[1]);im.save(sys.argv[2]);print(im.size,im.getbbox())
