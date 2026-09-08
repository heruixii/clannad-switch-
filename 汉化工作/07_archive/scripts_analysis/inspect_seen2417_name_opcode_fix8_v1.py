from pathlib import Path
import json,re
P=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_export\script_json\SEEN2417.json')
d=json.loads(P.read_text(encoding='utf-8-sig'))
# recursively locate objects containing Tomoya / 朋也 / 8334 / 8277
hits=[]
def walk(x,path=()):
    if isinstance(x,dict):
        s=json.dumps(x,ensure_ascii=False)
        if any(k in s for k in ['Tomoya','朋也','8334','8277']):
            hits.append((path,x))
        for k,v in x.items(): walk(v,path+(k,))
    elif isinstance(x,list):
        for i,v in enumerate(x): walk(v,path+(i,))
walk(d)
print('hits',len(hits))
shown=set()
for path,x in hits:
    # only leaf-ish opcode dicts, avoid parent duplicates
    ident=id(x)
    if ident in shown: continue
    shown.add(ident)
    if any(k in x for k in ['opcode','op','name','mnemonic','args','text','raw']):
        print('\nPATH',path)
        print(json.dumps(x,ensure_ascii=False,indent=2)[:5000])
# inspect commands list around exact command with Tomoya
cmds=None
for key in ['commands','ops','instructions','items']:
    if isinstance(d,dict) and isinstance(d.get(key),list): cmds=d[key];print('TOPLIST',key,len(cmds));break
if cmds:
    for i,c in enumerate(cmds):
        s=json.dumps(c,ensure_ascii=False)
        if 'Tomoya' in s or '朋也' in s or '#8334' in s:
            print('\nAROUND INDEX',i)
            for j in range(max(0,i-12),min(len(cmds),i+18)):
                print(j,json.dumps(cmds[j],ensure_ascii=False)[:1500])

