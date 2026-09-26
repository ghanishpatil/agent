# The Forgotten Sequence - Writeup

**Challenge:** The Forgotten Sequence  
**Category:** Web (Easy)  
**Flag:** `Kaal{3AST3RFL@9}`

## Description
"In the cycle of time, patterns repeat - but only the observant recognize them. A hidden ritual lies embedded within the realm. Invoke it correctly, and the system shall respond."

**URL:** https://kaalchakractf.com/

## Solution

### Step 1: Website Reconnaissance
Visited the CTF website and inspected the page source. Found an external JavaScript file referenced:

```html
<script src="script.js"></script>
```

Downloaded and analyzed the JavaScript file.

### Step 2: Analyzing script.js
The JavaScript file contained several interesting elements:

**Fake flag in comment:**
```javascript
//{faK3_flag} oopsiee.....
```

**Console hint:**
```javascript
console.log('Looking for flags? Try the Konami Code...');
```

**Konami Code listener:**
```javascript
const contra = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
                'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
                'b', 'a'];
```

**Flag reveal function:**
```javascript
function activateConfetti() {
    // Displays popup with button containing: {3AST3RFL@9}
}
```

### Step 3: Executing the Konami Code
The "hidden ritual" mentioned in the description is the classic **Konami Code** - a famous cheat code from gaming history.

On the website, I entered the sequence using keyboard:
```
↑ ↑ ↓ ↓ ← → ← → B A
```

This triggered the `initConfetti()` function, which activated confetti animation and displayed a popup containing the flag.

### Step 4: Extracting the Flag
The popup revealed the flag text: `{3AST3RFL@9}`

Combined with the flag format: `Kaal{3AST3RFL@9}`

## Flag
`Kaal{3AST3RFL@9}`
