from pathlib import Path
import json,csv,collections,struct
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'03_text/switch_export/script_json'
OUT=ROOT/'03_text/switch_extracted/switch_messages.tsv'
SUM=ROOT/'03_text/switch_inventory/message-extract-summary.json'

def raw_params(code):
    out=bytearray()
    for pd in code.get('paramDatas',[]):
        v=str(pd.get('value',''))
        if v.startswith('0x'):
            h=v[2:].replace(' ','')
            if len(h)%2: h='0'+h
            out.extend(bytes.fromhex(h))
    return bytes(out)

def read_lp_utf16(raw,pos):
    if pos+2>len(raw): raise ValueError('missing length')
    n=struct.unpack_from('<H',raw,pos)[0]; pos+=2
    need=2*n
    if pos+need>len(raw): raise ValueError(f'length {n} beyond raw')
    b=raw[pos:pos+need]; pos+=need
    text=b.decode('utf-16le',errors='replace')
    if pos+2>len(raw): raise ValueError('missing terminator')
    term=raw[pos:pos+2]
    if term!=b'\x00\x00': raise ValueError(f'bad terminator {term.hex()}')
    pos+=2
    return text,pos,n

def parse_message(raw):
    jp,pos,jplen=read_lp_utf16(raw,0)
    en,pos,enlen=read_lp_utf16(raw,pos)
    return jp,en,jplen,enlen,raw[pos:]

def clean_cell(s):
    return s.replace('\r','\\r').replace('\n','\\n').replace('\t','\\t')

def main():
    OUT.parent.mkdir(parents=True,exist_ok=True); SUM.parent.mkdir(parents=True,exist_ok=True)
    files=sorted(SRC.glob('SEEN*.json'))
    rows=[]; opcounts=collections.Counter(); errors=[]; trail=collections.Counter()
    for fp in files:
        try:
            data=json.loads(fp.read_text(encoding='utf-8-sig'))
        except Exception as e:
            errors.append({'scene':fp.stem,'code_index':'','error':'json:'+repr(e)}); continue
        for ci,code in enumerate(data.get('codes',[])):
            op=code.get('opcode',''); opcounts[op]+=1
            if op!='MESSAGE': continue
            raw=raw_params(code)
            try:
                jp,en,jplen,enlen,trailing=parse_message(raw)
                trail[trailing.hex().upper()]+=1
                info=code.get('info') or {}; idata=info.get('data') or []
                rows.append({
                    'scene':fp.stem,'code_index':ci,
                    'info_data':','.join(str(x) for x in idata),
                    'jp_len':jplen,'en_len':enlen,
                    'jp_text':clean_cell(jp),'en_text':clean_cell(en),
                    'trailing_hex':trailing.hex().upper(),
                })
            except Exception as e:
                errors.append({'scene':fp.stem,'code_index':ci,'error':repr(e),'raw_prefix':raw[:96].hex().upper()})
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['scene','code_index','info_data','jp_len','en_len','jp_text','en_text','trailing_hex']
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t'); w.writeheader(); w.writerows(rows)
    summary={
        'scene_json_files':len(files),'message_rows':len(rows),'parse_errors':len(errors),
        'opcode_counts':dict(opcounts),'trailing_patterns':dict(trail),'errors':errors[:50],
        'output':str(OUT)
    }
    SUM.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
