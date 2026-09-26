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
def crop(x0,x1,name,scale=6):
    ys=[y for x in range(x0,x1) for y in range(len(grid[x])) if grid[x][y]==TARGET]
    if not ys: 
        print('empty',name); return
    y0,y1=min(ys),max(ys)
    W=x1-x0; H=y1-y0+1
    img=Image.new('L',(W,H),255); px=img.load()
    for x in range(x0,x1):
        for y in range(y0,y1+1):
            if y<len(grid[x]) and grid[x][y]==TARGET: px[x-x0,y-y0]=0
    img=img.resize((W*scale,H*scale),Image.NEAREST)
    img.save(fr'f:\mission-git-hackss\mission-git-hackss\{name}.png')
    print('saved',name, 'x',x0,x1,'y',y0,y1)
# the '73' area was around segments 15-17 (x 3473..3979) and 'd' 4017..4199
crop(3450,3660,'char_7')   # the 7
crop(3600,3800,'char_3')   # the 3
crop(3800,4200,'char_d')   # the d (may clip)
# the '1' in crimson: segment near x 933-1155 region -> zoom
crop(900,1200,'char_1')
