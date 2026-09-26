# 🚀 START HERE - MD-EXPLOIT-ENGINE

Welcome to MD-EXPLOIT-ENGINE! This guide will get you started in minutes.

## What is MD-EXPLOIT-ENGINE?

A comprehensive, production-ready automated CTF challenge solver that can:
- 🎯 Automatically classify challenges into categories
- 🔓 Solve web, crypto, pwn, reversing, forensics, and OSINT challenges
- 🤖 Use machine learning for intelligent classification
- 🌐 Provide CLI, Web, and API interfaces
- 🐳 Deploy with Docker in seconds

## Quick Start (3 Steps)

### Step 1: Install

```bash
# Clone the repository
git clone https://github.com/yourusername/md-exploit-engine.git
cd md-exploit-engine

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config/config.example.yaml config/config.yaml
```

### Step 2: Run

```bash
# Solve a challenge
python main.py --challenge /path/to/challenge.zip

# Or start the web dashboard
python main.py --web --port 8080
```

### Step 3: Enjoy!

Open http://localhost:8080 and start solving challenges!

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[README.md](README.md)** - Full project overview
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Detailed installation
- **[docs/USAGE.md](docs/USAGE.md)** - Usage examples
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

## 🎯 What Can It Solve?

### Web Challenges
- SQL Injection
- XSS
- Command Injection
- LFI/RFI
- Path Traversal

### Crypto Challenges
- Base64 (nested)
- Caesar Cipher
- ROT13
- Hex Encoding
- XOR

### Binary Challenges
- Buffer Overflow
- Format String
- ret2win

### Forensics
- Steganography
- Metadata Analysis
- File Carving

### OSINT
- Web Search
- Wayback Machine
- Target Enumeration

### Reverse Engineering
- String Extraction
- Binary Analysis
- Static Analysis

## 💻 Usage Examples

### Command Line
```bash
# Auto-detect category
python main.py --challenge challenge.zip

# Specify category
python main.py --challenge challenge.zip --category web

# Verbose mode
python main.py --challenge challenge.zip --verbose
```

### Python API
```python
from core.engine import ExploitEngine
from core.config import Config

config = Config('config/config.yaml')
engine = ExploitEngine(config)

result = engine.solve_challenge('challenge.zip')
if result.success:
    print(f"Flag: {result.flag}")
```

### Web Dashboard
```bash
python main.py --web --port 8080
# Open http://localhost:8080
```

### REST API
```bash
# Start API server
python main.py --api --port 5000

# Make request
curl -X POST http://localhost:5000/solve \
  -H "Content-Type: application/json" \
  -d '{"name": "challenge", "category": "web"}'
```

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_engine.py
```

## 📁 Project Structure

```
md-exploit-engine/
├── main.py              # Entry point
├── core/                # Core engine
├── modules/             # Solver modules
├── api/                 # REST API
├── web/                 # Web dashboard
├── ml/                  # Machine learning
├── utils/               # Utilities
├── tests/               # Test suite
├── docs/                # Documentation
├── examples/            # Usage examples
└── config/              # Configuration
```

## 🎓 Learning Path

1. **Beginner**: Start with [QUICKSTART.md](QUICKSTART.md)
2. **User**: Read [docs/USAGE.md](docs/USAGE.md)
3. **Developer**: Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **Contributor**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## 🔧 Configuration

Edit `config/config.yaml`:

```yaml
general:
  threads: 4        # Number of worker threads
  timeout: 300      # Timeout per challenge (seconds)

modules:
  web:
    enabled: true   # Enable/disable modules
  crypto:
    enabled: true
```

## 🆘 Need Help?

- 📖 Check [docs/](docs/) for detailed documentation
- 💡 See [examples/](examples/) for code examples
- 🐛 Report issues on GitHub
- 💬 Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## ⚡ Quick Commands

```bash
# Show help
python main.py --help

# Solve challenge
python main.py --challenge challenge.zip

# Web dashboard
python main.py --web

# API server
python main.py --api

# Run tests
pytest

# Setup
python scripts/setup.py
```

## 🌟 Features

- ✅ 6 solver modules (Web, Crypto, Pwn, Rev, Forensics, OSINT)
- ✅ ML-based classification
- ✅ Multi-threaded execution
- ✅ CLI, Web, and API interfaces
- ✅ Docker support
- ✅ Comprehensive logging
- ✅ Extensive documentation
- ✅ Test suite included

## ⚠️ Important

This tool is for **educational purposes** and **authorized CTF competitions only**.
Always ensure you have proper authorization before using this tool.

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## Next Steps

1. ✅ Read [QUICKSTART.md](QUICKSTART.md)
2. ✅ Try the examples in [examples/](examples/)
3. ✅ Explore the [docs/](docs/) directory
4. ✅ Start solving challenges!

**Happy Hacking! 🎉**

---

**MD-EXPLOIT-ENGINE v1.0.0**
Built with ❤️ for the CTF community
