from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
import torch,csv
from pathlib import Path
model_id='Helsinki-NLP/opus-mt-ja-zh'
print('loading',model_id,flush=True)
tok=AutoTokenizer.from_pretrained(model_id)
model=AutoModelForSeq2SeqLM.from_pretrained(model_id)
model.eval();torch.set_num_threads(20)
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\03_text\matched\switch_pc_v10\unmatched.tsv')
rows=[]
with p.open('r',encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  if len(r['jp_text'])>=6:
   rows.append(r)
  if len(rows)>=20:break
texts=[r['jp_text'] for r in rows]
b=tok(texts,return_tensors='pt',padding=True,truncation=True,max_length=256)
with torch.inference_mode(): out=model.generate(**b,max_new_tokens=256,num_beams=3)
trs=tok.batch_decode(out,skip_special_tokens=True)
for r,t in zip(rows,trs):
 print(f"{r['scene']}\t{r['code_index']}\tJP={r['jp_text']}\tEN={r['en_text']}\tZH={t}",flush=True)
