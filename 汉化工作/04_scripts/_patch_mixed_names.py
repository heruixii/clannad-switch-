from pathlib import Path
root=Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
p=root/'04_scripts/extract_reallive_anchored_text.py'
s=p.read_text(encoding='utf-8-sig')
old="""def decode_after(data,start,lang,maxlen=2048):
    unit=cp932_unit if lang=='jp' else gbk_unit
    j=start; chars=[]; raw=bytearray()
    while j<len(data) and j-start<maxlen:
        n,ch=unit(data,j)
        if not n: break
        raw += data[j:j+n]; chars.append(ch); j+=n
    return bytes(raw),''.join(chars)
"""
new="""def decode_after(data,start,lang,maxlen=2048):
    unit=cp932_unit if lang=='jp' else gbk_unit
    j=start; chars=[]; raw=bytearray()
    # Some Chinese-compiled CLANNAD rows preserve RealLive/CP932 name brackets
    # (0x8179/0x817A) around otherwise-GBK speaker text. Decode only those
    # structural punctuation pairs specially; do not treat the whole row as CP932.
    zh_cp932_struct={b'\\x81\\x79':'【', b'\\x81\\x7a':'】'}
    while j<len(data) and j-start<maxlen:
        if lang=='zh' and j+1<len(data):
            pair=bytes(data[j:j+2])
            if pair in zh_cp932_struct:
                raw += data[j:j+2]; chars.append(zh_cp932_struct[pair]); j+=2; continue
        n,ch=unit(data,j)
        if not n: break
        raw += data[j:j+n]; chars.append(ch); j+=n
    return bytes(raw),''.join(chars)
"""
if old not in s: raise SystemExit('decode_after block not found')
p.write_text(s.replace(old,new),encoding='utf-8')

b=root/'04_scripts/build_pc_control_corpus.py'
t=b.read_text(encoding='utf-8-sig')
old2="""            elif jk!=zk:
                status='review-type-mismatch'; reason=f'{jk}!={zk}'
"""
new2="""            elif jk!=zk:
                # RealLive occasionally emits a standalone speaker-name event.
                # If JP is exactly 【name】 and ZH is the same name with compiler quotes only,
                # treat it as a structural name event rather than narration/dialogue conflict.
                jm=re.fullmatch(r'【([^】]+)】', trim(jt)); zn=trim(zt).strip('\\\"')
                if jm and zn==jm.group(1):
                    status='name-event'; reason='standalone-speaker-name'
                else:
                    status='review-type-mismatch'; reason=f'{jk}!={zk}'
"""
if old2 not in t: raise SystemExit('type mismatch block not found')
b.write_text(t.replace(old2,new2),encoding='utf-8')
print('patched',p,b)
