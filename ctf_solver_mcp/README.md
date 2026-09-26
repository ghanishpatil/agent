# CTF Solver MCP Server

An MCP (Model Context Protocol) server that automatically solves CTF challenges by fragmenting them into smaller, solvable parts.

## Features

- **Automatic Challenge Analysis**: Breaks down CTF challenges into manageable fragments
- **Multi-Fragment Solving**: Solves each fragment independently and combines results
- **Pattern Recognition**: Identifies common CTF patterns (flags, base64, hidden data, etc.)
- **Cipher Decoding**: Supports multiple cipher types (base64, hex, morse, ROT13, etc.)
- **Steganography Detection**: Identifies hidden data in images and files
- **Brute Force Capabilities**: Password cracking with wordlists and patterns

## Installation

```bash
cd ctf_solver_mcp
pip install -e .
```

## Usage

### As an MCP Server

Add to your MCP settings (e.g., Kiro's `mcp.json`):

```json
{
  "mcpServers": {
    "ctf-solver": {
      "command": "python",
      "args": ["/path/to/ctf_solver_mcp/server.py"],
      "env": {}
    }
  }
}
```

### Available Tools

1. **solve_ctf_challenge**
   - Automatically solves a complete CTF challenge
   - Input: `url` (string)
   - Returns: Flags, solutions, and analysis

2. **analyze_challenge**
   - Analyzes and fragments a challenge without solving
   - Input: `url` (string)
   - Returns: Challenge fragments with priorities

3. **decode_cipher**
   - Decodes common ciphers
   - Input: `cipher_text` (string), `cipher_type` (optional)
   - Returns: Decoded text

4. **extract_hidden_data**
   - Extracts hidden data from files
   - Input: `file_url` (string), `extraction_type` (optional)
   - Returns: Hidden data found

5. **brute_force_password**
   - Brute forces passwords
   - Input: `target` (string), `wordlist` (optional), `pattern` (optional)
   - Returns: Cracked password

## How It Works

### 1. Challenge Fragmentation

The solver breaks challenges into these fragments:

- **Visible Text**: All readable content
- **Flags**: Direct flag patterns (CTF{...}, FLAG{...})
- **JavaScript**: Code analysis for keys/passwords
- **Forms & Inputs**: Hidden form data
- **HTML Comments**: Developer comments with hints
- **Base64 Data**: Encoded strings
- **Response Headers**: HTTP headers with clues

### 2. Fragment Solving

Each fragment is solved independently:

- **Priority-based**: Critical fragments (flags) solved first
- **Pattern Matching**: Recognizes common CTF patterns
- **Decoder Chain**: Tries multiple decoding methods
- **Context Aware**: Uses hints from other fragments

### 3. Solution Compilation

Results are combined to produce:

- All flags found
- Decryption keys
- Hidden endpoints
- Complete solution path

## Example Usage

```python
# In your MCP client (e.g., Kiro)
result = await mcp.call_tool("solve_ctf_challenge", {
    "url": "https://example-ctf.com/challenge"
})

# Result:
{
    "success": true,
    "flags_found": ["CTF{example_flag}"],
    "fragments_analyzed": 7,
    "fragments_solved": 4,
    "solutions": [...]
}
```

## Supported Challenge Types

- Web-based CTF challenges
- Steganography challenges
- Cryptography challenges
- Password cracking
- Source code analysis
- API endpoint discovery
- Hidden data extraction

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black ctf_solver_mcp/
```

### Type Checking

```bash
mypy ctf_solver_mcp/
```

## Roadmap

- [ ] Advanced steganography tools (LSB extraction, etc.)
- [ ] Machine learning for pattern recognition
- [ ] Multi-stage challenge support
- [ ] Automated exploit generation
- [ ] Integration with common CTF tools (john, hashcat, etc.)
- [ ] Challenge database and learning from past solves
- [ ] Real-time collaboration features

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- [MCP (Model Context Protocol)](https://github.com/anthropics/mcp)
- BeautifulSoup for HTML parsing
- Requests for HTTP operations

## Support

For issues or questions, please open an issue on GitHub.
