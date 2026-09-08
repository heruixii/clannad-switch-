import csv, pathlib, collections
root=pathlib.Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
R=list(csv.DictReader(open(root/'03_text/matched/pc_control_parallel_v3/all.tsv',encoding='utf-8-sig'),delimiter='\t'))
S={'anchor','equal-segment','name-event','unique-gap','manual-gap','partial-gap'}
C=collections.Counter()
for r in R:
    if r['status'] not in S: continue
    a=r['jp_speaker'].strip(' \"')
    b=r['zh_speaker'].strip(' \"')
    if a and b: C[(a,b)] += 1
for (a,b),n in C.most_common(120):
    print(n, a, '=>', b)
