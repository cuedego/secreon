# Vaultix

Fault-tolerant secret storage using Shamir's Secret Sharing.

## Overview

Vaultix implements Shamir's Secret Sharing scheme, allowing you to split a secret into multiple shares where any threshold number of shares can reconstruct the original secret. This provides fault tolerance and security for sensitive data.

## Features

- **Generate shares** from a secret (string or file)
- **Recover secret** from shares
- **JSON format** for share storage (default)
- **KDF support** for passphrases (SHA-256, PBKDF2)
- **Configurable threshold** and share count
- **Safe defaults** (secrets never stored in config)

## Installation

No dependencies required beyond Python 3.6+. Clone and run:

```bash
git clone https://github.com/cuedego/vaultix.git
cd vaultix
python3 vaultix.py --help
```

Or use directly:
```bash
python3 src/sss.py --help
```

## Usage

### Generate shares from a secret

```bash
# Generate 5 shares with threshold of 3 from a string secret
python3 vaultix.py generate --secret 'my secret message' --minimum 3 --shares 5 --out shares.json

# Generate shares from a file (BIP39 seed, keys, etc.)
python3 vaultix.py generate --secret-file seed.txt --out shares.json

# Generate shares using PBKDF2 for passphrase (recommended for passphrases)
python3 vaultix.py generate --secret 'my passphrase' --kdf pbkdf2:200000 --out shares.json

# Generate shares using SHA-256 (fast but less secure for passphrases)
python3 vaultix.py generate --secret 'my passphrase' --kdf sha256 --out shares.json
```

### Recover secret from shares

```bash
# Recover secret from JSON file (outputs integer by default)
python3 vaultix.py recover --shares-file shares.json

# Attempt to decode recovered secret as UTF-8 string
python3 vaultix.py recover --shares-file shares.json --as-str

# Recover from stdin
cat shares.json | python3 vaultix.py recover

# Write recovered secret to file
python3 vaultix.py recover --shares-file shares.json --as-str --out recovered.txt
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

- **Passphrases**: If using passphrases, always use `--kdf pbkdf2:N` (N >= 100000 iterations) to slow down brute-force attacks. SHA-256 does not protect weak passphrases.
- **Random secrets**: For high-security applications, use a cryptographically random secret rather than a passphrase.
- **Share storage**: Protect share files with appropriate file permissions. Consider distributing shares to different locations.
- **Threshold**: Choose a threshold that balances security (higher threshold = more shares needed) and fault tolerance (lower threshold = more resilient to share loss).

## Examples

### Example 1: Split and recover a text secret

```bash
# Generate shares
python3 vaultix.py generate --secret "The treasure is buried under the old oak tree" --out shares.json

# Recover (any 3 of 5 shares by default)
python3 vaultix.py recover --shares-file shares.json --as-str
```

### Example 2: Protect a BIP39 seed phrase

```bash
# Create shares from a seed file
python3 vaultix.py generate --secret-file examples/sample-seed.txt --minimum 5 --shares 10 --out seed-shares.json

# Later, recover the seed
python3 vaultix.py recover --shares-file seed-shares.json --as-str
```

### Example 3: Use PBKDF2 for passphrase-based secrets

```bash
# Generate with strong KDF
python3 vaultix.py generate --secret 'MyStrongPassphrase123!' --kdf pbkdf2:200000 --out shares.json

# The salt and iterations are stored in shares.json metadata
# Recovery works the same way
python3 vaultix.py recover --shares-file shares.json --as-str
```

## How It Works

Shamir's Secret Sharing uses polynomial interpolation over a finite field. A secret is encoded as the y-intercept of a random polynomial of degree `k-1` (where `k` is the threshold). Each share is a point `(x, y)` on this polynomial. Any `k` points can reconstruct the polynomial and recover the secret.

## License

This implementation is released into the Public Domain under CC0 and OWFa licenses.
