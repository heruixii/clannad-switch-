from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\patch_title_rgba_fix3_v30.py')
s=p.read_text(encoding='utf-8-sig')
old="erase=cv2.dilate(erase,np.ones((3,3),np.uint8),iterations=2);alpha[erase.astype(bool)]=0\ndef fit"
new="erase=cv2.dilate(erase,np.ones((3,3),np.uint8),iterations=2);alpha[erase.astype(bool)]=0\n# Also remove the old normal-state English RGB glyphs. The engine may sample CZ3 channels as separate states, so alpha-only cleanup is insufficient.\nfor c in range(3): arr[:,:,c]=cv2.inpaint(arr[:,:,c],(erase*255).astype(np.uint8),3,cv2.INPAINT_TELEA)\ndef fit"
assert old in s
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
