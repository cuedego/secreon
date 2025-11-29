# Configuration

This directory contains configuration files for Secreon.

## Files

- `default.json` - Default settings for share generation

## Configuration Options

```json
{
  "minimum": 3,      // Default threshold (shares needed to recover)
  "shares": 5,       // Default number of shares to generate
  "prime": null      // Default prime (null = use built-in 2^2203-1)
}
```

## Important Security Note

**NEVER store secrets, private keys, or seed phrases in configuration files!**

Secrets must always be provided via:
- `--secret` command line argument
- `--secret-file` file input

Configuration files are for non-sensitive parameters only.

## Custom Configuration

You can create custom config files and specify them with:

```bash
python3 secreon.py generate --config config/custom.json --secret "test"
```
