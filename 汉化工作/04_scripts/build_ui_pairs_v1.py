from pathlib import Path
import csv,struct,json
R=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
dirs={
 'SYSCG':R/'03_text/ui_work/SYSCG.PAK_unpacked',
 'PARTS':R/'03_text/ui_work/PARTS.PAK_unpacked',
 'MANUAL':R/'03_text/switch_work/paks/MANUAL.PAK_unpacked',
}
def dim(p):
 b=p.read_bytes();return struct.unpack_from('<HH',b,8) if len(b)>=12 and b[:2]==b'CZ' else (None,None)
pairs=[]
# explicit core
for pak,a,b in [('SYSCG','MCM_TITLES','MCM_TITLES_EN'),('SYSCG','MN_EX_BG01','MN_EX_BG01_EN'),('SYSCG','MN_EX_BG03','MN_EX_BG03_EN'),('SYSCG','NAMEBASE','NAMEBASE_EN'),('SYSCG','NAME','NAME_EN'),('PARTS','CONFIG_BG','CONFIG_BG_EN'),('PARTS','CONFIG_TAB','CONFIG_TAB_EN'),('PARTS','SYSTEM_ICON','SYSTEM_ICON_EN')]:
 pa,pb=dirs[pak]/a,dirs[pak]/b;pairs.append((pak,a,b,*dim(pa),*dim(pb)))
# manual EN_x -> x
for en in sorted(dirs['MANUAL'].glob('EN_*')):
 jp=dirs['MANUAL']/en.name[3:]
 if jp.exists():pairs.append(('MANUAL',jp.name,en.name,*dim(jp),*dim(en)))
print(json.dumps({'pairs':len(pairs),'same_dim':sum(1 for r in pairs if r[3:5]==r[5:7]),'diff_dim':[(r[0],r[1],r[2],r[3:5],r[5:7]) for r in pairs if r[3:5]!=r[5:7]]},ensure_ascii=False,indent=2))
out=R/'03_text/ui_work/ui_language_pairs.tsv'
with out.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['pak','jp','en','jp_w','jp_h','en_w','en_h']);w.writerows(pairs)
