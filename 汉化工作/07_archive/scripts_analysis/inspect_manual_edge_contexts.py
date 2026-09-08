from pathlib import Path
import sys,csv
sys.path.insert(0,str(Path(__file__).parent))
from align_by_control_anchors import scene
ROOT=Path(__file__).resolve().parents[1]
for sc,ji,zi in [('SEEN4418',239,245),('SEEN4428',394,397),('SEEN6416',199,200)]:
 J,Z,_=scene(ROOT,sc[4:])
 print('\n###',sc,'TARGET',ji,zi)
 print('JP')
 for i in range(max(0,ji-5),min(len(J),ji+6)):print(i,J[i]['text'])
 print('ZH')
 for i in range(max(0,zi-5),min(len(Z),zi+6)):print(i,Z[i]['text'])
