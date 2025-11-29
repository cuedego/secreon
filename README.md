# Secreon

Fault-tolerant secret storage using Shamir's Secret Sharing.

## Overview

Secreon implements Shamir's Secret Sharing scheme, allowing you to split a secret into multiple shares where any threshold number of shares can reconstruct the original secret. This provides fault tolerance and security for sensitive data.

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
git clone https://github.com/cuedego/secreon.git
cd secreon
python3 secreon.py --help

```

Or use directly:

```bash
python3 src/sss.py --help

```

## Usage

### Generate shares from a secret

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

## Migration / Converting combined share files

If you have an existing combined shares file (the legacy default format) and
want to split it into individual share files for distribution, you can do so
with a small script or one-liner. Example (Python one-liner):

```bash
python3 - <<'PY'
import json,sys,os
f = '/path/to/shares.json'
out_prefix = 'share'
os.makedirs('split-out', exist_ok=True)
data = json.load(open(f))
meta = data.get('meta', {})
for i, s in enumerate(data.get('shares', []), 1):
  fname = os.path.join('split-out', f"{out_prefix}-{i}.json")
  obj = {'meta': dict(meta, share_index=i), 'share': s}
  open(fname,'w').write(json.dumps(obj, indent=2))
print('Wrote', len(data.get('shares', [])), 'files to split-out')
PY

```

This creates `split-out/share-1.json`, `split-out/share-2.json`, etc., using
the metadata from the combined file. The resulting files are compatible with
the `--shares-file` and `--shares-dir` recovery options.

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

This implementation is released into the Public Domain under CC0 and OWFa licenses.
