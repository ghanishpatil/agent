prof={
'002':{8:'f7535567',11:'cc583f4d',13:'1b37',14:'40c8cc59',16:'fb4eea48',12:'0002'},
'006':{8:'f7535567',11:'cc583f4d',13:'1c37',14:'990bdb03',16:'fb4eea48',12:'0002'},
'008':{8:'f7535567',11:'58804bc5',13:'ec3e',14:'990bdb03',16:'5e14b0ed',12:'0002'},
'003':{8:'a68d20eb',11:'cc583f4d',13:'1b37',14:'24ebc118',16:'fb4eea48',12:'0102'},
'009':{8:'a68d20eb',11:'58804bc5',13:'ec3e',14:'fd28d642',16:'5e14b0ed',12:'0102'},
'010':{8:'a68d20eb',11:'cc583f4d',13:'1c37',14:'fd28d642',16:'fb4eea48',12:'0102'},
}
allp=list(prof)
def xor(vals):
    n=min(len(v)//2 for v in vals); b=[bytes.fromhex(v) for v in vals]
    o=bytearray(n)
    for x in b:
        for i in range(n): o[i]^=x[i]
    return bytes(o).hex()

print('=== per-profile 14-byte (slot8+11+13+14) ===')
for p in allp:
    cand=prof[p][8]+prof[p][11]+prof[p][13]+prof[p][14]
    print(p, cand, '(len',len(cand)//2,')')
print()
print('=== per-profile (slot8+11+14+13) alt order ===')
for p in allp:
    cand=prof[p][8]+prof[p][11]+prof[p][14]+prof[p][13]
    print(p, 'HTF{r9_'+cand+'}')
print()
# distinct unique data words -> maybe the 14 bytes are the SET of unique values in canonical order
for slot in [8,11,13,14,16]:
    print('slot',slot,'unique:',sorted(set(prof[p][slot] for p in allp)))
