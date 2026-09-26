l0=bytes.fromhex('43395452000404060301030200040301000205010003020a020300010b030200010f030102004792')
l1=bytes.fromhex('43395452010404060200010302040301020007020003010a010002030b030002010d02010300ada9')

for name,d in [('lane0',l0),('lane1',l1)]:
    print(f'=== {name} ===')
    print('magic',d[:4],'laneid',d[4],'byte5',d[5])
    body=d[5:-2]
    print('body:',' '.join(f'{b:02d}' for b in body))
    # Try parse: repeated [n][n values] groups
    p=0; groups=[]
    while p<len(body):
        n=body[p]; grp=list(body[p+1:p+1+n]); groups.append((n,grp)); p+=1+n
    print('as [len][vals] groups:')
    for n,g in groups:
        print(f'   len={n} vals={g}')
