# module index -> signature byte, from tag-switch emulation (byte->slot inverted)
byte2slot={0x22:8,0x31:2,0x35:10,0x38:1,0x3a:12,0x3c:9,0x46:17,0x49:4,0x6b:6,0x6d:14,
           0x84:3,0x90:11,0x9d:0,0xa9:7,0xc0:18,0xc1:16,0xd2:5,0xd3:19,0xd4:13,0xd5:15}
slot2byte={v:k for k,v in byte2slot.items()}
modules=['o3','o4','o5','dx','da','ds','c7','c8','cf','cr','sn','g8','x3','mh','ml','xs','lc','zl','bz','xz']
mod2byte={modules[i]:slot2byte[i] for i in range(20)}
print('module -> byte:')
for m in modules: print(f'  {m} = {mod2byte[m]:#04x}')

lane0=['o4','da','c8','cr','x3','ml','lc']
lane1=['o4','dx','c7','cf','g8','ml','lc']  # newest

b0=bytes(mod2byte[m] for m in lane0)
b1=bytes(mod2byte[m] for m in lane1)
print('lane0 bytes:', b0.hex())
print('lane1 bytes:', b1.hex())
print()
print('CANDIDATES:')
print('lane0+lane1 :', 'HTF{r9_'+(b0+b1).hex()+'}')
print('lane1+lane0 :', 'HTF{r9_'+(b1+b0).hex()+'}')
print('lane1 only  :', 'HTF{r9_'+b1.hex()+'}')
print('lane0 only  :', 'HTF{r9_'+b0.hex()+'}')
# also raw module strings
print('lane1 str   :', 'HTF{r9_'+''.join(lane1)+'}')
print('lane0+1 str :', 'HTF{r9_'+''.join(lane0+lane1)+'}')
