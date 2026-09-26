# Quick Start Guide

Get MD-EXPLOIT-ENGINE up and running in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/md-exploit-engine.git
cd md-exploit-engine

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config/config.example.yaml config/config.yaml
```

## Basic Usage

### 1. Solve a Challenge (CLI)

```bash
python main.py --challenge /path/to/challenge.zip
```

### 2. Start Web Dashboard

```bash
python main.py --web --port 8080
```

Then open http://localhost:8080 in your browser.

### 3. Use as Python Library

```python
from core.engine import ExploitEngine
from core.config import Config

config = Config('config/config.yaml')
engine = ExploitEngine(config)

result = engine.solve_challenge('challenge.zip')
print(f"Flag: {result.flag}")
```

## Examples

### Crypto Challenge

```bash
# Auto-detect and solve
python main.py --challenge encrypted.txt

# Force category
python main.py --challenge encrypted.txt --category crypto
```

### Web Challenge

```bash
python main.py --challenge web_challenge --category web
```

### Binary Challenge

```bash
python main.py --challenge binary.elf --category pwn
```

## Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
general:
  threads: 4
  timeout: 300

modules:
  web:
    enabled: true
  crypto:
    enabled: true
  pwn:
    enabled: true
```

## Testing

```bash
# Run tests
pytest

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_engine.py
```

## Common Commands

```bash
# Show help
python main.py --help

# Verbose mode
python main.py --challenge challenge.zip --verbose

# Debug mode
python main.py --challenge challenge.zip --debug

# Custom timeout
python main.py --challenge challenge.zip --timeout 600

# Multiple threads
python main.py --challenge challenges/ --threads 8
```

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### Permission Errors
```bash
chmod +x main.py
chmod +x scripts/*.sh
```

### Configuration Issues
```bash
# Reset to default config
cp config/config.example.yaml config/config.yaml
```

## Next Steps

- Read [USAGE.md](docs/USAGE.md) for detailed usage
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- See [examples/](examples/) for code examples
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Support

- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)
- Issues: GitHub Issues
- Tests: [tests/](tests/)

Happy hacking! 🚀
