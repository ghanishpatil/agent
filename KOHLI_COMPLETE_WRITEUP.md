# Kohli Writeup
**Team Exploit4**

Flag: `Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_da82e0b4}`

so this challenge was called "Kohli never waits for the pitch report. He reads it ball by ball. Can you read this system the same way?" and honestly the cricket reference threw us off at first because we thought it was about sending requests repeatedly or doing some kind of rate limiting bypass. turns out the "ball by ball" thing was way more literal than we expected.

when you open the challenge URL you get this terminal interface called Kaalchakra Terminal. its got all the usual anti-debugging stuff - F12 blocking, debugger statements running in loops, context menu disabled, the whole package. basically trying to make you think theres something sophisticated going on. the terminal accepts commands and sends them as POST requests to `/run` with JSON like `{"cmd": "whatever"}`.

we tried the obvious stuff first. typed in `help`, got back `{"output":"0x00"}`. tried `ls`, same thing. `cat flag.txt`, still `0x00`. every single command just returned this hex zero output. so clearly the commands werent being executed normally or there was some kind of filter or encoding happening server-side.

at this point we were stuck for a bit trying different injection techniques, thinking maybe theres command injection or the terminal is parsing things weird. then someone actually looked at the hint again - "reads it ball by ball" - and realized this might be about character-by-character processing. like maybe each character needs to be read individually or theres some encoding per character.

we started digging through similar CTF challenges and found some references to character repetition encoding schemes. basically the idea is that each character in your input needs to be repeated a specific number of times based on some formula, and the server decodes it by grouping consecutive identical characters and checking if the count matches what it expects.

the formula we figured out was:
```python
def expected_repeat(ascii_val, position):
    return ((ascii_val % 5) + 3) + (position % 3)
```

so for each character, you take its ASCII value mod 5, add 3, then add the position in the string mod 3. that gives you how many times to repeat that character. the server groups all consecutive identical characters together, checks if the count matches the expected value, and if it does, outputs that character once. if the count is higher than expected it outputs the character twice.

once we had the formula we just needed to encode the right command. obviously we want `cat flag.txt` to read the flag file. so we wrote a quick script to encode it:

```python
def encode_command(target_cmd):
    encoded = ""
    position = 0
    for ch in target_cmd:
        ascii_val = ord(ch)
        repeat_count = expected_repeat(ascii_val, position)
        encoded += ch * repeat_count
        position += 1
    return encoded

target = "cat flag.txt"
encoded = encode_command(target)
```

this turns "cat flag.txt" into something like `cccccccaaaaaatttttt     ffffffllllllllaaaaaggggggg.......ttttxxxxtttttt` which is 70 characters of repeated letters and symbols. looks completely ridiculous but when you send it to the server it decodes back to the original command.

we sent the encoded string to `/run`:
```python
r = requests.post("http://chall-bcaad8ca.evt-207.glabs.ctf7.com/run", 
                  json={"cmd": encoded}, 
                  timeout=10)
```

and got back:
```json
{"output": "Kaal{r2p2t1t1on_add1ct10n_d2t2ct2d_da82e0b4}"}
```

flag captured. the flag itself is pretty funny because "r2p2t1t1on_add1ct10n_d2t2ct2d" is just leetspeak for "repetition addiction detected" which basically tells you the solution method if you already solved it.

the reason this works is the server has a custom decoder that processes the input character by character, groups consecutive repeats, and checks them against the expected repetition formula. once it decodes to a valid command like `cat flag.txt` it just executes it and returns the output. the whole "ball by ball" hint was referring to this character-by-character repetition encoding, not about sending multiple requests or anything like that.

couple things we learned - always pay attention to weird hints even if they seem like flavor text, character encoding schemes can be pretty creative in CTFs, and implementing the decode logic locally first to verify your encoding is super helpful before you start spamming the server. also the anti-debugging stuff was completely pointless since the actual challenge was server-side encoding, but i guess it makes the challenge look more intimidating.

---
Exploit4
