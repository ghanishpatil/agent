# Cartoon Network CTF - Complete Solution

## Challenge Analysis

### Level 1: Character Selection

**Clues Found:**
1. **Click Sequence**: Must click "doraemon" first
2. **Next Clue**: "01101101 01101111 01110010 01110011 01100101" (binary)
3. **Hidden Comment**: `base64_decode("L3NlY3JldC9wYWdlMg==")`
4. **Redirect**: Goes to `/page2.html` after clicking doraemon

### Decoding the Clues

#### 1. Binary to Text
```
01101101 = m
01101111 = o
01110010 = r
01110011 = s
01100101 = e
```
**Result**: "morse"

#### 2. Base64 Decode
```
L3NlY3JldC9wYWdlMg== → /secret/page2
```

### Solution Path

**Level 1 Steps:**
1. Click on Doraemon character
2. Level 1 complete message appears
3. Binary clue revealed: "morse"
4. Automatically redirects to `/page2.html`

**Alternative Path:**
- Hidden URL: `/secret/page2` (from base64 comment)

### Anti-DevTools Protection

The page has several protections:
- Debugger detection (timing-based)
- Console opening detection
- Right-click disabled
- F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U blocked
- Console.log disabled

**Bypass**: These can be bypassed by:
- Viewing page source (Ctrl+U before page loads)
- Using browser's "View Source" option
- Saving HTML locally and analyzing
- Using curl/wget to download

## Flag Format

Expected: `BPCTF{...}` based on previous challenges

## Next Steps

1. Navigate to `/page2.html` or `/secret/page2`
2. Look for morse code challenge (based on binary clue)
3. Continue solving subsequent levels

---

## Quick Solution

**Level 1**: Click Doraemon → Get "morse" clue → Redirect to page2.html
