from capstone import *
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
target='mov w8, #0x1010101'
for immr in range(64):
  for imms in range(64):
    word=0x32000000 | (immr<<16) | (imms<<10) | (31<<5) | 8
    b=word.to_bytes(4,'little')
    xs=list(md.disasm(b,0))
    if xs:
      s=f'{xs[0].mnemonic} {xs[0].op_str}'
      if s==target:
        print(hex(word),b.hex(),s,'immr',immr,'imms',imms)
