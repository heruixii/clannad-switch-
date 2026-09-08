from pathlib import Path
import sys,csv,unicodedata
from decompress_reallive import decompress_blob
STOP={0x00,0x0a,0x23,0x24,0x40}  # NUL LF # $ @

def cp932_unit(data,i):
    b=data[i]
    if b in STOP or b<0x20: return 0,''
    if 0x20<=b<=0x7e:
        return 1,chr(b)
    if 0xa1<=b<=0xdf:
        try:return 1,bytes([b]).decode('cp932')
        except:return 0,''
    if (0x81<=b<=0x9f) or (0xe0<=b<=0xfc):
        if i+1>=len(data): return 0,''
        t=data[i+1]
        if not ((0x40<=t<=0x7e) or (0x80<=t<=0xfc)): return 0,''
        try:return 2,data[i:i+2].decode('cp932')
        except:return 0,''
    return 0,''

def gbk_unit(data,i):
    b=data[i]
    if b in STOP or b<0x20: return 0,''
    if 0x20<=b<=0x7e: return 1,chr(b)
    if 0x81<=b<=0xfe and i+1<len(data):
        t=data[i+1]
        if 0x40<=t<=0xfe and t!=0x7f:
            try:return 2,data[i:i+2].decode('gbk')
            except:return 0,''
    return 0,''

def lang_stats(s):
    kana=sum('\u3040'<=c<='\u30ff' for c in s)
    han=sum(('\u3400'<=c<='\u9fff') or ('\uf900'<=c<='\ufaff') for c in s)
    latin=sum(c.isascii() and c.isalnum() for c in s)
    return kana,han,latin

def plausible(s,lang):
    s=s.strip(' ,()[]{}<>\"\'\\')
    if not s:return False
    kana,han,latin=lang_stats(s)
    visible=sum(not c.isspace() for c in s)
    if lang=='jp':
        # dialogue/resources: kana is strongest signal; kanji-only names/titles need >=2 Han
        if kana>=1: return visible>=2
        return han>=2 and han/visible>=0.45
    else:
        return han>=2 and han/visible>=0.45

def extract(blob,lang):
    dec,h=decompress_blob(blob); doff=h[1]; data=dec[doff:]; unit=cp932_unit if lang=='jp' else gbk_unit
    out=[]; i=0
    while i<len(data):
        n,ch=unit(data,i)
        if not n: i+=1; continue
        start=i; chars=[]; raw=bytearray(); j=i
        while j<len(data):
            n,ch=unit(data,j)
            if not n: break
            raw+=data[j:j+n]; chars.append(ch); j+=n
        text=''.join(chars)
        abs_off=doff+start
        keyed=(abs_off>=3 and dec[abs_off-3]==0x40)
        keyed_text=keyed and any(ord(c)>=0x80 and not (0xE000<=ord(c)<=0xF8FF) and not (0xFF61<=ord(c)<=0xFF9F) for c in text)
        if plausible(text,lang) or keyed_text: out.append((abs_off,bytes(raw),text))
        i=max(j,i+1)
    return out

def write(src,lang,out):
    rows=extract(Path(src).read_bytes(),lang); Path(out).parent.mkdir(parents=True,exist_ok=True)
    with open(out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['idx','offset','rawhex','text'])
        for k,(off,raw,text) in enumerate(rows):w.writerow([k,off,raw.hex(),text])
    print(Path(src).name,lang,'rows',len(rows))
    for k,x in enumerate(rows[:35]):print(k,hex(x[0]),x[2].encode('unicode_escape').decode())
if __name__=='__main__':write(sys.argv[1],sys.argv[2],sys.argv[3])



