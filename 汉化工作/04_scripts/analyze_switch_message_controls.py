from pathlib import Path
import csv,re,collections,json
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\switch_extracted\switch_messages.tsv')
CTRL=re.compile(r'\$(?:S(?:U)?\d{3}(?:,\d+)?|W(?:\([^)]*\))?|[A-Za-z]+\d*|\[[^\]]*\])')
rows=[]
with p.open('r',encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
c=collections.Counter(); inline=[];samples=[]
for r in rows:
 s=r['jp_text']; toks=list(CTRL.finditer(s))
 if not toks:continue
 c['rows_with_control']+=1;c['control_tokens']+=len(toks)
 body=s.split('@',1)[1] if s.startswith('`') and '@' in s else s
 ms=list(CTRL.finditer(body))
 # non-leading if visible nonspace text exists before token
 for m in ms:
  pre=body[:m.start()]
  if re.search(r'[^\s`@]',pre):
   c['rows_inline_control']+=1;inline.append(r);break
 if len(samples)<50:samples.append((r['scene'],r['code_index'],s))
print(json.dumps(dict(c),indent=2));print('INLINE_SAMPLE')
for r in inline[:80]:print(r['scene'],r['code_index'],repr(r['jp_text']))
