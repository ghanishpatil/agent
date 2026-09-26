# CTF Solver MCP - Usage Guide

## Quick Start

### 1. Installation

```bash
cd ctf_solver_mcp
pip install -e .
```

### 2. Configure in Kiro

Add to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "ctf-solver": {
      "command": "python",
      "args": ["C:/path/to/ctf_solver_mcp/server.py"],
      "env": {},
      "disabled": false,
      "autoApprove": ["solve_ctf_challenge", "analyze_challenge", "decode_cipher"]
    }
  }
}
```

### 3. Use in Kiro

```
Hey Kiro, use the ctf-solver to solve this challenge: https://example-ctf.com
```

## Detailed Examples

### Example 1: Solve Complete Challenge

```
Use ctf-solver to solve: https://thriving-meringue-85c152.netlify.app
```

**What it does:**
1. Fetches the page
2. Extracts all fragments (text, JS, comments, etc.)
3. Finds flags in source code
4. Decodes base64/hex data
5. Returns all flags found

**Expected Output:**
```json
{
  "success": true,
  "flags_found": ["FLAG{LOVE}"],
  "fragments_analyzed": 7,
  "fragments_solved": 4
}
```

### Example 2: Analyze Only (No Solving)

```
Use ctf-solver to analyze: https://joyful-mandazi-1c2213.netlify.app
```

**What it does:**
- Breaks challenge into fragments
- Prioritizes each fragment
- Returns structure without solving

**Use case:** When you want to understand the challenge structure first

### Example 3: Decode Cipher

```
Use ctf-solver to decode: "VGhlIGZsYWcgaXMgaGlkZGVu"
```

**What it does:**
- Tries multiple decoding methods
- Returns all successful decodings

**Output:**
```json
{
  "decoded": [
    {"type": "base64", "result": "The flag is hidden"}
  ]
}
```

### Example 4: Extract Hidden Data

```
Use ctf-solver to extract hidden data from: https://example.com/image.png
```

**What it does:**
- Downloads the file
- Checks metadata
- Looks for steganography
- Extracts strings

## Advanced Usage

### Custom Wordlist for Brute Force

```
Use ctf-solver to brute force https://example.com/login with wordlist:
["password123", "admin", "CTF{test}"]
```

### Pattern-Based Password Generation

```
Use ctf-solver to brute force with pattern: "CTF{*****}"
```

This generates all 5-character combinations in CTF{} format.

## Fragment Types Explained

### 1. Visible Text (Priority: High)
- All text content on the page
- Useful for finding hints, instructions

### 2. Flags Found (Priority: Critical)
- Direct flag patterns: CTF{...}, FLAG{...}
- Immediately returns if found

### 3. JavaScript (Priority: High)
- Analyzes all JS code
- Looks for: keys, passwords, API endpoints
- Checks for obfuscation

### 4. Forms & Inputs (Priority: Medium)
- Hidden form fields
- Input validation patterns
- Submit endpoints

### 5. HTML Comments (Priority: High)
- Developer comments
- Often contain hints or TODOs
- May have disabled features

### 6. Base64 Data (Priority: High)
- Automatically decodes
- Checks if result is meaningful
- May contain flags or keys

### 7. Response Headers (Priority: Low)
- Custom headers
- May contain hints (X-Flag, X-Hint, etc.)

## Tips for Best Results

### 1. Let It Analyze First
```
Analyze this challenge first: [URL]
```
Then review fragments before solving.

### 2. Combine with Manual Analysis
```
The ctf-solver found these fragments. Let me check fragment #3 (JavaScript) manually.
```

### 3. Use for Multi-Stage Challenges
```
1. Solve stage 1: [URL]
2. Use the key from stage 1 to solve stage 2
```

### 4. Save Solutions to Brain
```
After solving, save this to CTF_BRAIN.md for future reference
```

## Common Patterns Recognized

### Web Challenges
- Hidden API endpoints
- JavaScript obfuscation
- Cookie/session manipulation
- SQL injection points

### Crypto Challenges
- Base64, Hex, ROT13
- Caesar cipher
- XOR encryption
- Hash identification

### Steganography
- LSB extraction
- Metadata analysis
- File signature detection
- Hidden text layers

### Password Cracking
- Common wordlists
- Pattern generation
- Hash cracking
- Brute force optimization

## Troubleshooting

### "No flags found"
- Challenge may require interaction
- Try analyzing fragments manually
- Check if JavaScript needs execution

### "Connection timeout"
- Challenge site may be down
- Try with longer timeout
- Check if VPN/proxy needed

### "Decoding failed"
- Cipher may be custom
- Try manual analysis
- Check for multi-layer encoding

## Integration with Other Tools

### With Hashcat
```
1. Use ctf-solver to extract hash
2. Save hash to file
3. Run hashcat on the hash
```

### With Burp Suite
```
1. Use ctf-solver to find API endpoints
2. Test endpoints in Burp
3. Use solver for response analysis
```

### With Steganography Tools
```
1. Use ctf-solver to identify stego
2. Download file
3. Use specialized tools (steghide, stegsolve)
```

## Performance Tips

1. **Auto-approve common tools** in mcp.json
2. **Use analyze first** for complex challenges
3. **Cache results** for repeated analysis
4. **Parallel fragment solving** (automatic)

## Security Notes

- Server runs locally (no data sent externally)
- Respects robots.txt
- Rate limiting on requests
- No persistent storage of sensitive data

## Future Features

Coming soon:
- [ ] Machine learning for pattern recognition
- [ ] Integration with CTFd platforms
- [ ] Automated report generation
- [ ] Team collaboration features
- [ ] Challenge difficulty estimation

## Support

For help:
1. Check this guide
2. Review README.md
3. Check example challenges in tests/
4. Open an issue on GitHub

Happy CTF solving! 🚩
