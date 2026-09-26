import struct
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
def fi(t): return t<len(tfi) and tfi[t]==1
maxX,maxY=4200,1200
p=599; d=data
grid=[]
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
        btype=-1
        if has_block:
            if ext_block: btype=struct.unpack('<H',d[p:p+2])[0]; p+=2
            else: btype=d[p]; p+=1
            if fi(btype): p+=4
            if block_painted: p+=1
        if has_wall:
            p+=1
            if wall_painted: p+=1
        if liq or liq_sh: p+=1
        if ext_wall: p+=1
        if rle==2: mult=struct.unpack('<H',d[p:p+2])[0]+1; p+=2
        elif rle==1: mult=d[p]+1; p+=1
        else: mult=1
        for _ in range(mult):
            column.append(btype if has_block else -1)
            if len(column)>=maxY: break
    grid.append(column)
TARGET=122
# column has letter if any type-122 in main letter band (y 129..500)
colhas=[]
for x in range(maxX):
    col=grid[x]
    has=any(col[y]==TARGET for y in range(129,500) if y<len(col))
    colhas.append(has)
# find runs of consecutive True separated by gaps
segs=[]
x=0
while x<maxX:
    if colhas[x]:
        s=x
        while x<maxX and colhas[x]: x+=1
        segs.append((s,x-1))
    else:
        x+=1
# merge tiny gaps within a character (gap < 6 columns => same char)
merged=[]
for s,e in segs:
    if merged and s-merged[-1][1] <= 5:
        merged[-1]=(merged[-1][0],e)
    else:
        merged.append((s,e))
print('num character-ish segments:', len(merged))
for i,(s,e) in enumerate(merged):
    print(i, 'x',s,'-',e,'width',e-s+1)
