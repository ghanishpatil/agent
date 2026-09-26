# 🎯 JOYFUL MANDAZI CTF - COMPLETE SOLUTION

## Challenge URL
https://joyful-mandazi-1c2213.netlify.app

## 🚩 FLAG: `CTF{HELLO_HOW_ARE_YOU}`

---

## Complete Walkthrough

### Level 1: Character Selection
**Page**: `/` (index)
- **Task**: Click the correct cartoon character
- **Solution**: Click **Doraemon**
- **Clue Revealed**: Binary `01101101 01101111 01110010 01110011 01100101`
- **Decoded**: "morse"
- **Hidden**: Base64 `L3NlY3JldC9wYWdlMg==` → `/secret/page2`
- **Redirect**: `/page2.html`

### Level 2: Morse Code Mystery
**Page**: `/page2.html`
- **Morse Code**: `.--. .-.. . .- ... . / .... . .-.. .--`
- **Decoded**: "PLEASE HELP"
- **Hint**: "The answer is in the sound of silence..."
- **Next**: `/page3.html`

### Level 3: Binary Puzzle
**Page**: `/page3.html`
- **Binary**: `01001001 00100000 01100001 01101101 00100000 01100010 01101001 01101110 01100001 01110010 01111001`
- **Decoded**: "I am binary"
- **Hint**: "8-bit ASCII conversion needed"
- **Next**: `/page4.html`

### Level 4: Base64 Mystery
**Page**: `/page4.html`
- **Base64**: `VGhlIGZsYWcgaXMgaGlkZGVuIGluIHRoZSBzZXZlbnRoIHBhZ2UuIEZpbmQgdGhlIHBhdGggdG8gL2RvcmVtb24=`
- **Decoded**: "The flag is hidden in the seventh page. Find the path to /doremon"
- **Clue**: Go to page 7
- **Next**: `/page7.html`

### Level 5-6: (Intermediate pages)
**Pages**: `/page5.html`, `/page6.html`
- Transitional pages leading to final challenge

### Level 7: Final Challenge - Doraemon's Secret
**Page**: `/page7.html`
- **Task**: 
  1. Click on Doraemon
  2. Click all 5 magic tools:
     - 🚪 Anywhere Door
     - 🚁 Bamboo Copter
     - 🍞 Memory Bread
     - ⏰ Time Machine
     - 💡 Small Light
- **Result**: Flag is revealed!

---

## 🚩 THE FLAG

```
CTF{HELLO_HOW_ARE_YOU}
```

**Location**: Found in `/page7.html` source code and displayed after completing all tasks

---

## Key Findings

### Hidden Comments in page7.html:
```html
<!-- All previous levels completed! -->
<!-- Final flag: CTF{HELLO_HOW_ARE_YOU} -->
```

### JavaScript Variables:
```javascript
const flag = 'CTF{HELLO_HOW_ARE_YOU}';
```

### Flag Display:
```html
<div class="flag-code" id="flag">CTF{HELLO_HOW_ARE_YOU}</div>
```

---

## Solution Summary

1. **Level 1**: Click Doraemon → "morse"
2. **Level 2**: Morse code → "PLEASE HELP"
3. **Level 3**: Binary → "I am binary"
4. **Level 4**: Base64 → "Go to page 7"
5. **Level 7**: Click Doraemon + all 5 tools → **FLAG REVEALED**

---

## Anti-DevTools Bypass

The challenge has protections, but the flag can be found by:
1. Viewing page source (Ctrl+U before page loads)
2. Using curl/wget to download HTML
3. Searching for "CTF{" in the source code
4. Reading the JavaScript variables

---

## Tools Used

- Web browser / curl
- Binary decoder
- Morse code decoder
- Base64 decoder
- Source code analysis

---

## Completion Message

```
🎉 CONGRATULATIONS! 🎉
You've mastered all 6 levels!
🏆 CTF Challenge Complete 🏆
```

---

**Challenge Solved!** ✅
