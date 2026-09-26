import sys, os
sys.path.insert(0, r'F:\mission-git-hackss\mission-git-hackss\.agent\src')

from ctf_ingest.store import KnowledgeStore
from ctf_ingest.retrieval import KnowledgeRetriever, RetrievalQuery, records_from_store

kb_root = r'F:\mission-git-hackss\mission-git-hackss\.agent\knowledge'
corpora = ['jiaje_v1', 'jiaje_redbud_v1/store', 'domectf_v1/store', 'local_writeups']

all_records = []
for c in corpora:
    p = os.path.join(kb_root, c)
    try:
        recs = list(records_from_store(KnowledgeStore(p)))
        all_records.extend(recs)
        print(f'loaded {len(recs)} from {c}')
    except Exception as e:
        print(f'skip {c}: {str(e)[:80]}')

print('total records:', len(all_records))
if not all_records:
    sys.exit(0)

retr = KnowledgeRetriever.from_records(all_records)
for q in ['jinja2 server side template injection sandbox escape bypass',
          'flask session cookie privilege escalation role admin',
          'SSTI filter blocklist bypass attr globals',
          'template injection read config secret flag rce']:
    print('\n===== QUERY:', q)
    res = retr.retrieve(RetrievalQuery(text=q), k=4)
    for r in res:
        rec = r.record
        print(f'  [{r.score}] {rec.metadata.category} | {rec.title[:60]} | matched={r.matched_terms[:8]}')
        for t in rec.techniques[:3]:
            print(f'        tech: {t.technique_id} ({t.name[:40]})')
