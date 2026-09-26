import struct, sys

data = open(r'f:\mission-git-hackss\mission-git-hackss\AWholeNewWorld.wld','rb').read()

# tileframeimportant
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

def parse_tiles(start):
    p=start
    d=data
    cols=[]
    col_types=[]  # per tile: block type or -1 for air
    while len(cols) < maxX:
        column=[]
        while len(column) < maxY:
            f1=d[p]; p+=1
            f2=f3=f4=0
            if f1&1:
                f2=d[p]; p+=1
                if f2&1:
                    f3=d[p]; p+=1
                    if f3&1:
                        f4=d[p]; p+=1
            has_block = (f1>>1)&1
            ext_block = (f1>>5)&1
            block_painted=(f3>>3)&1
            has_wall=(f1>>2)&1
            ext_wall=(f3>>6)&1
            wall_painted=(f3>>4)&1
            # liquid bits from f1 (3,4) and f3(7)
            liq = (f1>>3)&3
            liq_shimmer = (f3>>7)&1
            # rle from f1 bits 6,7
            rle=(f1>>6)&3
            btype=-1
            if has_block:
                if ext_block:
                    btype=struct.unpack('<H',d[p:p+2])[0]; p+=2
                else:
                    btype=d[p]; p+=1
                if frame_important(btype):
                    p+=4  # u2 u2
                if block_painted:
                    p+=1
            if has_wall:
                p+=1  # wall low
                if wall_painted: p+=1
            if liq!=0 or liq_shimmer:
                p+=1  # volume
            if ext_wall:
                p+=1  # wall high
            if rle==2:
                mult=struct.unpack('<H',d[p:p+2])[0]+1; p+=2
            elif rle==1:
                mult=d[p]+1; p+=1
            else:
                mult=1
            for _ in range(mult):
                column.append(btype if has_block else -1)
                if len(column)>=maxY: break
        cols.append(column)
    return cols, p

start=int(sys.argv[1]) if len(sys.argv)>1 else 599
cols,end=parse_tiles(start)
print('parsed columns', len(cols), 'end offset', end)
print('next bytes', data[end:end+20].hex())

# render
try:
    from PIL import Image
    img=Image.new('RGB',(maxX,maxY))
    px=img.load()
    for x in range(maxX):
        col=cols[x]
        for y in range(min(maxY,len(col))):
            t=col[y]
            if t==-1:
                px[x,y]=(135,206,235)  # sky
            else:
                # color by type mod for contrast
                px[x,y]=((t*37)%256,(t*91)%256,(t*53)%256)
    img.save(r'f:\mission-git-hackss\mission-git-hackss\world_render.png')
    print('saved world_render.png')
except Exception as e:
    print('render err', e)
