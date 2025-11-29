# Secreon Documentation

## Architecture

### Core Components

- **`src/sss.py`** - Main Shamir's Secret Sharing implementation
  - Polynomial generation and evaluation
  - Lagrange interpolation for secret recovery
  - JSON serialization/deserialization
  - KDF support (SHA-256, PBKDF2)
  - CLI interface (generate/recover commands)

### Security Features

1. **Prime Field Arithmetic**: Uses Mersenne prime 2^2203-1 for operations
2. **KDF Support**: Optional PBKDF2 with configurable iterations and salt
3. **Modular Inverse Validation**: Ensures denominators are invertible
4. **Threshold Validation**: Enforces k-of-n security model
5. **Byte Length Preservation**: Stores original length for lossless recovery

### File Formats

#### Combined Shares JSON Structure (Legacy/Default)

```json
{
  "meta": {
    "minimum": 3,
    "shares": 5,
    "prime": 170141183460469231731687303715884105727,
    "secret_byte_length": 146,
    "kdf": {
      "kdf": "pbkdf2",
      "iterations": 100000,
      "salt": "base64encodedstring"
    }
  },
  "shares": [
    {"x": 1, "y": 12345...},
    {"x": 2, "y": 67890...}
  ]
}

```

#### Individual Share JSON Structure (Split Shares)

When using `--split-shares`, each share is written to a separate file:

```json
{
  "meta": {
    "minimum": 3,
    "shares": 5,
    "share_index": 1,
    "prime": 170141183460469231731687303715884105727,
    "secret_byte_length": 146,
    "kdf": {
      "kdf": "pbkdf2",
      "iterations": 100000,
      "salt": "base64encodedstring"
    }
  },
  "share": {
    "x": 1,
    "y": 12345...
  }
}

```

**Benefits of Split Shares:**
- Eliminates risk of data corruption during manual file splitting
- Each file is self-contained with complete metadata
- Safer for distribution - no accidental exposure of multiple shares
- Simplifies share management and tracking

JSON Schemas for these formats are provided in `docs/share_schema.json`.

#### Configuration (config/default.json)

```json
{
  "minimum": 3,
  "shares": 5,
  "prime": null
}

```

**Note**: Secrets must NEVER be stored in configuration files.

## API Reference

### Core Functions


#### `make_random_shares(secret, minimum, shares, prime=_PRIME)`

Generates random Shamir shares for a secret.

**Parameters:**

- `secret` (int): The secret value to split
- `minimum` (int): Threshold - number of shares needed to recover
- `shares` (int): Total number of shares to generate
- `prime` (int, optional): Prime modulus for field arithmetic

**Returns:** List of (x, y) tuples representing share points

#### `recover_secret(shares, prime=_PRIME)`

Recovers the secret from share points using Lagrange interpolation.

**Parameters:**

- `shares` (list): List of (x, y) tuples
- `prime` (int, optional): Prime modulus used in generation

**Returns:** Recovered secret integer

### CLI Commands


#### Generate Command

```bash
python3 src/sss.py generate [OPTIONS]

```

**Options:**

- `--secret, -s`: Secret string
- `--secret-file, -f`: Path to file containing secret
- `--minimum, -m`: Threshold (default: 3)
- `--shares, -n`: Number of shares (default: 5)
- `--out, -o`: Output file for shares JSON (or base name for split shares)
- `--format`: json|lines (default: json)
- `--kdf`: sha256 or pbkdf2:ITERATIONS
- `--prime`: Custom prime modulus
- `--split-shares`: Generate individual files for each share

#### Recover Command

```bash
python3 src/sss.py recover [OPTIONS]

```

**Options:**

- `--shares-file, -i`: Path(s) to shares JSON file(s), can specify multiple
- `--shares-dir, -d`: Directory containing share files
- `--format`: json|lines (default: json)
- `--as-str`: Decode recovered secret as UTF-8 string
- `--out, -o`: Output file
- `--prime`: Override prime from metadata

**Recovery Methods:**

1. Single file: `--shares-file shares.json`
2. Multiple files: `--shares-file share-1.json share-2.json share-3.json`
3. Directory: `--shares-dir /path/to/shares/`

## Mathematical Background

Shamir's Secret Sharing is based on polynomial interpolation over finite fields:

1. **Secret Encoding**: Secret S becomes y-intercept of polynomial P(x) of degree k-1
2. **Share Generation**: Each share i is point (i, P(i) mod p)
3. **Recovery**: Given k points, Lagrange interpolation reconstructs P(0) = S

**Security**: Any k-1 or fewer shares reveal no information about the secret.

## Best Practices

### For BIP39 Seeds (24 words)

```bash
# Use default prime (2^2203-1) - automatically handles BIP39 seeds
# Use split shares for safer distribution
python3 src/sss.py generate --secret-file seed.txt --minimum 3 --shares 5 \
  --out share.json --split-shares

```

### For Passphrases

```bash
# Always use PBKDF2 with high iteration count
python3 src/sss.py generate --secret "my passphrase" --kdf pbkdf2:200000 \
  --out shares.json

```

### For Critical Data Distribution

```bash
# Split shares eliminate manual file editing risks
python3 src/sss.py generate --secret-file critical.key --minimum 4 --shares 7 \
  --out share.json --split-shares

# Distribute individual files to different secure locations
# Recovery from any 4 files:
python3 src/sss.py recover --shares-file share-1.json share-3.json \
  share-5.json share-7.json --as-str

```

### For Files

```bash
# Large files may need custom prime
python3 src/sss.py generate --secret-file document.pdf --out shares.json

```

## Testing

Run the test suite:

```bash
python3 tests/test_sss.py

```

All 17 tests should pass, including split shares functionality tests.

## Troubleshooting

### "Secret exceeds prime" Error

**Solution**: The default prime handles up to ~275 bytes. For larger secrets, specify a larger prime:

```bash
--prime $((2**4096 - 1))

```

### Recovery Produces Garbled Output

**Solution**: Use `--as-str` flag only for text secrets. For binary data, omit the flag and redirect output:

```bash
python3 src/sss.py recover --shares-file shares.json > output.bin

```

### KDF Metadata Not Found

This happens when recovering shares generated without KDF. The tool handles this automatically - no action needed.
