from pathlib import Path
import json
O=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\05_build\keyword_fix5')
for fn in ['keyword_zh_01_35.json','keyword_zh_36_71.json']:
 p=O/fn;d=json.loads(p.read_text(encoding='utf-8'))
 def setv(i,title=None,desc=None):
  k=str(i);v=d[k]
  if title is not None:v[0]=title
  if desc is not None:v[1]=desc
 if fn.startswith('keyword_zh_01'):
  setv(10,'奇鲁奇鲁与米契鲁','“奇鲁奇鲁”和“米契鲁”是莫里斯·梅特林克戏剧《青鸟》中两名角色的日语音译。他们是一对兄妹，原名分别为Tyltyl和Mytyl。')
  setv(14,desc='《蒲公英女孩》是罗伯特·F·Young创作的科幻短篇小说。故事讲述中年男子马克·伦道夫遇到一名年纪只有他一半、并声称来自240年后未来的少女。')
  setv(35,desc='吉备团子是日本西部的特色团子，在日本颇有名气，并与民间故事《桃太郎》有很深的联系。')
 else:
  setv(44,desc='明太子是以明太鱼卵盐渍调味制成的食品，通常带有辣味。')
  setv(46,desc='桃太郎是日本著名民间故事的主人公。他用吉备团子招募了狗、猴子和野鸡作为伙伴，一同踏上讨伐鬼怪的旅程。')
  setv(57,desc='正坐是一种跪坐姿势，双膝跪地后让身体坐在脚跟或脚掌上。')
  setv(66,desc='鳗鱼派是日本浜松的特色酥脆黄油饼干，调味中加入了鳗鱼提取物。')
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 print('UPDATED',fn)
