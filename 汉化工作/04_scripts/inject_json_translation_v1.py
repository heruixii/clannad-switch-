from pathlib import Path
import csv,json,struct,shutil,sys
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
SRC=ROOT/'03_text/switch_export/script_json'; DST=ROOT/'03_text/switch_inject/json_zh'
MSG=ROOT/'03_text/translated/message_targets_complete_v12.tsv'; SEL=ROOT/'03_text/translated/select_targets_complete_v2.tsv'
def rd(p):
 with p.open('r',encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
mm={(r['scene'],int(r['code_index'])):r for r in rd(MSG)}; sm={(r['scene'],int(r['code_index'])):r for r in rd(SEL)}
def raw_params(c):
 out=bytearray()
 for p in c.get('paramDatas',[]):
  v=str(p.get('value',''))
  if v.startswith('0x'):out.extend(bytes.fromhex(v[2:].replace(' ','')))
 return bytes(out)
def lp_read(raw,pos):
 n=struct.unpack_from('<H',raw,pos)[0];pos+=2;b=raw[pos:pos+2*n];pos+=2*n
 assert raw[pos:pos+2]==b'\0\0';pos+=2
 return b.decode('utf-16le'),pos
def lp_make(s):
 b=s.encode('utf-16le');return struct.pack('<H',len(b)//2)+b+b'\0\0'
def unesc(s):return s.replace('\\r','\r').replace('\\n','\n').replace('\\t','\t')
def to_params(raw):
 a=[];n=len(raw)//2*2
 for i in range(0,n,2):a.append({'type':'Byte2','value':'0x'+raw[i:i+2].hex().upper()})
 if len(raw)%2:a.append({'type':'Byte','value':'0x'+raw[-1:].hex().upper()})
 return a
def inject_scene(sc):
 fp=SRC/f'{sc}.json';d=json.loads(fp.read_text(encoding='utf-8-sig'));mc=ss=0
 for ci,c in enumerate(d.get('codes',[])):
  k=(sc,ci)
  if k in mm:
   assert c.get('opcode')=='MESSAGE',k
   raw=raw_params(c);jp,p=lp_read(raw,0);en,p=lp_read(raw,p);trail=raw[p:]
   zh=unesc(mm[k]['zh_text'])
   nr=lp_make(jp)+lp_make(zh)+trail;c['paramDatas']=to_params(nr);mc+=1
  if k in sm:
   assert c.get('opcode')=='SELECT',k
   raw=raw_params(c);head=raw[:8];jp,p=lp_read(raw,8);en,p=lp_read(raw,p);tail=raw[p:]
   zh=unesc(sm[k]['zh_text']);nr=head+lp_make(jp)+lp_make(zh)+tail;c['paramDatas']=to_params(nr);ss+=1
 DST.mkdir(parents=True,exist_ok=True);out=DST/f'{sc}.json';out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8-sig')
 print(sc,'message',mc,'select',ss,'out',out);return out
if __name__=='__main__':
    arg=sys.argv[1] if len(sys.argv)>1 else 'SEEN0414'
    if arg.upper()=='ALL':
        totals={'message':0,'select':0}; seen_m=set(); seen_s=set(); files=sorted(SRC.glob('SEEN*.json'))
        DST.mkdir(parents=True,exist_ok=True)
        for fp in files:
            sc=fp.stem; d=json.loads(fp.read_text(encoding='utf-8-sig')); mc=ss=0
            for ci,c in enumerate(d.get('codes',[])):
                k=(sc,ci)
                if k in mm:
                    assert c.get('opcode')=='MESSAGE',k
                    raw=raw_params(c);jp,p=lp_read(raw,0);en,p=lp_read(raw,p);trail=raw[p:]
                    nr=lp_make(jp)+lp_make(unesc(mm[k]['zh_text']))+trail;c['paramDatas']=to_params(nr);mc+=1;seen_m.add(k)
                if k in sm:
                    assert c.get('opcode')=='SELECT',k
                    raw=raw_params(c);head=raw[:8];jp,p=lp_read(raw,8);en,p=lp_read(raw,p);tail=raw[p:]
                    nr=head+lp_make(jp)+lp_make(unesc(sm[k]['zh_text']))+tail;c['paramDatas']=to_params(nr);ss+=1;seen_s.add(k)
            (DST/f'{sc}.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8-sig')
            totals['message']+=mc; totals['select']+=ss
        print({'json_files':len(files),**totals,'message_targets':len(mm),'select_targets':len(sm),'missing_message_targets':len(set(mm)-seen_m),'missing_select_targets':len(set(sm)-seen_s)})
        assert seen_m==set(mm) and seen_s==set(sm)
    else:
        inject_scene(arg)

