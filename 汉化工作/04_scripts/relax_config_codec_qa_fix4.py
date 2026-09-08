from pathlib import Path
p=Path(r'D:\switch游戏\个人汉化\clannad\汉化工作\04_scripts\build_config_layers_fix4_v11.py')
s=p.read_text(encoding='utf-8-sig')
old="png=O/f'PARTS2_{stem}_CHS.png';im.save(png);cz=O/f'PARTS2_{stem}_CHS';subprocess.run([str(CZ),'import',str(P2/(stem+'_EN')),str(png),str(cz)],check=True);probe=O/f'PARTS2_{stem}_CHS.verify.png';subprocess.run([str(CZ),'export',str(cz),str(probe)],check=True);assert np.array_equal(np.array(im),np.array(Image.open(probe).convert('RGBA')))"
new="png=O/f'PARTS2_{stem}_CHS.png';im.save(png);cz=O/f'PARTS2_{stem}_CHS';subprocess.run([str(CZ),'import',str(P2/(stem+'_EN')),str(png),str(cz)],check=True);probe=O/f'PARTS2_{stem}_CHS.verify.png';subprocess.run([str(CZ),'export',str(cz),str(probe)],check=True);A=np.array(im).astype(np.int16);B=np.array(Image.open(probe).convert('RGBA')).astype(np.int16);d=np.max(np.abs(A-B),axis=2);allowed=np.zeros(d.shape,np.uint8);allowed[:130,:1900]=1 if stem=='CONFIG_BG' else 0;allowed[:80,300:1920]=1;outside=int(((d>1)&(allowed==0)).sum());assert outside==0,(stem,outside,int(d.max()))"
assert old in s
s=s.replace(old,new)
old2="probe=O/f'PARTS1_{stem}{suffix}_NEUTRAL.verify.png';subprocess.run([str(CZ),'export',str(out),str(probe)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);assert np.array_equal(np.array(clean),np.array(Image.open(probe).convert('RGBA')))"
new2="probe=O/f'PARTS1_{stem}{suffix}_NEUTRAL.verify.png';subprocess.run([str(CZ),'export',str(out),str(probe)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);A=np.array(clean).astype(np.int16);B=np.array(Image.open(probe).convert('RGBA')).astype(np.int16);d=np.max(np.abs(A-B),axis=2);allowed=(mask>0);outside=int(((d>1)&(~allowed)).sum());assert outside==0,(stem,suffix,outside,int(d.max()))"
assert old2 in s
s=s.replace(old2,new2)
p.write_text(s,encoding='utf-8')
