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

from PIL import Image
TARGET=122
# find bounding box of target blocks
minx,maxx,miny,maxy=maxX,0,maxY,0
for x in range(maxX):
    col=grid[x]
    for y in range(len(col)):
        if col[y]==TARGET:
            minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
print('bbox', minx,maxx,miny,maxy)
# render whole with only target black
img=Image.new('RGB',(maxX,maxY),(255,255,255))
px=img.load()
for x in range(maxX):
    col=grid[x]
    for y in range(len(col)):
        if col[y]==TARGET:
            px[x,y]=(0,0,0)
img.save(r'f:\mission-git-hackss\mission-git-hackss\letters_only.png')
# also crop tight
crop=img.crop((max(0,minx-10),max(0,miny-10),min(maxX,maxx+10),min(maxY,maxy+10)))
crop.save(r'f:\mission-git-hackss\mission-git-hackss\letters_crop.png')
print('saved')
