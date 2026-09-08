import os
os.environ['HF_HOME']=r'D:\switch游戏\个人汉化\clannad\汉化工作\tools\hf_cache'
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
import torch,csv,re
from pathlib import Path
mid='neverLife/nllb-200-distilled-600M-ja-zh'
print('loading',mid,flush=True)
tok=AutoTokenizer.from_pretrained(mid,src_lang='jpn_Jpan')
model=AutoModelForSeq2SeqLM.from_pretrained(mid,device_map='cpu')
model.eval();torch.set_num_threads(20)
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\switch_pc_v10\unmatched.tsv')
rows=[]
with p.open('r',encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if len(r['jp_text'])>=6:rows.append(r)
  if len(rows)>=20:break
# protect switch formatting/control tokens and speaker prefix by translating body only
CTRL=re.compile(r'(\$[A-Za-z]+(?:\([^)]*\))?(?:\d{3}(?:,\d+)?)?|[＊％][Ａ-ＺA-Z]|\*\w+)')
def body(s):
 s=s.replace('\\n','\n').replace('\\r','\r')
 if s.startswith('`') and '@' in s:return s.split('@',1)[1]
 return s
texts=[body(r['jp_text']) for r in rows]
b=tok(texts,return_tensors='pt',padding=True,truncation=True,max_length=256)
with torch.inference_mode():
 out=model.generate(**b,forced_bos_token_id=tok.convert_tokens_to_ids('zho_Hans'),max_new_tokens=256,num_beams=3)
trs=tok.batch_decode(out,skip_special_tokens=True)
for r,t in zip(rows,trs):print(f"{r['scene']}\t{r['code_index']}\tJP={r['jp_text']}\tEN={r['en_text']}\tNLLB={t}",flush=True)
