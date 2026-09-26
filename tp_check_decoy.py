import os, re, sqlite3
con=sqlite3.connect('tp_files/var__cache__deltaforge__historian_cache.db')
q=set()
for (c,) in con.execute('SELECT untrusted_content FROM analyst_queue'):
    for m in re.findall(r'HTF\{[^}]*\}', c):
        q.add(m)
img=open(os.path.join('temporal_paradox','Temporal Paradox','gateway_snapshot.img'),'rb').read()
disk=set(m.decode('latin1') for m in re.findall(rb'HTF\{[^}]*\}', img))
cand='HTF{r9_a68d20eb58804bc5ec3efd28d642}'
alt ='HTF{r9_f753556758804bc5ec3e990bdb03}'
print('decoys in analyst_queue:', len(q))
print('HTF{} strings on disk   :', len(disk))
print('candidate is a planted decoy?', cand in q or cand in disk)
print('alt       is a planted decoy?', alt in q or alt in disk)
print('a few decoys:', list(q)[:4])
