from pathlib import Path
import csv,re,collections,json
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
P=ROOT/'03_text/matched/pc_control_parallel_v4/all.tsv'
SAFE={'anchor','equal-segment','name-event','unique-gap','confirmed-gap','recursive-hard','highconf-anchor'}
def trim(s):return (s or '').strip(' \t\"')
def sp(s):
 m=re.match(r'^【([^】]+)】',trim(s));return m.group(1).strip(' \"') if m else ''
rows=list(csv.DictReader(open(P,encoding='utf-8-sig'),delimiter='\t'))
mp=collections.defaultdict(collections.Counter)
for r in rows:
 if r['status'] not in SAFE:continue
 a,b=sp(r['jp_text']),sp(r['zh_text'])
 if a and b:mp[a][b]+=1
out=[]
for a,c in mp.items():
 total=sum(c.values()); top=c.most_common(5);out.append({'jp':a,'total':total,'top':top,'conf':top[0][1]/total})
out.sort(key=lambda x:-x['total'])
print('speakers',len(out),'highconf',sum(x['conf']>=.95 for x in out))
for x in out[:100]:print(x['jp'].encode('unicode_escape').decode(),x['total'],round(x['conf'],3),[(b.encode('unicode_escape').decode(),n) for b,n in x['top']])
