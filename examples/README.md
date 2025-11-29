# Examples

This directory contains example seed phrases and demo files for testing Secreon.

## Files

- `sample-seed.txt` - Example BIP39 24-word mnemonic phrase (NOT a real wallet!)

## Usage

### Generate shares from example seed

```bash
cd ..
python3 src/sss.py generate --secret-file examples/sample-seed.txt --minimum 3 --shares 5 --out examples/demo-shares.json
```

### Recover the seed

```bash
python3 src/sss.py recover --shares-file examples/demo-shares.json --as-str
```

## Important

**Never commit real wallet seeds or private keys!** The files in this directory are for demonstration purposes only.
