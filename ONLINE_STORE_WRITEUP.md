Online Store Challenge - Writeup by Team Exploit4

Challenge: An online store hides more than just products
Category: Web
Difficulty: Medium
Points: 300
Author: ronin26th

When I opened the challenge URL at http://138.199.163.92:3000/, I saw a simple online store page with the title "WELCOME TO MY STORE" and a search box. The page looked pretty basic - just a header, an image, and a form with a text input labeled "Search items" and a submit button.

I opened the browser's DevTools to check the page source. Right away I noticed something interesting in the HTML - there were two hidden paragraphs at the bottom. One said "?file=" and the other contained what looked like base64: "Rm9sbG93IHRoZSByb290cyE=". I decoded this and got "Follow the roots!" which seemed like a hint.

Looking at the form, I saw it was sending a GET request to index.php with a parameter called "file". This immediately made me think of Local File Inclusion (LFI) vulnerabilities. The parameter name "file" is a classic indicator that the application might be including files based on user input.

I tested the LFI by trying to read /etc/passwd:
http://138.199.163.92:3000/index.php?file=/etc/passwd

It worked! I got the contents of the passwd file, confirming the LFI vulnerability. But I needed to find the flag, and the hint said "Follow the roots!" which suggested looking in the /root directory. When I tried /root/flag, I got a permission denied error, so I couldn't directly read it.

Since I had LFI, I decided to read the source code of index.php itself to understand how the application works. I used a PHP filter wrapper to get the base64-encoded source:
http://138.199.163.92:3000/index.php?file=php://filter/convert.base64-encode/resource=index.php

After decoding the base64, I found the complete PHP source code. This is where things got interesting. The code had an Admin class and was checking for a cookie called "winter_is_coming". Here's what the vulnerable code was doing:

1. It takes the cookie value, base64 decodes it, and unserializes it
2. After unserializing, it sets $unout->my_secret = $FLAG
3. Then it checks: if $unout->is_admin == 0 AND $unout->your_secret === $unout->my_secret, show the flag

The key vulnerability here is PHP Object Injection combined with a logic flaw. The code sets my_secret to the FLAG after deserialization, then checks if your_secret equals my_secret. At first this seems impossible - how can your_secret equal my_secret if we don't know the flag value?

The trick is to use PHP's reference feature in serialization. In PHP, you can make one property reference another using the R:N syntax in serialized data. If I make your_secret a reference to my_secret, then when the code sets my_secret = FLAG, your_secret will automatically also be FLAG because they point to the same memory location.

I crafted a serialized Admin object:
O:5:"Admin":3:{s:8:"is_admin";i:0;s:9:"my_secret";s:4:"test";s:11:"your_secret";R:3;}

Breaking this down:
- O:5:"Admin":3 - Object of class Admin with 3 properties
- s:8:"is_admin";i:0 - is_admin = 0 (integer)
- s:9:"my_secret";s:4:"test" - my_secret = "test" (will be overwritten with FLAG)
- s:11:"your_secret";R:3 - your_secret is a Reference to element 3 (which is my_secret's value)

The R:3 is the magic part. It tells PHP that your_secret should reference the same memory location as my_secret. So when the code later does $unout->my_secret = $FLAG, both my_secret and your_secret become FLAG.

I base64 encoded this payload and set it as the winter_is_coming cookie:

import requests
import base64

payload = 'O:5:"Admin":3:{s:8:"is_admin";i:0;s:9:"my_secret";s:4:"test";s:11:"your_secret";R:3;}'
encoded = base64.b64encode(payload.encode()).decode()

cookies = {'winter_is_coming': encoded}
r = requests.get('http://138.199.163.92:3000/', cookies=cookies)

When I sent this request, the page displayed a congratulations message with the flag in a code block. The condition was satisfied because your_secret and my_secret were now both pointing to the FLAG value, making them equal.

Flag: Kaal{d33pdA8k5eC83ts}

Team Exploit4
