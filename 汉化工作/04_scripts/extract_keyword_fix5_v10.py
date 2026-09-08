from pathlib import Path
import struct,json,statistics
src=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_work\script_probe\SCRIPT.PAK_unpacked\_KEYWORD')
b=src.read_bytes();off=0;rows=[]
while off<len(b):
    start=off
    if off+10>len(b): raise ValueError(('trailing',off,len(b)))
    rec_size,total,z,magic,idx=struct.unpack_from('<5H',b,off);off+=10
    def gs():
        nonlocal_dummy=None
        global off
    ss=[]
    for k in range(4):
        n=struct.unpack_from('<H',b,off)[0];off+=2
        raw=b[off:off+n*2];off+=n*2
        term=struct.unpack_from('<H',b,off)[0];off+=2
        if term!=0: raise ValueError(('term',len(rows),k,hex(off),term))
        ss.append(raw.decode('utf-16le'))
    if off-start!=rec_size: raise ValueError(('size',len(rows),start,rec_size,off-start))
    rows.append({'index':idx,'record_size':rec_size,'total':total,'zero':z,'magic':magic,'title':ss[0],'display_title':ss[1],'body1':ss[2],'body2':ss[3]})
print('records',len(rows),'bytes',len(b),'total values',sorted(set(r['total'] for r in rows)),'magic',sorted(set(r['magic'] for r in rows))[:20],'zero',sorted(set(r['zero'] for r in rows)))
print('index first/last',rows[0]['index'],rows[-1]['index'],'unique',len(set(r['index'] for r in rows)))
print('body_equal',sum(r['body1']==r['body2'] for r in rows),'/',len(rows))
print('chars title',sum(len(r['title']) for r in rows),'body1',sum(len(r['body1']) for r in rows),'body2',sum(len(r['body2']) for r in rows))
print('body1 median/max',statistics.median(len(r['body1']) for r in rows),max(len(r['body1']) for r in rows))
for r in rows[:30]:
 print(r['index'],repr(r['title']),repr(r['body1'][:180]),'eq',r['body1']==r['body2'])
out=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\keyword_fix5');out.mkdir(parents=True,exist_ok=True)
(out/'keyword_en.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (out/'keyword_en.tsv').open('w',encoding='utf-8-sig',newline='') as f:
 f.write('index\ttitle\tbody1\tbody2_equal\n')
 for r in rows:f.write(f"{r['index']}\t{r['title'].replace(chr(9),' ')}\t{r['body1'].replace(chr(9),' ').replace(chr(10),'\\n')}\t{int(r['body1']==r['body2'])}\n")
