import csv, pathlib, random
root=pathlib.Path(r"D:\switch游戏\个人汉化\clannad\汉化工作")
R=list(csv.DictReader(open(root/'03_text/matched/pc_control_parallel_v3/learned_anchor_candidates.tsv',encoding='utf-8-sig'),delimiter='\t'))
random.Random(20260907).shuffle(R)
for n,r in enumerate(R[:70],1):
    print(f"[{n}] {r['scene']} b{r['block_id']} {r['reason']} fp={r['fp_pair_count']} {r['jp_event_index']}->{r['zh_event_index']}")
    print(' JP:',r['jp_text'])
    print(' ZH:',r['zh_text'])
