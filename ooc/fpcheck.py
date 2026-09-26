import hashlib, os, re

freeze = open(r'F:\mission-git-hackss\mission-git-hackss\.agent\docs\phase5_freeze.md', encoding='utf-8').read()
# parse "  <sha256>  ctf_agent/....py"
manifest = {}
for m in re.finditer(r'([0-9a-f]{64})\s+(ctf_agent/\S+)', freeze):
    manifest[m.group(2)] = m.group(1)

src_root = r'F:\mission-git-hackss\mission-git-hackss\.agent\src'
mismatches = []
matched = 0
missing = []
for rel in manifest:
    full = os.path.join(src_root, rel.replace('/', os.sep))
    if not os.path.exists(full):
        missing.append(rel); continue
    d = hashlib.sha256(open(full, 'rb').read()).hexdigest()
    if d == manifest[rel]:
        matched += 1
    else:
        mismatches.append(rel)

print('manifest files:', len(manifest))
print('matched (raw bytes):', matched)
print('mismatched:', len(mismatches))
for r in mismatches:
    print('   DIFF:', r)
print('missing:', missing)

# Try CRLF<->LF normalized hashing on mismatches
print('--- newline-normalized retry on mismatches ---')
for rel in mismatches:
    full = os.path.join(src_root, rel.replace('/', os.sep))
    raw = open(full, 'rb').read()
    lf = raw.replace(b'\r\n', b'\n')
    crlf = lf.replace(b'\n', b'\r\n')
    hlf = hashlib.sha256(lf).hexdigest()
    hcrlf = hashlib.sha256(crlf).hexdigest()
    tag = 'LF-match' if hlf == manifest[rel] else ('CRLF-match' if hcrlf == manifest[rel] else 'still-diff')
    print('  ', rel, tag)
