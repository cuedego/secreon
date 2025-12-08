# Installation & Setup Guide

**Version**: 1.0
**Date**: December 8, 2025

---

## Quick Install

### For macOS / Linux

```bash
# Clone repository
git clone https://github.com/cuedego/secreon.git
cd secreon

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install in development mode
python3 -m pip install -e .

# Verify
secreon slip39 --help
```

### For Windows

```powershell
# Clone repository
git clone https://github.com/cuedego/secreon.git
cd secreon

# Create virtual environment (optional but recommended)
python3 -m venv venv
venv\Scripts\activate

# Install in development mode
python3 -m pip install -e .

# Verify
secreon slip39 --help
```

### Using PyPI (when available)

```bash
pip install secreon
secreon slip39 --help
```

---

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, Windows
- **Dependencies**: None (only Python standard library)
- **Disk Space**: ~50 MB (including tests)
- **Memory**: 1 MB minimum (typical usage: <10 MB)

---

## Detailed Setup Instructions

### 1. Prerequisites

#### Install Python 3.8+

**macOS** (using Homebrew):
```bash
brew install python3
python3 --version  # Should show 3.8 or higher
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
python3 --version  # Should show 3.8 or higher
```

**Windows** (using Windows Package Manager):
```powershell
winget install Python.Python.3.11
python --version  # Should show 3.8 or higher
```

Or download from https://www.python.org/downloads/

#### Install Git

**macOS**:
```bash
brew install git
git --version
```

**Ubuntu/Debian**:
```bash
sudo apt-get install git
git --version
```

**Windows**:
Download from https://git-scm.com/download/win

### 2. Clone Repository

```bash
git clone https://github.com/cuedego/secreon.git
cd secreon
```

### 3. Create Virtual Environment (Recommended)

A virtual environment isolates Secreon dependencies from your system Python.

**macOS / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**:
```powershell
python3 -m venv venv
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```cmd
python3 -m venv venv
venv\Scripts\activate.bat
```

### 4. Install Secreon

```bash
# Install in development mode (allows importing slip39 as a module)
pip install -e .

# Or install in normal mode
pip install .
```

### 5. Verify Installation

```bash
# Check CLI is accessible
secreon slip39 --help

# Check Python module is importable
python3 -c "import slip39; print(f'SLIP-39 version: {slip39.__version__}')"

# Quick functionality test
secreon slip39 generate-seed --words 24
```

---

## Running Tests

### Run All Tests

```bash
# Full test suite (218 tests + 300 property-based examples)
python3 -m pytest tests/ -v

# Or faster summary
python3 -m pytest tests/ -q

# Expected output: "218 passed in ~25s"
```

### Run Specific Test Categories

```bash
# SLIP-39 official vectors only
python3 -m pytest tests/test_slip39_vectors.py -v

# Property-based tests only
python3 -m pytest tests/test_property_based.py -v

# GF(256) tests only
python3 -m pytest tests/test_gf256.py -v

# Cipher tests only
python3 -m pytest tests/test_cipher.py -v
```

### Test Coverage

```bash
# Run with coverage report
pip install coverage  # One-time install
coverage run -m pytest tests/ -q
coverage report  # Summary
coverage html    # Detailed HTML report (open htmlcov/index.html)
```

---

## Usage Examples

### Generate a New Seed

```bash
secreon slip39 generate-seed --words 24
# Output: anatomy branch academic acid badge badge balance balance beach beacon beacon bear beat beauty because become beef beer before begin behalf behind believe below belt bench
```

### Split Seed into SLIP-39 Shares

```bash
# 3-of-5 shares with passphrase
SEED="anatomy branch academic acid badge badge balance balance beach beacon beacon bear beat beauty because become beef beer before begin behalf behind believe below belt bench"

secreon slip39 generate \
  --bip39 "$SEED" \
  --group-threshold 1 \
  --groups "3,5" \
  --passphrase "MySecurePassphrase" \
  --output shares.txt
```

### Recover Seed from Shares

```bash
secreon slip39 recover \
  --input-file share-1.txt share-2.txt share-3.txt \
  --passphrase "MySecurePassphrase"
```

### Inspect Share Information

```bash
secreon slip39 info share-1.txt share-2.txt share-3.txt
```

### Validate Shares

```bash
secreon slip39 validate shares/*.txt
```

---

## Docker Setup (Optional)

If you prefer Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
RUN git clone https://github.com/cuedego/secreon.git .
RUN pip install -e .

ENTRYPOINT ["secreon"]
CMD ["slip39", "--help"]
```

Build and run:
```bash
docker build -t secreon .
docker run --rm secreon slip39 generate-seed --words 24
```

---

## Air-Gapped Setup (Recommended for Sensitive Secrets)

For maximum security, generate shares on an air-gapped (non-networked) machine:

### Prerequisites

- Dedicated USB drive or machine that can be disconnected from network
- Python 3.8+ installed on air-gapped machine

### Setup Steps

1. **Prepare USB drive** (from connected machine):
   ```bash
   # Clone secreon to USB
   git clone https://github.com/cuedego/secreon.git /mnt/usb/secreon
   ```

2. **Boot air-gapped machine** (disconnect network cable)

3. **Mount USB and install**:
   ```bash
   cd /mnt/usb/secreon
   python3 -m pip install -e . --user
   ```

4. **Generate shares**:
   ```bash
   secreon slip39 generate-seed --words 24
   secreon slip39 generate --bip39 "seed..." --groups "3,5" --passphrase "..."
   ```

5. **Store shares securely** (printed or on encrypted USB)

6. **Power off machine** (or wipe)

---

## Docker Container with Secreon

For isolated execution:

```bash
# Create container
docker run --rm -it python:3.11 bash

# Inside container:
pip install secreon
secreon slip39 generate-seed --words 24
secreon slip39 generate --bip39 "..." --groups "3,5"
```

---

## Development Setup

If you want to contribute to Secreon:

### Install Development Dependencies

```bash
# Install test dependencies
pip install pytest hypothesis

# Install code review tools (optional)
pip install pylint flake8 black
```

### Run Tests During Development

```bash
# Watch mode (re-run tests on file changes)
pip install pytest-watch
ptw tests/

# Or manual runs
pytest tests/ -v
pytest tests/ -v --tb=short  # Shorter tracebacks
pytest tests/ -k "test_cipher"  # Run specific tests
```

### Code Quality Checks

```bash
# Check style
flake8 src/slip39/*.py tests/*.py
pylint src/slip39/*.py

# Format code
black src/slip39/*.py tests/*.py

# Type hints (Python 3.10+)
python3 -m mypy src/slip39/ --strict
```

---

## Troubleshooting

### "command not found: secreon"

**Cause**: Secreon not installed or virtual environment not activated

**Solution**:
```bash
# If using virtual environment, activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Then install
pip install -e .

# Verify
which secreon  # Should show path
```

### "ModuleNotFoundError: No module named 'slip39'"

**Cause**: Module not installed or virtual environment not activated

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Install
pip install -e .

# Verify
python3 -c "import slip39"
```

### "pytest: command not found"

**Cause**: pytest not installed

**Solution**:
```bash
pip install pytest hypothesis
python3 -m pytest tests/ -v
```

### Tests fail with "Missing dependencies"

**Cause**: Optional dependencies not installed

**Solution**:
```bash
# Secreon has no required dependencies
# But pytest and hypothesis are needed for tests
pip install pytest hypothesis

# Then re-run
python3 -m pytest tests/
```

### "Permission denied" on macOS/Linux

**Cause**: Secreon script not executable

**Solution**:
```bash
chmod +x secreon.py
./secreon.py slip39 --help
```

---

## Uninstall

### From Virtual Environment

```bash
# Deactivate venv
deactivate

# Remove venv directory
rm -rf venv
```

### From System

```bash
pip uninstall secreon
```

---

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed command reference
- Review [Security Best Practices](USER_GUIDE.md#security-best-practices)
- Check [Deployment Guide](SECURITY_POLICY_DEPLOYMENT.md) for production deployment
- Run tests: `pytest tests/ -v`

---

**Questions?** See the FAQ in [USER_GUIDE.md](USER_GUIDE.md#faq) or create an issue on GitHub.

---

**Last Updated**: December 8, 2025
**Status**: Production Ready
