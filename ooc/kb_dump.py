import sys, os
sys.path.insert(0, r'F:\mission-git-hackss\mission-git-hackss\.agent\src')
from ctf_ingest.store import KnowledgeStore
from ctf_ingest.retrieval import records_from_store

kb_root = r'F:\mission-git-hackss\mission-git-hackss\.agent\knowledge'
corpora = ['jiaje_v1', 'jiaje_redbud_v1/store', 'domectf_v1/store', 'local_writeups']
all_records = []
for c in corpora:
    try:
        all_records.extend(list(records_from_store(KnowledgeStore(os.path.join(kb_root, c)))))
    except Exception:
        pass

wanted = ['switch it up', 'student erp', 'up? down', 'cloudnine']
for rec in all_records:
    tl = rec.title.lower()
    if any(w in tl for w in wanted):
        print('\n' + '=' * 70)
        print('TITLE:', rec.title, '| cat:', rec.metadata.category, '| pts:', rec.metadata.points)
        print('SUMMARY:', (rec.summary or '')[:400])
        print('TECHNIQUES:', [t.technique_id for t in rec.techniques])
        print('--- trajectory steps ---')
        for s in rec.trajectory.steps:
            txt = (s.text or '').strip().replace('\n', ' ')
            if txt:
                print(f'  [{s.kind.value}] {txt[:220]}')
