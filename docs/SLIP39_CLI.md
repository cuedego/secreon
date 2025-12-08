# SLIP-39 CLI Documentation

The Secreon SLIP-39 CLI provides a complete implementation of the [SLIP-39](https://github.com/satoshilabs/slips/blob/master/slip-0039.md) standard for Shamir's Secret Sharing, optimized for cryptocurrency wallets.

## Table of Contents

- [Overview](#overview)
- [Commands](#commands)
  - [generate-seed](#generate-seed)
  - [generate](#generate)
  - [recover](#recover)
  - [info](#info)
  - [validate](#validate)
- [Examples](#examples)
- [Security Considerations](#security-considerations)

## Overview

SLIP-39 allows you to split a secret (typically a cryptocurrency wallet seed) into multiple shares using Shamir's Secret Sharing. The secret can only be recovered by combining a sufficient number of shares (the threshold).

**Key Features:**
- Two-level secret sharing (groups with members)
- BIP-39 compatibility
- Passphrase encryption
- Checksum validation
- Trezor-compatible implementation

## Commands

### generate-seed

Generate a new BIP-39 seed phrase.

```bash
secreon slip39 generate-seed [options]
```

**Options:**
- `--words, -w {12,15,18,21,24}` - Number of words (default: 24)
- `--passphrase, -p PASSPHRASE` - Optional BIP-39 passphrase
- `--out, -o FILE` - Output file (default: stdout)
- `--show-seed` - Display the master seed in hex format

**Examples:**

```bash
# Generate a 24-word seed phrase
secreon slip39 generate-seed --words 24

# Generate and save to file
secreon slip39 generate-seed --words 24 --out my-seed.txt

# Generate with BIP-39 passphrase and show hex seed
secreon slip39 generate-seed --words 24 --passphrase "my passphrase" --show-seed
```

### generate

Generate SLIP-39 shares from a secret.

```bash
secreon slip39 generate [options]
```

**Input Options (one required):**
- `--bip39 MNEMONIC` - BIP-39 mnemonic to split (24 words)
- `--bip39-file FILE` - File containing BIP-39 mnemonic
- `--secret HEX` - Secret as hex string (32 bytes = 64 hex chars)
- `--secret-file FILE` - File containing secret (raw bytes)

**Share Options:**
- `--groups, -g SPEC [SPEC ...]` - Group specifications as "threshold,count" (required)
- `--group-threshold, -t N` - Number of groups required to recover (default: all groups)
- `--passphrase, -p PASS` - Passphrase for encryption (recommended)
- `--iteration-exponent, -e N` - PBKDF2 iteration exponent 0-4 (default: 1)
- `--extendable` - Create extendable backup (default: true)
- `--no-extendable` - Create non-extendable backup

**Output Options:**
- `--out, -o FILE` - Output file for shares (default: stdout)
- `--split-shares` - Output each share to a separate file
- `--out-dir DIR` - Output directory for split shares (default: current directory)

**Examples:**

```bash
# Single group: 3-of-5 shares
secreon slip39 generate \
    --bip39 "word1 word2 ... word24" \
    --groups "3,5" \
    --passphrase "MyPassword" \
    --out shares.json

# Two groups: need 2-of-3 from Group 1 OR 3-of-5 from Group 2
secreon slip39 generate \
    --bip39 "word1 word2 ... word24" \
    --groups "2,3" "3,5" \
    --group-threshold 1 \
    --passphrase "MyPassword" \
    --split-shares \
    --out-dir ./shares

# Three groups with 2-of-3 requirement
secreon slip39 generate \
    --secret 6279dd1b4ee16db237eae885ad951996ebfde973aef9df5018aead46a947fa82 \
    --groups "2,3" "3,5" "1,1" \
    --group-threshold 2 \
    --passphrase "MyPassword" \
    --out shares.json
```

**Group Specifications:**

The `--groups` parameter takes one or more "threshold,count" pairs:
- `"3,5"` means "need 3 shares out of 5 to reconstruct this group"
- Multiple groups enable flexible recovery scenarios

**Common Configurations:**

1. **Basic**: Single group, 3-of-5
   ```bash
   --groups "3,5"
   ```

2. **Backup**: Two groups where you can recover with either
   ```bash
   --groups "2,3" "3,5" --group-threshold 1
   ```

3. **Multi-sig style**: Need shares from multiple groups
   ```bash
   --groups "2,3" "2,3" "1,1" --group-threshold 2
   ```

### recover

Recover secret from SLIP-39 shares.

```bash
secreon slip39 recover [options]
```

**Input Options (one required):**
- `--shares FILE [FILE ...]` - JSON file(s) containing shares
- `--shares-dir DIR` - Directory containing share files
- `--mnemonics, -m MNEM [MNEM ...]` - Share mnemonics directly

**Other Options:**
- `--passphrase, -p PASS` - Passphrase for decryption (if used during generation)
- `--out, -o FILE` - Output file for recovered secret (default: stdout)
- `--format {hex,bip39}` - Output format (default: hex)

**Examples:**

```bash
# Recover from share files
secreon slip39 recover \
    --shares share-1.json share-2.json share-3.json \
    --passphrase "MyPassword"

# Recover from directory
secreon slip39 recover \
    --shares-dir ./shares \
    --passphrase "MyPassword" \
    --out recovered.txt

# Recover from mnemonics directly
secreon slip39 recover \
    --passphrase "MyPassword" \
    --mnemonics \
        "lizard lily acrobat echo ..." \
        "lizard lily acrobat email ..." \
        "lizard lily beard eclipse ..."
```

**Note:** You must provide exactly the threshold number of shares from enough groups to meet the group threshold. Extra shares from the same group will cause an error.

### info

Display information about a SLIP-39 share without recovering the secret.

```bash
secreon slip39 info [MNEMONIC] [options]
```

**Options:**
- `MNEMONIC` - SLIP-39 share mnemonic to inspect (positional)
- `--file, -f FILE` - JSON file containing share

**Examples:**

```bash
# Display info from mnemonic
secreon slip39 info "lizard lily acrobat echo advocate package ..."

# Display info from file
secreon slip39 info --file share-1.json
```

**Output includes:**
- Share identifier
- Iteration exponent
- Group index and threshold
- Member index and threshold
- Value length
- Extendable flag

### validate

Validate SLIP-39 share mnemonics.

```bash
secreon slip39 validate [MNEMONIC ...] [options]
```

**Options:**
- `MNEMONIC` - One or more share mnemonics (positional)
- `--file, -f FILE [FILE ...]` - File(s) containing shares (JSON or plain text)

**Examples:**

```bash
# Validate mnemonics
secreon slip39 validate \
    "lizard lily acrobat echo ..." \
    "lizard lily acrobat email ..."

# Validate from files
secreon slip39 validate -f share-1.json share-2.json share-3.json

# Validate all shares in directory
secreon slip39 validate -f ./shares/*.json
```

## Examples

### Complete Workflow

```bash
# 1. Generate a new seed
secreon slip39 generate-seed --words 24 --out seed.txt
BIP39_SEED=$(cat seed.txt | tail -1)

# 2. Split into SLIP-39 shares (2-of-3 groups)
secreon slip39 generate \
    --bip39 "$BIP39_SEED" \
    --groups "2,3" "3,5" \
    --group-threshold 2 \
    --passphrase "MySecurePassword" \
    --split-shares \
    --out-dir ./my-shares

# 3. Validate shares
secreon slip39 validate -f ./my-shares/*.json

# 4. Check share info
secreon slip39 info --file ./my-shares/slip39-g1-s1.json

# 5. Recover secret (using minimum required shares)
secreon slip39 recover \
    --passphrase "MySecurePassword" \
    --shares \
        ./my-shares/slip39-g1-s1.json \
        ./my-shares/slip39-g1-s2.json \
        ./my-shares/slip39-g2-s1.json \
        ./my-shares/slip39-g2-s2.json \
        ./my-shares/slip39-g2-s3.json
```

### Simple Single-Group Backup

```bash
# Generate 3-of-5 shares
secreon slip39 generate \
    --bip39 "your 24 word seed phrase here..." \
    --groups "3,5" \
    --passphrase "password" \
    --out shares.json

# Later recover with any 3 shares
secreon slip39 recover \
    --shares shares.json \
    --passphrase "password"
```

### Advanced Multi-Group Setup

```bash
# Create a sophisticated multi-sig style backup:
# - Group 1 (Family): Need 2 of 3 shares
# - Group 2 (Friends): Need 3 of 5 shares  
# - Group 3 (Lawyer): 1 of 1 share (backup)
# - Need ANY 2 of these 3 groups to recover

secreon slip39 generate \
    --bip39-file my-seed.txt \
    --groups "2,3" "3,5" "1,1" \
    --group-threshold 2 \
    --passphrase "MyVerySecurePassword" \
    --split-shares \
    --out-dir ./distributed-backup

# You can recover with:
# - 2 family shares + 3 friend shares
# - 2 family shares + 1 lawyer share
# - 3 friend shares + 1 lawyer share
```

## Security Considerations

### Passphrases

- **Always use a passphrase** for additional security
- Passphrase is used with PBKDF2-HMAC-SHA256 encryption
- Lost passphrase = lost access to your secret
- Store passphrase separately from shares

### Share Distribution

- **Never store all shares together**
- Distribute shares to different physical/digital locations
- Consider giving shares to trusted individuals
- Use group thresholds to balance security and availability

### Iteration Exponent

- Higher values increase security but slow down recovery
- Default (1) = 5000 iterations per round
- Maximum (4) = 80000 iterations per round
- Affects both generation and recovery time

### Backup Strategy

Recommended approach:
1. Generate with multiple groups
2. Set group threshold to 2 or more
3. Distribute groups to different trusted parties
4. Keep one "emergency" group (1-of-1) in very secure location
5. Test recovery before trusting the backup

### Trezor Compatibility

This implementation is fully compatible with Trezor's SLIP-39 implementation. You can:
- Generate shares in Secreon and recover in Trezor
- Generate shares in Trezor and recover in Secreon
- Mix shares between implementations

## Technical Details

- **Standard**: [SLIP-39](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
- **Encryption**: Feistel cipher with PBKDF2-HMAC-SHA256
- **Field**: GF(256) for Shamir's Secret Sharing
- **Checksum**: RS1024 error detection
- **Wordlist**: 1024 words from SLIP-39 standard
- **Compatible with**: Trezor Model T, Trezor Safe 3

## See Also

- [SLIP-39 Specification](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
- [BIP-39 Specification](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
- [Demo Script](../examples/slip39-cli-demo.sh)
- [Technical Documentation](./TECHNICAL.md)

