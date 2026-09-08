from pathlib import Path
import csv
ROOT=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作')
P=ROOT/'03_text/translated/message_targets_complete_v12.tsv'
rows=list(csv.DictReader(P.open('r',encoding='utf-8-sig',newline=''),delimiter='\t'))
M={(r['scene'],r['code_index']):r for r in rows}
# systematic historical corruption: Switch speaker ％Ｂ was decoded as 亾Ｂ in PC Chinese
fixed=0
for r in rows:
    if r['jp_text'].startswith('`％Ｂ@') and r['zh_text'].startswith('`亾Ｂ@'):
        r['zh_text']='`％Ｂ@'+r['zh_text'].split('@',1)[1];fixed+=1
# exact fixes for remaining runtime controls / player variables
F={
('SEEN0414','1116'):'$S065咚！',
('SEEN0415','3140'):'$W(c31)$S000,0呜啊啊啊啊啊啊啊啊啊啊啊啊──────…',
('SEEN0422','1167'):'`春原@「才不给＊Ａ看呢！」',('SEEN0422','1702'):'`春原@「才不给＊Ａ看呢！」',('SEEN0422','2185'):'`春原@「才不给＊Ａ看呢！」',
('SEEN1423','1384'):'`风子@「没关系。至少也比＊Ａ可靠。」',
('SEEN1426','3016'):'`古河@「如果＊Ａ也能一起帮忙，我会很高兴。」',
('SEEN1428','3353'):'这对％Ａ来说，应该是相当大的打击吧。',
('SEEN1430','467'):'$S065啊啊啊啊啊啊─────！',('SEEN1430','897'):'$S065啊啊啊啊啊啊─────！',('SEEN1430','969'):'$S065啊啊啊啊啊啊─────！',
('SEEN1513','819'):'如今，古河面包店的入口处…再也不会出现％Ａ的身影。',
('SEEN3425','571'):'`杏@$S040（………）',
('SEEN3426','360'):'$S081$SU000突突突突…',
('SEEN3507','2093'):'`春原@「我觉得和杏在一起的＊Ａ更自然。」',('SEEN3507','2207'):'`春原@『我觉得和杏在一起的＊Ａ更自然。』',
('SEEN5430','11606'):'`宫泽@「＊Ｂ在想什么呢？」',
('SEEN6417','1462'):'`古河@「不会的。＊Ａ个子高，又很帅…」',
('SEEN6419','2249'):'`＊Ｂ@「不，普通地写成＊Ａ，读作＊Ａ。」',
('SEEN6421','1070'):'$S065$SU000团子大家族…',
('SEEN6802_1','3438'):'我有些难为情，把视线移向站在％Ｄ身旁的女孩。',
('SEEN6802_1','3728'):'顺便介绍了还被％Ｄ抱着的汐。',
('SEEN6802_1','3828'):'％Ｄ先把汐放下，接着名叫风子的女孩把她抱了起来。',
('SEEN6811','4278'):'`＊Ｂ@「是我，＊Ａ。」',
('SEEN6811','4350'):'`渚@「＊Ｂ，怎么了？」',
('SEEN6811','9187'):'哦…原来店长会叫渚『＊Ａ君』啊。',
('SEEN7601','10787'):'$S065咚！',('SEEN7601','10889'):'$S065咚！',
}
for k,v in F.items():
    if k not in M:raise RuntimeError('missing '+str(k))
    M[k]['zh_text']=v;fixed+=1
with P.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
print('fixed',fixed,'explicit',len(F))
