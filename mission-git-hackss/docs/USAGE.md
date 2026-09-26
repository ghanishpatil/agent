# Usage Guide

## Command Line Interface

### Basic Usage

Solve a challenge:

```bash
python main.py --challenge /path/to/challenge.zip
```

Specify category:

```bash
python main.py --challenge challenge.zip --category web
```

### Web Dashboard

Start the web dashboard:

```bash
python main.py --web --port 8080
```

Then open http://localhost:8080 in your browser.

### API Server

Start the API server:

```bash
python main.py --api --host 0.0.0.0 --port 5000
```

## Configuration

Edit `config/config.yaml` to customize:

- Module settings
- Timeout values
- API keys for external services
- Flag patterns
- CTF platform integration

## Module-Specific Usage

### Web Exploitation

```python
from modules.web import WebModule
from core.challenge import Challenge

challenge = Challenge(
    name="web_challenge",
    url="http://target.com",
    category="web"
)

module = WebModule(config)
result = module.solve(challenge)
```

### Cryptography

```python
from modules.crypto import CryptoModule

challenge = Challenge(
    name="crypto_challenge",
    files=[Path("encrypted.txt")],
    category="crypto"
)

module = CryptoModule(config)
result = module.solve(challenge)
```

### Binary Exploitation

```python
from modules.pwn import PwnModule

challenge = Challenge(
    name="pwn_challenge",
    files=[Path("binary")],
    host="target.com",
    port=1337,
    category="pwn"
)

module = PwnModule(config)
result = module.solve(challenge)
```

## API Usage

### Solve Challenge via API

```bash
curl -X POST http://localhost:5000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "name": "challenge1",
    "category": "web",
    "url": "http://target.com"
  }'
```

Response:

```json
{
  "success": true,
  "flag": "flag{example}",
  "method": "_check_source_code",
  "duration": 2.5
}
```

## Advanced Features

### Multi-threaded Solving

```bash
python main.py --challenge challenges/ --threads 8
```

### Custom Timeout

```bash
python main.py --challenge challenge.zip --timeout 600
```

### Verbose Logging

```bash
python main.py --challenge challenge.zip --verbose
```

### Debug Mode

```bash
python main.py --challenge challenge.zip --debug
```

## Examples

### Example 1: Web Challenge

```bash
python main.py --challenge web_challenge --category web
```

### Example 2: Crypto Challenge

```bash
python main.py --challenge encrypted.txt --category crypto
```

### Example 3: Binary Challenge

```bash
python main.py --challenge binary.elf --category pwn
```

## Tips

1. Always start with auto-detection if unsure of category
2. Use verbose mode to see what techniques are being tried
3. Check logs in `logs/` directory for detailed information
4. Use the web dashboard for easier interaction
5. Configure API keys for external services in config.yaml
