# Secreon

Fault-tolerant secret sharing using Shamir's Secret Sharing with full SLIP-39 support for cryptocurrency wallets. It´s a compact implementation built for those rare individuals who believe their 24-word seed deserves the same threat modeling as state secrets. No external dependencies, no magic, just deterministic cryptography and the quiet fear of irreversible loss.

## Overview

Secreon provides two complementary secret sharing implementations:

1. **Classic SSS**: General-purpose Shamir's Secret Sharing for any secret
2. **SLIP-39**: Cryptocurrency-focused implementation with BIP-39 compatibility and Trezor compatibility

## Features

### Classic SSS

- **Generate shares** from any secret (string or file)
- **Recover secret** from shares
- **JSON format** for share storage
- **KDF support** (SHA-256, PBKDF2)
- **Configurable threshold** and share count

### SLIP-39 (Cryptocurrency Wallets)

- **BIP-39 compatible** - works with standard wallet seeds
- **Two-level secret sharing** - groups with member thresholds
- **Passphrase encryption** - additional security layer
- **Trezor compatible** - interoperable with Trezor hardware wallets
- **Checksum validation** - RS1024 error detection
- **Complete CLI** - generate, recover, validate, and inspect shares

## Quick Start

### SLIP-39 for Cryptocurrency Wallets

```bash
# Generate a new BIP-39 seed
python3 secreon.py slip39 generate-seed --words 24

# Split into SLIP-39 shares (3-of-5)
python3 secreon.py slip39 generate \
    --bip39 "your 24 word seed phrase here" \
    --groups "3,5" \
    --passphrase "YourPassword" \
    --split-shares \
    --out-dir ./shares

# Recover secret from shares
python3 secreon.py slip39 recover \
    --shares share-1.json share-2.json share-3.json \
    --passphrase "YourPassword"

# Validate shares
python3 secreon.py slip39 validate -f ./shares/*.json

# Get share information
python3 secreon.py slip39 info --file share-1.json
```

See [SLIP-39 CLI Documentation](docs/SLIP39_CLI.md) for complete details.

## Installation

No dependencies required beyond Python 3.6+. Clone and run:

```bash
git clone https://github.com/cuedego/secreon.git
cd secreon
python3 secreon.py --help
```

## Usage

### SLIP-39 Commands

See [SLIP-39 CLI Documentation](docs/SLIP39_CLI.md) for complete details.

```bash
# Generate BIP-39 seed
python3 secreon.py slip39 generate-seed --words 24

# Generate SLIP-39 shares
python3 secreon.py slip39 generate --bip39 "..." --groups "3,5" --passphrase "..."

# Recover secret
python3 secreon.py slip39 recover --shares share1.json share2.json share3.json -p "..."

# Validate shares
python3 secreon.py slip39 validate -f share1.json share2.json

# Display share info
python3 secreon.py slip39 info "lizard lily acrobat..."
```

### Classic SSS Commands

```bash
# Generate 5 shares with threshold of 3 from a string secret
python3 secreon.py generate --secret 'my secret message' --minimum 3 --shares 5 --out shares.json

# Generate shares from a file (BIP39 seed, keys, etc.)
python3 secreon.py generate --secret-file seed.txt --out shares.json

# Generate shares using PBKDF2 for passphrase (recommended for passphrases)
python3 secreon.py generate --secret 'my passphrase' --kdf pbkdf2:200000 --out shares.json

# Generate shares using SHA-256 (fast but less secure for passphrases)
python3 secreon.py generate --secret 'my passphrase' --kdf sha256 --out shares.json

# Generate individual share files (safer for distribution)
python3 secreon.py generate --secret 'my secret' --out share.json --split-shares
# This creates: share-1.json, share-2.json, share-3.json, etc.

```

### Recover secret from shares

```bash
# Recover secret from JSON file (outputs integer by default)
python3 secreon.py recover --shares-file shares.json

# Attempt to decode recovered secret as UTF-8 string
python3 secreon.py recover --shares-file shares.json --as-str

# Recover from stdin
cat shares.json | python3 secreon.py recover

# Write recovered secret to file
python3 secreon.py recover --shares-file shares.json --as-str --out recovered.txt

# Recover from multiple individual share files
python3 secreon.py recover --shares-file share-1.json share-3.json share-5.json --as-str

# Recover from a directory containing share files
python3 secreon.py recover --shares-dir /path/to/shares/ --as-str

```

## Configuration

Default parameters can be set in `config/default.json` (optional):

```json
{
  "minimum": 3,
  "shares": 5,
  "prime": null
}

```

**Note:** Secrets must NEVER be stored in config files. They must be provided via CLI (`--secret` or `--secret-file`).

## Security Considerations

**Passphrases**: If using passphrases, always use `--kdf pbkdf2:N` (N >= 100000 iterations) to slow down brute-force attacks. SHA-256 does not protect weak passphrases.

**Random secrets**: For high-security applications, use a cryptographically random secret rather than a passphrase.

**Share storage**: Protect share files with appropriate file permissions. Consider distributing shares to different locations.

**File permissions while editing**: When creating or splitting share files, temporarily restrict permissions to avoid accidental exposure (example: `chmod 600 share-*.json`).

**Split shares**: Use `--split-shares` to generate individual files for each share. This eliminates the risk of data corruption during manual file splitting and makes distribution safer.

**Threshold**: Choose a threshold that balances security (higher threshold = more shares needed) and fault tolerance (lower threshold = more resilient to share loss).

## Examples

### Example 1: Split and recover a text secret

```bash
# Generate shares
python3 secreon.py generate --secret "The treasure is buried under the old oak tree" --out shares.json

# Recover (any 3 of 5 shares by default)
python3 secreon.py recover --shares-file shares.json --as-str

```

### Example 2: Protect a BIP39 seed phrase

```bash
# Create shares from a seed file
python3 secreon.py generate --secret-file examples/sample-seed.txt --minimum 5 --shares 10 --out seed-shares.json

# Later, recover the seed
python3 secreon.py recover --shares-file seed-shares.json --as-str

```

### Example 3: Use PBKDF2 for passphrase-based secrets

```bash
# Generate with strong KDF
python3 secreon.py generate --secret 'MyStrongPassphrase123!' --kdf pbkdf2:200000 --out shares.json

# The salt and iterations are stored in shares.json metadata
# Recovery works the same way
python3 secreon.py recover --shares-file shares.json --as-str

```

### Example 4: Split shares for safe distribution

```bash
# Generate individual share files
python3 secreon.py generate --secret "Critical data" --minimum 3 --shares 5 --out myshare.json --split-shares
# Creates: myshare-1.json, myshare-2.json, myshare-3.json, myshare-4.json, myshare-5.json

# Distribute shares to different locations
# Each file is self-contained with all necessary metadata

# Later, recover from any 3 shares
python3 secreon.py recover --shares-file myshare-1.json myshare-2.json myshare-5.json --as-str

# Or recover from a directory
python3 secreon.py recover --shares-dir ./shares/ --as-str

```

## How It Works

Shamir's Secret Sharing uses polynomial interpolation over a finite field. A secret is encoded as the y-intercept of a random polynomial of degree `k-1` (where `k` is the threshold). Each share is a point `(x, y)` on this polynomial. Any `k` points can reconstruct the polynomial and recover the secret.

## License

This project is dedicated to the public domain under the CC0 1.0 Universal (CC0-1.0) waiver. See the `LICENSE` file for the full text.
