import struct
from PIL import Image
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
minx,maxx,miny,maxy=maxX,0,maxY,0
for x in range(maxX):
    col=grid[x]
    for y in range(len(col)):
        if col[y]==TARGET:
            minx=min(minx,x); maxx=max(maxx,x); miny=min(miny,y); maxy=max(maxy,y)
print('bbox',minx,maxx,miny,maxy)
W=maxx-minx+1; H=maxy-miny+1
img=Image.new('L',(W,H),255)
px=img.load()
for x in range(minx,maxx+1):
    col=grid[x]
    for y in range(miny,maxy+1):
        if y<len(col) and col[y]==TARGET:
            px[x-minx,y-miny]=0
# split into two halves so each is legible when scaled
scale=4
half=W//2
for idx,(x0,x1) in enumerate([(0,half),(half,W)]):
    part=img.crop((x0,0,x1,H))
    part=part.resize((part.width*scale, part.height*scale), Image.NEAREST)
    part.save(fr'f:\mission-git-hackss\mission-git-hackss\zoom_{idx}.png')
print('saved zoom_0.png zoom_1.png')
