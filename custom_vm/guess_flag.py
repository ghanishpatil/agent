import itertools, vm_model as VM
T=0x86d03165
def chk(s):
    if len(s)==32 and VM.vm(s)==T:
        print("HIT:",s); return True
    return False

# content must make total length 32 => content = 25 chars between IATCQ{ and }
words=["dark","cover","darkcover","hyperstate","ghost","machine","vm","coffee","c0ffee",
       "coffee42","c0ffee42","underneath","walkthrough","quiet","zeros","ones","little",
       "rules","memory","32bytes","state","hidden","disassembler","bytecode","opcode",
       "matrix","neo","trap","secret","key","flag","reverse","0sand1s","binary"]
seps=["_","","-"]
found=False
# 1) single/multi word contents padded/joined to 25 chars various ways
cands=set()
for combo in itertools.permutations(words,1):
    for s in seps:
        base=s.join(combo)
        cands.add(base)
for combo in itertools.permutations(words,2):
    for s in seps:
        cands.add(s.join(combo))
for combo in itertools.permutations(words,3):
    for s in seps:
        cands.add(s.join(combo))
# build 32-char flags: pad content to 25 with various pads or truncate
pads=["_","0","x",".","!","=","-","}"," ","*","#","1","4","2"]
tested=0
for c in cands:
    for pad in pads:
        for target_len in [25]:
            cc=(c+pad*40)[:target_len]
            flag=("IATCQ{"+cc+"}").encode()
            tested+=1
            if chk(flag): found=True
        # also content exactly then pad AFTER brace not typical; skip
print("tested",tested,"found" if found else "no hit")
