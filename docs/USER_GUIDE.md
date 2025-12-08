# SLIP-39 User Guide & Documentation

**Version**: 1.0
**Date**: December 8, 2025
**Status**: Production Ready

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Topics](#advanced-topics)
8. [FAQ](#faq)

---

## Introduction

### What is SLIP-39?

SLIP-39 (Shamir's Secret Sharing for SLIP-0039) is a standard for splitting cryptocurrency seed phrases into multiple shares. It enables:

- **Threshold-based recovery**: Recover your seed from M out of N shares (e.g., 2 out of 3)
- **Passphrase protection**: Additional encryption layer for maximum security
- **Trezor compatibility**: Interoperable with Trezor hardware wallets
- **Error detection**: Built-in checksum validation (RS1024)

### Why Use SLIP-39?

- **Single Point of Failure**: A traditional seed phrase is vulnerable to theft or loss of one copy
- **Threshold Security**: Distribute shares across multiple locations; attacker needs multiple shares to recover your seed
- **Disaster Recovery**: Lose one share? Recover from the rest (if below threshold)
- **Custody Options**: 
  - Solo custody: Split seed among yourself (3-of-5 for fault tolerance)
  - Group custody: Split among family/business partners (2-of-3)
  - Institutional: Multi-signature with sharesholders

### When NOT to Use SLIP-39

- **Simple accounts**: Single accounts with low value may not need SSS complexity
- **Emergency only**: If you need frequent access to your seed, traditional backup may be more practical
- **Centralized**: Don't store all shares in one location (defeats the purpose)

---

## Installation

### Requirements

- Python 3.8 or higher
- No external dependencies (uses only Python standard library)

### Installation from Source

```bash
# Clone the repository
git clone https://github.com/cuedego/secreon.git
cd secreon

# Optional: Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode (allows importing slip39 as a module)
python3 -m pip install -e .

# Verify installation
python3 -c "import slip39; print(f'SLIP-39 version: {slip39.__version__}')"
```

### Installation from PyPI (when available)

```bash
python3 -m pip install secreon
secreon slip39 --help
```

### Verify Installation

```bash
# Test the CLI
secreon slip39 --help

# Quick functionality test
secreon slip39 generate --help
secreon slip39 recover --help
secreon slip39 info --help
secreon slip39 validate --help
```

---

## Quick Start

### Generate a New Seed Phrase

```bash
# Generate a random 24-word BIP-39 seed
secreon slip39 generate-seed --words 24

# Output: (your-random-seed-phrase)
```

### Split Seed into SLIP-39 Shares

```bash
# Create 5 shares, need 3 to recover (3-of-5 threshold)
secreon slip39 generate \
  --bip39 "your 24 word seed phrase here" \
  --group-threshold 1 \
  --groups "3,5" \
  --passphrase "MySecurePassphrase" \
  --output shares.txt
```

This creates:
- **1 group threshold**: Only 1 group required (standard single-group setup)
- **3-of-5 member threshold**: Need 3 out of 5 shares to recover
- **Encrypted with passphrase**: Wrong passphrase → wrong seed recovered
- **Output file**: Contains all 5 shares in mnemonic format

### Recover Seed from Shares

```bash
# Provide the minimum required shares (3 in this case)
secreon slip39 recover \
  --input-file share-1.txt share-2.txt share-3.txt \
  --passphrase "MySecurePassphrase"

# Output: (original-seed-phrase)
```

### Inspect Share Information

```bash
# See share metadata without recovering
secreon slip39 info share-1.txt

# Output:
# Group Index: 0
# Member Index: 0
# Group Threshold: 1
# Member Threshold: 3
# Extendable: false
# Iteration Exponent: 0
```

---

## Detailed Usage

### Command Reference

#### `secreon slip39 generate-seed`

Generate a new random BIP-39 seed phrase.

**Usage**:
```bash
secreon slip39 generate-seed [--words 12|24]
```

**Options**:
- `--words` (default: 24): Generate 12-word (128-bit) or 24-word (256-bit) seed
  - 12-word: Faster, less secure (use for low-value accounts)
  - 24-word: Slower, more secure (recommended for cryptocurrencies)

**Example**:
```bash
# 24-word seed (256-bit security)
secreon slip39 generate-seed --words 24

# 12-word seed (128-bit security)
secreon slip39 generate-seed --words 12
```

---

#### `secreon slip39 generate`

Split a seed phrase into SLIP-39 shares.

**Usage**:
```bash
secreon slip39 generate \
  --bip39 "seed phrase..." \
  [--group-threshold <n>] \
  [--groups "<m1>,<n1>" "<m2>,<n2>" ...] \
  [--passphrase "password"] \
  [--iteration-exponent <0-31>] \
  [--extendable] \
  [--output <file>]
```

**Required Options**:
- `--bip39`: The seed phrase to split (24 or 12 words)

**Threshold Configuration**:
- `--group-threshold` (default: 1): Number of groups needed to recover seed
- `--groups` (default: "2,3"): Threshold and count for each group in format "threshold,count"
  - Examples:
    - `"2,3"` — 2 of 3 shares needed
    - `"3,5"` — 3 of 5 shares needed
    - `"1,1"` — All shares in one group; 1 of 1 member (single share, no SSS)

**Security Options**:
- `--passphrase`: Additional encryption layer (required to recover seed)
  - Should be strong, unique, memorizable
  - Can be empty string for no passphrase (less secure)
  - Only printable ASCII characters (space, letters, numbers, punctuation)
- `--iteration-exponent` (default: 0): PBKDF2 iteration count = 2^(exponent+8)
  - 0: Fast (256 iterations) — test/low-security use
  - 5: Medium (8,192 iterations) — standard, recommended
  - 10: Slow (262,144 iterations) — high-security, offline use
  - 20: Very slow (1M+ iterations) — extreme security

**Advanced Options**:
- `--extendable`: Allow future addition of shares (Trezor feature)
- `--output` (default: shares.txt): Output file for shares

**Examples**:

```bash
# Basic: 3-of-5 shares, no passphrase, standard security
secreon slip39 generate \
  --bip39 "your seed here" \
  --groups "3,5"

# Secure: 2 groups with different thresholds, strong passphrase
secreon slip39 generate \
  --bip39 "your seed here" \
  --group-threshold 2 \
  --groups "2,3" "3,5" \
  --passphrase "MyVerySecurePassphrase123!" \
  --iteration-exponent 10

# Solo custody: 3-of-5 with passphrase, high security
secreon slip39 generate \
  --bip39 "your seed here" \
  --groups "3,5" \
  --passphrase "MemorizeThis" \
  --iteration-exponent 5 \
  --output solo-shares.txt
```

---

#### `secreon slip39 recover`

Recover a seed phrase from SLIP-39 shares.

**Usage**:
```bash
secreon slip39 recover \
  --input-file <share1> [<share2> ...] \
  [--passphrase "password"] \
  [--output <file>]
```

**Required Options**:
- `--input-file`: One or more share files (must meet threshold requirement)

**Security Options**:
- `--passphrase`: Same passphrase used during generation
  - If wrong passphrase: Decryption will succeed but with wrong seed
  - No checksum validation (user responsibility to verify seed is correct)

**Output**:
- `--output` (optional): Save seed to file instead of printing to stdout
  - Recommended: Redirect to file on secure medium
  - Example: `secreon slip39 recover ... --output seed.txt`

**Examples**:

```bash
# Recover from shares, prompt for passphrase
secreon slip39 recover \
  --input-file share-1.txt share-2.txt share-3.txt

# Recover with passphrase, save to file
secreon slip39 recover \
  --input-file share-1.txt share-2.txt share-3.txt \
  --passphrase "MySecurePassphrase" \
  --output recovered-seed.txt

# Recover and display
secreon slip39 recover \
  --input-file group1-share1.txt group1-share2.txt group2-share1.txt \
  --passphrase "MySecurePassphrase"
```

---

#### `secreon slip39 info`

Inspect share metadata without recovering.

**Usage**:
```bash
secreon slip39 info [<share1> ...]
```

**Options**:
- Positional arguments: One or more share files

**Output**:
- Group Index: Which group this share belongs to
- Member Index: Position within the group
- Group Threshold: How many groups required to recover
- Member Threshold: How many members per group required
- Extendable: Whether future shares can be added
- Iteration Exponent: PBKDF2 iteration count factor

**Example**:

```bash
# Inspect all shares in a directory
secreon slip39 info shares/*

# Output:
# File: shares/share-1.txt
# Group Index: 0
# Member Index: 0
# Group Threshold: 1
# Member Threshold: 3
# Extendable: false
# Iteration Exponent: 0
# 
# File: shares/share-2.txt
# ...
```

---

#### `secreon slip39 validate`

Validate share files (checksum, format).

**Usage**:
```bash
secreon slip39 validate [<share1> ...]
```

**Options**:
- Positional arguments: One or more share files

**Checks**:
- ✓ Valid mnemonic format (words from SLIP-39 wordlist)
- ✓ Valid checksum (RS1024 error detection)
- ✓ Valid encoding (group/member indices, flags)

**Example**:

```bash
# Validate all shares
secreon slip39 validate shares/*

# Output: ✓ All shares valid
# or: ✗ Invalid checksum in share-2.txt
```

---

### Output Format

Shares can be stored in multiple formats:

#### Text Format (Mnemonic Words)

```
anatomy branch academic acid badge badge balance balance beach beacon beacon bear beat beauty because become beef beer before begin behalf behind believe below belt bench
```

**Advantages**:
- Human-readable (can write by hand if needed)
- Robust (can correct OCR errors via checksum)
- Compatible with Trezor (can import into hardware wallet)

**Disadvantages**:
- Long to write by hand (90 words per share)
- Requires manual entry for recovery

#### JSON Format (Machine-Readable)

```json
{
  "mnemonic": "anatomy branch academic acid badge...",
  "group_index": 0,
  "member_index": 0,
  "group_threshold": 1,
  "member_threshold": 3,
  "extendable": false,
  "iteration_exponent": 0
}
```

**Advantages**:
- Machine-readable (easy to parse)
- Includes metadata (no need to inspect separately)
- Fast recovery (no manual entry)

**Disadvantages**:
- Larger file size
- Requires file storage (cannot write by hand)

---

## Security Best Practices

### Passphrase Management

1. **Use Strong Passphrases**:
   - ✓ Length: 12+ characters
   - ✓ Mix: Uppercase, lowercase, numbers, punctuation
   - ✗ Avoid: Dictionary words, birthdays, sequential patterns
   - Example good: `Tr0pic@lP1neapp1e!` (not a dict word, mixed case/numbers/symbols)
   - Example bad: `MyPassword123` (too common, predictable pattern)

2. **Store Separately from Shares**:
   - Shares: Hidden in secure location (safe, safety deposit box, distributed across people)
   - Passphrase: Memorized or stored separately (brain, secure password manager)
   - Attacker needs BOTH to recover seed

3. **Unique Passphrases**:
   - Use different passphrase for each seed (don't reuse)
   - Compromise of one passphrase doesn't expose other seeds

4. **Recovery Plan**:
   - Document somewhere secure: "If I forget passphrase, how will recovery work?"
   - Consider backup passphrase (stored in different location)
   - Test recovery with correct passphrase periodically

### Share Distribution

#### Scenario 1: Solo Custody (Individual Protection)

**Setup**: 3-of-5 shares across personal locations

```
Location 1: Safe at home (Share 1)
Location 2: Bank safety deposit (Share 2)
Location 3: Trusted family member (Share 3)
Location 4: Another safe location (Share 4)
Location 5: Backup at friend's house (Share 5)
```

**Security**:
- Attacker needs 3 shares → hard to get all 3
- Lose 2 shares → still recoverable
- Natural disaster destroys 1 location → still recoverable

**Recovery Time**: Hours to days (collect from 3 locations)

#### Scenario 2: Multi-Signature (Group Custody)

**Setup**: 2-of-3 groups, each with 2-of-3 members

```
Group 1 (You): 2-of-3 shares
  - Safe at home (You-1)
  - Bank safety deposit (You-2)
  - Lawyer's office (You-3)

Group 2 (Spouse): 2-of-3 shares
  - Spouse's safe (Spouse-1)
  - Bank safety deposit (Spouse-2)
  - Parent's house (Spouse-3)

Group 3 (Business Partner): 2-of-3 shares
  - Partner's safe (Partner-1)
  - Office safe (Partner-2)
  - CPA's office (Partner-3)
```

**Security**:
- Need 2 out of 3 groups → prevents single person from recovering alone
- Each group has 2-of-3 → loss of one share per group still allows recovery
- Highest security: requires cooperation of 2 stakeholders

**Recovery Time**: Days (need to coordinate between 2 people)

#### Scenario 3: Institutional Custody

**Setup**: Multi-signature with custodians, auditors, legal

```
Custodian Group: 3-of-5 shares
  - Vault 1, Custodian A
  - Vault 2, Custodian B
  - Vault 3, Custodian C
  - Vault 4, Custodian D
  - Vault 5, Custodian E

Overall: 2-of-3 groups
  - Custodian group (above)
  - Auditor group (3-of-5 shares held by audit committee)
  - Legal group (3-of-5 shares held by legal team)
```

**Security**:
- Single custodian cannot recover alone
- Need cooperation across multiple independent parties
- Highest institutional security

**Recovery Time**: Weeks (requires coordination across all parties)

### Storage Best Practices

1. **Physical Security**:
   - [ ] Use fire-resistant safe or safety deposit box
   - [ ] Distribute across multiple locations (don't keep all shares in one place)
   - [ ] Consider geographically distant locations (avoid single natural disaster)

2. **Environmental Protection**:
   - [ ] Paper: Use acid-free paper for long-term durability
   - [ ] Laminate or place in plastic sleeve (water protection)
   - [ ] Store in cool, dry place (avoid humidity, temperature extremes)
   - [ ] Avoid direct sunlight (ink fading)

3. **Access Control**:
   - [ ] Limit number of people with access
   - [ ] Keep passphrase separate from shares
   - [ ] Document who has access, where shares are stored
   - [ ] Periodic audits (are all shares still in place?)

4. **Backup Copies**:
   - [ ] Create multiple copies of critical shares (not required, but recommended)
   - [ ] Store backups in different location than originals
   - [ ] Test periodically that shares are readable/recoverable

### Threat Model

**Secreon protects against**:
- ✓ Loss of one share (if below threshold)
- ✓ Theft of one or two shares (if threshold > 2)
- ✓ Theft without passphrase (shares alone are encrypted)
- ✓ Physical destruction of one storage location

**Secreon does NOT protect against**:
- ✗ Attacker with all shares + passphrase (can recover seed)
- ✗ Passphrase is weak (brute-force may succeed)
- ✗ Recovery passphrase is visible during entry (keylogger, shoulder surfing)
- ✗ Hardware compromise during recovery (infected computer may capture seed)

---

## Troubleshooting

### Common Issues

#### "Wrong number of mnemonics"

**Error**:
```
MnemonicError: Wrong number of mnemonics. Expected 2 mnemonics starting with "anatomy branch academic ...", but 3 were provided.
```

**Causes**:
- Provided shares from multiple groups when only 1 group needed
- Provided more shares than required by threshold
- Mixed shares from different splitting configurations

**Solution**:
1. Check share metadata: `secreon slip39 info <shares>`
2. Ensure all shares have same group/member threshold
3. Provide exactly `group_threshold` groups, each with `member_threshold` members
4. Check group indices: if multiple groups, need 1 share from each

#### "Wrong passphrase" (Silent Failure)

**Problem**:
```
# Recovery appears to succeed but produces wrong seed
secreon slip39 recover --input-file ... --passphrase "WrongPassword"
# Output: wrong-seed-phrase
```

**Why**:
- SLIP-39 doesn't validate passphrase correctness (no integrity check)
- Wrong passphrase → wrong decryption → different seed
- This is by design (privacy: no way to prove which passphrase is "correct")

**Solution**:
1. Verify passphrase: Does it match what you used to generate?
2. Test recovery with known shares first
3. Document passphrase securely before splitting

#### "Invalid checksum"

**Error**:
```
MnemonicError: Invalid checksum on share "anatomy branch academic..."
```

**Causes**:
- Share was corrupted during storage/transmission
- Typo when copying share manually
- File was partially corrupted

**Solution**:
1. Check file for corruption: `secreon slip39 validate <share>`
2. If stored on paper: re-read carefully (OCR may have errors)
3. Use checksum to correct single errors (RS1024 can fix 1 error)
4. If multiple errors: share may be unrecoverable; use another share

#### "Insufficient number of groups"

**Error**:
```
MnemonicError: Insufficient number of mnemonic groups. The required number of groups is 2.
```

**Causes**:
- Group threshold is 2 but you only provided 1 group
- Shares are from same group (not different groups)

**Solution**:
1. Check `secreon slip39 info` for group indices
2. If all shares are group 0, you need shares from group 1 (or higher)
3. Provide shares from different groups: `secreon slip39 recover --input-file group0-share.txt group1-share.txt ...`

### Validation Troubleshooting

#### Check if recovery is possible

```bash
# Step 1: Get share info
secreon slip39 info share-*.txt

# Step 2: Count shares per group
# If group_threshold=2, need shares from 2 different groups
# If member_threshold=3, need 3 shares from each group

# Step 3: Try recovery
secreon slip39 recover --input-file <shares from 2 groups>
```

#### Recover and verify

```bash
# Step 1: Generate test seed
TEST_SEED=$(secreon slip39 generate-seed --words 24)
echo "Test seed: $TEST_SEED"

# Step 2: Split into shares
secreon slip39 generate --bip39 "$TEST_SEED" --groups "2,3" --output test-shares.txt

# Step 3: Extract specific shares and recover
secreon slip39 recover --input-file share-1.txt share-2.txt

# Step 4: Verify recovered seed matches original
# (output should match $TEST_SEED)
```

---

## Advanced Topics

### Custom Group Configurations

SLIP-39 supports complex multi-group schemes:

#### Example 1: 2-of-3 Groups, Each 2-of-3

```bash
secreon slip39 generate \
  --bip39 "$SEED" \
  --group-threshold 2 \
  --groups "2,3" "2,3" "2,3"
```

**Setup**:
- 3 groups total (Group 0, Group 1, Group 2)
- Need 2 out of 3 groups to recover
- Each group has 3 shares; need 2 to recover that group

**Recovery options**:
- Groups 0+1 with 2 shares each = 4 total shares needed
- Groups 0+2 with 2 shares each = 4 total shares needed
- Groups 1+2 with 2 shares each = 4 total shares needed

#### Example 2: Variable Thresholds

```bash
secreon slip39 generate \
  --bip39 "$SEED" \
  --group-threshold 2 \
  --groups "1,1" "2,3" "3,5"
```

**Setup**:
- Group 0: 1-of-1 (single share; must use this group)
- Group 1: 2-of-3 (need 2 out of 3)
- Group 2: 3-of-5 (need 3 out of 5)

**Recovery**:
- Must use Group 0 share (1 share)
- Plus either Group 1 (2 shares) OR Group 2 (3 shares)
- Total: Either 3 or 4 shares needed

**Use case**: Group 0 is "master" share kept in safe, Groups 1+2 are distributed to family

### Iteration Exponent Explained

The iteration exponent controls PBKDF2 iteration count:

```
iterations = 2^(iteration_exponent + 8)

exponent=0:  256 iterations    (instant)
exponent=1:  512 iterations    (instant)
exponent=5:  8,192 iterations  (fast, ~0.1s)
exponent=10: 262,144 iterations (medium, ~1s)
exponent=15: 8M iterations     (slow, ~30s)
exponent=20: 262M iterations   (very slow, ~15m)
```

**Recommendations**:
- **Default (0-5)**: Normal computers, most use cases
- **High (10-15)**: Air-gapped machines, offline use, high-security
- **Extreme (20+)**: Only if you have specific security requirements

**Security vs Performance**:
- Higher exponent = harder to brute-force passphrase
- But also slower legitimate recovery
- Sweet spot: exponent=5 (8K iterations, ~0.1s, reasonable security)

### Extendable Shares

The `--extendable` flag allows future share addition:

```bash
secreon slip39 generate \
  --bip39 "$SEED" \
  --groups "2,3" \
  --extendable \
  --output shares.txt
```

**Use case**: You think you might want to add more shares later

**Note**: This is a Trezor feature; secreon doesn't currently support adding shares after generation. The flag is here for future compatibility and to create Trezor-compatible shares.

---

## FAQ

### General Questions

**Q: How is SLIP-39 different from BIP-39?**

A: 
- **BIP-39**: Standard for mnemonic seed phrases (12 or 24 words)
- **SLIP-39**: Standard for splitting BIP-39 seeds into shares (90 words per share)
- SLIP-39 uses BIP-39 compatibility but adds Shamir's Secret Sharing

**Q: Can I use SLIP-39 with any wallet?**

A: 
- ✓ Wallets with SLIP-39 support: Trezor (recent models)
- ✗ Wallets without SLIP-39 support: Will see 90-word mnemonic as invalid
- Solution: Recover seed → import as BIP-39 into standard wallet

**Q: Is my seed secure after splitting?**

A:
- Yes, if:
  - Shares are distributed to separate secure locations
  - Passphrase is strong and stored separately
  - Below-threshold number of shares are ever in same location
- No, if:
  - All shares kept in one place
  - Passphrase is weak
  - Shares are exposed to same attack vector

**Q: What if I forget my passphrase?**

A:
- ✗ Secreon cannot recover a forgotten passphrase
- ✗ No "reset" or recovery mechanism
- Solution: Document passphrase securely (password manager, safe, mental note)

**Q: Can I recover if I lose one share?**

A:
- ✓ Yes, if you have more than threshold shares remaining
- Example: 3-of-5 threshold → can lose 2 shares, still recoverable
- ✗ No, if you lose threshold or more shares
- Lesson: Don't use 2-of-2 (loss of one share = permanent loss of seed)

### Security Questions

**Q: What's the difference between group threshold and member threshold?**

A:
- **Group threshold**: How many separate groups you need
- **Member threshold**: How many shares per group you need
- Example: 2 groups, 2-of-3 members
  - Need shares from 2 different groups
  - Each group needs 2 out of 3 shares
  - Total: 4 shares from 2 groups minimum

**Q: Should I use a passphrase?**

A:
- ✓ Yes, if you can memorize/store it securely
- ✓ Adds another layer of security (shares alone insufficient)
- ✗ No, if you can't reliably remember it (forgot = lost seed)
- Recommendation: Use passphrase + physically secure share storage

**Q: Is higher iteration exponent always better?**

A:
- More secure against brute-force: Yes
- But slower legitimate recovery: Also yes
- Sweet spot: exponent=5 (8K iterations, ~0.1s, reasonable security)
- Higher: Only needed if you suspect passphrase could be guessed

**Q: Can Trezor use my SLIP-39 shares?**

A:
- ✓ Yes, recent Trezor models support SLIP-39
- ✗ Older Trezor models don't support SLIP-39 (only BIP-39)
- Solution: Import recovered seed into any BIP-39-compatible wallet

### Operational Questions

**Q: How long does recovery take?**

A:
- PBKDF2 (passphrase derivation): 0.1-30 seconds (depends on iteration exponent)
- Lagrange interpolation (combining shares): < 1 second
- Total: Usually < 1 second (instant with exponent=0-5)

**Q: Can I generate shares offline?**

A:
- ✓ Yes, secreon has no network requirements
- ✓ Recommended: Generate on air-gapped machine for maximum security

**Q: How do I store shares long-term?**

A:
- Paper + laminate: 10+ years if stored dry
- Digital: USB/SSD in encrypted container (tested periodically)
- Combination: Paper original + digital backups in different locations
- Recommended: Acid-free paper, fire-resistant safe, geographically distributed

**Q: What if shares are found by attacker?**

A:
- ✓ Safe if passphrase is strong and unknown
- ✗ Not safe if attacker has passphrase too
- Mitigation: Use strong, unique passphrase; store separately from shares

**Q: Can I change my passphrase?**

A:
- ✗ No, passphrase is baked into encrypted shares
- Solution: Recover seed with old passphrase → re-split with new passphrase

**Q: Can I split shares into smaller shares?**

A:
- ✗ No, resharing is not supported in current version
- Workaround: Recover seed → re-split into new shares

---

**For more information, see**:
- `docs/TECHNICAL.md` — Technical design details
- `docs/SECURITY_AUDIT_CHECKLIST.md` — Security audit results
- `docs/SECURITY_POLICY_DEPLOYMENT.md` — Deployment guidelines
- `src/slip39/` — Source code with implementation details

---

**Last Updated**: December 8, 2025
**Status**: Production Ready
