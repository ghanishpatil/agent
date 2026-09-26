import struct, math, sys

data = open(r'f:\mission-git-hackss\mission-git-hackss\AWholeNewWorld.wld','rb').read()

class R:
    def __init__(self, d, o=0):
        self.d=d; self.o=o
    def i1(self):
        v=self.d[self.o]; self.o+=1; return v
    def i2(self):
        v=struct.unpack('<h',self.d[self.o:self.o+2])[0]; self.o+=2; return v
    def u2(self):
        v=struct.unpack('<H',self.d[self.o:self.o+2])[0]; self.o+=2; return v
    def i4(self):
        v=struct.unpack('<i',self.d[self.o:self.o+4])[0]; self.o+=4; return v
    def u4(self):
        v=struct.unpack('<I',self.d[self.o:self.o+4])[0]; self.o+=4; return v
    def i8(self):
        v=struct.unpack('<q',self.d[self.o:self.o+8])[0]; self.o+=8; return v
    def f4(self):
        v=struct.unpack('<f',self.d[self.o:self.o+4])[0]; self.o+=4; return v
    def f8(self):
        v=struct.unpack('<d',self.d[self.o:self.o+8])[0]; self.o+=8; return v
    def b(self):
        v=self.d[self.o]; self.o+=1; return v!=0
    def s(self):
        l=self.d[self.o]; self.o+=1; v=self.d[self.o:self.o+l].decode('latin1'); self.o+=l; return v
    def bits(self):
        v=self.d[self.o]; self.o+=1
        return [(v>>i)&1 for i in range(8)]

r=R(data,24)
cnt=r.i2()
ptrs=[r.i4() for _ in range(cnt)]
imp_count=r.i2()
imp_bytes=(imp_count+7)//8
tfi=[]
for _ in range(imp_bytes):
    v=r.i1()
    for i in range(8): tfi.append((v>>i)&1)
print('tileframeimportant bits', len(tfi))
print('header starts at', r.o)

# ---- header ----
name=r.s(); seed=r.s(); genver=r.i8()
r.o+=16  # guid
wid=r.i4()
left=r.i4(); right=r.i4(); top=r.i4(); bottom=r.i4()
maxY=r.i4(); maxX=r.i4()
print('name',name,'maxX',maxX,'maxY',maxY)
difficulty=r.i4()
for _ in range(8): r.b()  # drunk..zenith
r.i8()  # created_on datetime
r.i1()  # moon
# trees FourPartSplit
for _ in range(3): r.i4()
for _ in range(4): r.i4()
# moss FourPartSplit
for _ in range(3): r.i4()
for _ in range(4): r.i4()
r.i4(); r.i4(); r.i4()  # bg underground snow/jungle/hell
r.i4(); r.i4()  # spawn point
r.f8(); r.f8()  # underground/cavern level
r.f8()  # current time
r.b()  # is_daytime
r.u4()  # moon_phase
r.b(); r.b()  # blood moon, eclipse
r.i4(); r.i4()  # dungeon point
r.b()  # world evil
# 11 boss bools
for _ in range(11): r.b()
# 3 saved
for _ in range(3): r.b()
# 4 event defeats
for _ in range(4): r.b()
# shadow orbs: bool, bool, uint1
r.b(); r.b(); r.i1()
r.i4()  # altars smashed
r.b()  # hardmode
r.b()  # party doomed
r.i4(); r.i4(); r.i4(); r.f8()  # invasion delay/size/type/position
r.f8()  # slime rain
r.i1()  # sundial cooldown
r.b(); r.i4(); r.f4()  # rain
r.i4(); r.i4(); r.i4()  # hardmode ore 1/2/3
for _ in range(8): r.i1()  # bg forest,corruption,jungle,snow,hallow,crimson,desert,ocean
r.i4(); r.i2(); r.f4()  # clouds
acc=r.i4()
for _ in range(acc): r.s()
r.b()  # saved angler
r.i4()  # angler quest target
r.b(); r.b(); r.b()  # stylist, tax, golfer
r.i4()  # invasion size start
r.i4()  # cultist delay
mtc=r.i2()
for _ in range(mtc): r.i4()
r.b()  # sundial running
# 9 bools (fishron..everscream)
for _ in range(9): r.b()
# pillars defeated 4
for _ in range(4): r.b()
# lunar pillars present 4 + active
for _ in range(5): r.b()
r.b(); r.b()  # party center/natural
r.i4()  # party cooldown
pnc=r.i4()
for _ in range(pnc): r.i4()
r.b(); r.i4(); r.f4(); r.f4()  # sandstorm
r.b()  # bartender
r.b(); r.b(); r.b()  # old ones army tiers
for _ in range(5): r.i1()  # bg mushroom,underworld,forest2,3,4
r.b()  # combat book
r.i4(); r.b(); r.b(); r.b()  # lantern night
tvc=r.i4()
for _ in range(tvc): r.i4()
r.b(); r.b()  # halloween, xmas
r.i4(); r.i4(); r.i4(); r.i4()  # ore 1-4
r.b(); r.b(); r.b()  # pets
r.b(); r.b(); r.b()  # empress, queen slime, deerclops
# saved npcs block: nerdy,merchant,demo,partygirl,dyetrader,truffle,armsdealer,nurse,princess,combatbook2,peddler,slime cool,elder,clumsy,diva,surly,mystic,squire = 18
for _ in range(18): r.b()
r.b(); r.i1()  # moondial running, cooldown

tiles_start=r.o
print('TILES START (v1.4.4.9 layout):', tiles_start)
print('bytes there:', data[tiles_start:tiles_start+16].hex())
