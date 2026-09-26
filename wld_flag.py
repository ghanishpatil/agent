import struct
from collections import Counter
data = open(r'f:\mission-git-hackss\mission-git-hackss\AWholeNewWorld.wld','rb').read()
o=24
cnt=struct.unpack('<h',data[o:o+2])[0]; o+=2
o+=4*cnt
imp_count=struct.unpack('<h',data[o:o+2])[0]; o+=2
imp_bytes=(imp_count+7)//8
tfi=[]
for k in range(imp_bytes):
    v=data[o+k]
    for i in range(8): tfi.append((v>>i)&1)
def frame_important(t):
    return t<len(tfi) and tfi[t]==1
maxX,maxY=4200,1200

def parse(start):
    p=start; d=data; grid=[]
    for _ in range(maxX):
        column=[]
        while len(column)<maxY:
            f1=d[p]; p+=1
            f2=f3=f4=0
            if f1&1:
                f2=d[p]; p+=1
                if f2&1:
                    f3=d[p]; p+=1
                    if f3&1:
                        f4=d[p]; p+=1
            has_block=(f1>>1)&1; ext_block=(f1>>5)&1
            block_painted=(f3>>3)&1
            has_wall=(f1>>2)&1; ext_wall=(f3>>6)&1; wall_painted=(f3>>4)&1
            liq=(f1>>3)&3; liq_sh=(f3>>7)&1
            rle=(f1>>6)&3
            btype=-1; paint=0
            if has_block:
                if ext_block: btype=struct.unpack('<H',d[p:p+2])[0]; p+=2
                else: btype=d[p]; p+=1
                if frame_important(btype): p+=4
                if block_painted: paint=d[p]; p+=1
            if has_wall:
                p+=1
                if wall_painted: p+=1
            if liq or liq_sh: p+=1
            if ext_wall: p+=1
            if rle==2: mult=struct.unpack('<H',d[p:p+2])[0]+1; p+=2
            elif rle==1: mult=d[p]+1; p+=1
            else: mult=1
            for _ in range(mult):
                column.append((btype if has_block else -1, paint))
                if len(column)>=maxY: break
        grid.append(column)
    return grid
grid=parse(599)

# The letters appear brown & in the sky region (top). Count block types in the upper band where letters float (y ~ 200-360) but only isolated ones.
# Better: find the block type used for letters by looking at columns in sky. Letters are surrounded by sky(-1).
# Count paint values and types in region y 150-380
typecount=Counter(); paintcount=Counter()
for x in range(maxX):
    col=grid[x]
    for y in range(150,400):
        if y<len(col):
            t,pt=col[y]
            if t!=-1:
                typecount[t]+=1; paintcount[(t,pt)]+=1
print('top block types (y150-400):', typecount.most_common(15))
print('top (type,paint):', paintcount.most_common(15))
