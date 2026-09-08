from pathlib import Path
import struct,subprocess,json,hashlib
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作'); P=R/'03_text/ui_work/SYSCG2.PAK'; O=R/'05_build/syscg2_probe';O.mkdir(parents=True,exist_ok=True);EXE=R/'tools/LuckSystem/tools/cztool/cztool.exe'
b=P.read_bytes();hl,fc,idstart,bs,*rest=struct.unpack_from('<9I',b,0);pos=40
rows=[]
for i in range(fc):
 bo,ln=struct.unpack_from('<II',b,pos+i*8);data=b[bo*bs:bo*bs+ln];raw=O/f'ID_{idstart+i}';raw.write_bytes(data);png=O/f'ID_{idstart+i}.png'
 r=subprocess.run([str(EXE),'export',str(raw),str(png)],capture_output=True,text=True,encoding='utf-8',errors='replace')
 meta={'index':i,'id':idstart+i,'offset':bo*bs,'length':ln,'magic':data[:4].hex(),'export_rc':r.returncode}
 if png.exists():
  from PIL import Image
  im=Image.open(png);meta['width']=im.width;meta['height']=im.height;meta['mode']=im.mode
 rows.append(meta)
print(json.dumps({'hl':hl,'fc':fc,'idstart':idstart,'block':bs,'rows':rows},ensure_ascii=False,indent=2));(O/'inventory_v32.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
