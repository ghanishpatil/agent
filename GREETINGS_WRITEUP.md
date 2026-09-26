# Greetings - Reverse Engineering Writeup

When I opened the challenge, I was given a file called `greetings.zip`. The challenge description mentioned it was a "secure data package" intercepted from a courier, and that it might be some kind of communication program. Time to dig in.

I extracted the zip file and got a binary called `greetings` with no extension. First thing I did was check what kind of file this was:

```bash
xxd greetings | head
```

The file started with `7F 45 4C 46` - that's an ELF binary for Linux. But something felt off about it being just a compiled binary. I ran strings on it to see what was inside:

```bash
strings greetings | grep -i python
```

Boom! I saw references to:
- `python3.14`
- `pyiboot01_bootstrap`
- `pyimod01_archive`
- Tons of Python library imports (requests, json, pickle, etc.)

This wasn't just any binary - it was a PyInstaller-compiled Python application. PyInstaller is a tool that packages Python scripts into standalone executables, but here's the thing: it doesn't actually encrypt the code. It just bundles everything together. The original Python bytecode is still sitting there, waiting to be extracted.

I grabbed pyinstxtractor, a tool specifically designed to unpack PyInstaller binaries:

```bash
wget https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
python pyinstxtractor.py greetings
```

The output told me everything I needed to know:

```
[+] Processing greetings
[+] Pyinstaller version: 2.1+
[+] Python version: 3.14
[+] Length of package: 17489072 bytes
[+] Found 89 files in CArchive
[+] Beginning extraction...
[+] Possible entry point: greetings.pyc
[+] Successfully extracted pyinstaller archive
```

All the files got extracted to `greetings_extracted/`, and the main script was `greetings.pyc`. Now I had the compiled Python bytecode. I could have used a decompiler like uncompyle6, but I decided to just look at the raw bytecode for strings - sometimes that's faster.

I wrote a quick script to search for the flag pattern:

```python
#!/usr/bin/env python3
import re

pyc_file = "./greetings_extracted/greetings.pyc"

with open(pyc_file, 'rb') as f:
    data = f.read()
    
text = data.decode('latin-1', errors='ignore')
matches = re.findall(r'Kaal\{[^}]+\}', text)

if matches:
    print("[+] FLAG FOUND!")
    for match in matches:
        print(f"    {match}")
```

Ran it and there it was, hardcoded right in the bytecode:

```
[+] FLAG FOUND!
    Kaal{Py$nstaLLer_1s_N0t_Encrypt10n}
```

The flag itself is the lesson here: "PyInstaller is Not Encryption". The challenge was demonstrating that PyInstaller provides obfuscation through obscurity, not real security. The original bytecode stays intact inside the binary, and tools like pyinstxtractor can easily pull it out. If you're hardcoding sensitive data (flags, API keys, passwords) in Python and then using PyInstaller, anyone can extract it.

Here's the complete exploit script:

```python
#!/usr/bin/env python3
"""Complete Greetings exploit"""
import subprocess
import re
import os

# Extract PyInstaller archive
print("[*] Extracting PyInstaller archive...")
subprocess.run(['python', 'pyinstxtractor.py', 'greetings'])

# Read the extracted .pyc file
pyc_file = "./greetings_extracted/greetings.pyc"

print("[*] Searching for flag in bytecode...")
with open(pyc_file, 'rb') as f:
    data = f.read()
    
text = data.decode('latin-1', errors='ignore')
matches = re.findall(r'Kaal\{[^}]+\}', text)

if matches:
    print(f"\n[+] FLAG: {matches[0]}")
else:
    print("[-] Flag not found")
```

Flag: Kaal{Py$nstaLLer_1s_N0t_Encrypt10n}

Team Exploit4
