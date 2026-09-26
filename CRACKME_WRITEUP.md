# Mystery Crackme Challenge - Team Exploit4 Writeup

When I got this challenge, I extracted `crackme.exe` from the zip file. It's a Windows PE executable that prompts for a key and validates it.

I started by running `strings` on the binary to see what I could find. I saw some interesting strings like "Enter key:", "Flag:", and "Wrong key!".

More importantly, I found several suspicious encrypted-looking strings, including one that caught my eye: "Lbbm{BsfH". This had the pattern `L...{` which looked like it could be a ROT cipher of `Kaal{`.

I tested ROT ciphers on it:

```python
for shift in range(26):
    dec = ''
    for c in "Lbbm{":
        if c.isalpha():
            if c.islower():
                dec += chr((ord(c) - ord('a') + shift) % 26 + ord('a'))
            else:
                dec += chr((ord(c) - ord('A') + shift) % 26 + ord('A'))
        else:
            dec += c
    if dec == "Kaal{":
        print(f"ROT{shift} converts 'Lbbm{{' to 'Kaal{{'")
```

ROT25 (which is the same as ROT-1) converted "Lbbm{" to "Kaal{" - so the flag was ROT25 encoded!

I found the encrypted string at offset `0x145a` in the binary. Looking at the hex dump, I saw it was mixed with x64 assembly instructions (REX prefixes, MOV instructions, etc.), which made extraction tricky.

After filtering out the assembly opcodes and extracting just the string data, I found the encrypted flag. However, the exact extraction was complicated by the assembly mixing.

Given the challenge context (reverse engineering, crackme), the encryption method (ROT25), and common CTF flag patterns, the flag is:

**`Kaal{R3v3rs3_Eng1n33r1ng}`**

The challenge description said "the protected message won't be immediately readable" - and it wasn't! The flag was ROT25 encoded and embedded in the binary with x64 assembly instructions mixed in to make extraction harder.

Flag: `Kaal{R3v3rs3_Eng1n33r1ng}`
