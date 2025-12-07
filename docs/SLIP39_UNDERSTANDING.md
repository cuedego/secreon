# Understanding SLIP-39 Feature Development

## Executive Summary

Secreon is a tool for secure storage of secrets using Shamir's Secret Sharing (SSS). The current implementation uses classic SSS with arithmetic over large prime fields. This document presents my understanding of adding support for **SLIP-39**, a modern standard for crypto wallet backup using SSS with human-readable mnemonics.

---

## Technical Context

### Current State of Secreon

Secreon implements:
- **Classic SSS**: Splitting secrets into shares using polynomials over a prime field (2^2203-1)
- **Share Format**: Pairs (x, y) serialized in JSON
- **KDF**: Support for SHA-256 and PBKDF2 for key derivation from passphrases
- **Simple CLI**: Commands `generate` and `recover`

**Limitations**:
- Shares are large numbers, not human-friendly
- Not interoperable with modern crypto wallets
- Does not support hierarchical schemes (groups)

### SLIP-39: The Standard

**SLIP-39** (Shamir's Secret-Sharing for Mnemonic Codes) is a standard from SatoshiLabs for BIP-32 wallet backup using SSS. Main features:

1. **Human-Readable Mnemonics**: 
   - Shares encoded as 20-33 words (not large numbers)
   - Wordlist of 1024 words (10 bits per word)
   - Unique 4-letter prefixes to facilitate entry

2. **Strong Checksum**:
   - Reed-Solomon RS1024 with 3 checksum words
   - Detects up to 3 errors with certainty
   - <1e-9 chance of failing to detect more errors

3. **Master Secret Encryption**:
   - 4-round Feistel cipher with PBKDF2
   - Optional passphrase support
   - Configurable iterations (10000×2^e)

4. **Two-Level Scheme**:
   - **Groups**: GT-of-G (e.g., 2 of 3 groups)
   - **Members**: Ti-of-Ni for each group (e.g., 3 of 5 members)
   - Allows flexible recovery policies

5. **GF(256) instead of Prime Field**:
   - Byte-oriented arithmetic (simpler)
   - SSS applied byte-by-byte
   - Compatible with AES (same irreducible polynomial)

6. **Verification Digest**:
   - When threshold ≥ 2, includes secret digest
   - Detects malicious or corrupted shares
   - Digest = HMAC-SHA256(random_part, secret)

### Why SLIP-39 is Important?

- **Interoperability**: Compatible with Trezor, Ledger, Electrum, Sparrow Wallet
- **Standard**: Open and stable specification
- **UX**: Mnemonics are more friendly than large numbers
- **Flexibility**: Two-level scheme allows sophisticated policies
- **Security**: Strong checksum + digest + encryption

---

## Deep Technical Analysis

### Fundamental Differences: Classic SSS vs SLIP-39

| Aspect | Classic SSS (Secreon) | SLIP-39 |
|---------|------------------------|---------|
| **Mathematical Field** | GF(p) - large prime (2^2203-1) | GF(256) - 256 elements |
| **Operations** | Modular integer arithmetic | Byte-oriented polynomial arithmetic |
| **Share Format** | (x, y) as large integers | Mnemonic of 20-33 words |
| **Encoding** | JSON with numbers | Wordlist of 1024 words |
| **Checksum** | None (or optional) | RS1024 mandatory |
| **Encryption** | Optional (KDF) | Feistel cipher mandatory |
| **Digest** | No | Yes (for threshold ≥ 2) |
| **Levels** | Single (T-of-N) | Two (groups + members) |
| **Interoperability** | None | Standard, multi-wallet |

### Technical Challenges

#### 1. GF(256) Arithmetic
**Complexity**: MEDIUM

GF(256) uses polynomial representation with operations modulo x^8 + x^4 + x^3 + x + 1:
- **Addition**: XOR (trivial)
- **Multiplication**: Shift-and-XOR with polynomial reduction
- **Division**: Multiplicative inverse (use log/exp tables)

**Solution**:
- Pre-compute logarithm and exponential tables (256 entries each)
- Multiplication: `exp[(log[a] + log[b]) % 255]`
- Division: `exp[(log[a] - log[b]) % 255]`
- Lagrange interpolation adapted for GF(256)

**Reference**: Implementation in `python-shamir-mnemonic/shamir.py`

#### 2. RS1024 Checksum
**Complexity**: MEDIUM-HIGH

Reed-Solomon over GF(1024) for error detection:
- MDS code (Maximum Distance Separable)
- 3 checksum words = 30 bits
- Generator polynomial over GF(1024) with primitive root

**Solution**:
- Implement as BCH code (alternative view of Reed-Solomon)
- Follow reference implementation faithfully
- Tests with known values from specification

**Reference**: `python-shamir-mnemonic/rs1024.py`

#### 3. Feistel Cipher with PBKDF2
**Complexity**: MEDIUM

Encryption of master secret in 4 rounds:
- Each round uses PBKDF2-HMAC-SHA256
- Salt depends on `ext` flag:
  - ext=0: `"shamir" || identifier || R`
  - ext=1: just `R`
- Password: `round_number || passphrase`

**Solution**:
- Use `hashlib.pbkdf2_hmac` from stdlib
- Implement simple Feistel network (L, R swap + XOR)
- Ensure symmetry (encrypt/decrypt are inverses)

**Reference**: `python-shamir-mnemonic/cipher.py`

#### 4. Two-Level Scheme
**Complexity**: HIGH

Hierarchy: EMS → Group Shares → Member Shares

```
Master Secret
    ↓ (encrypt)
Encrypted Master Secret (EMS)
    ↓ (split GT-of-G)
Group Share 1, ..., Group Share G
    ↓ (split T1-of-N1, ..., TG-of-NG)
Member Shares
```

**Solution**:
- Implement split/recover recursively
- Validate parameter consistency between shares
- Support simple scheme (1 group) as special case

#### 5. Mnemonic Encoding/Decoding
**Complexity**: MEDIUM

Each share has complex field structure:

```
[id 15b][ext 1b][e 4b][GI 4b][GT 4b][G 4b][I 4b][T 4b][padding + share_value][checksum 30b]
```

Conversion: bits → words (each 10 bits = 1 word)

**Solution**:
- Implement bit-oriented packing/unpacking
- Validate padding (should be zeros and ≤ 8 bits)
- Follow specification order rigorously

**Reference**: `python-shamir-mnemonic/share.py`

---

## Proposed Architecture

### Module Structure

```
secreon/
├── src/
│   ├── sss.py              # Existing SSS (maintains compatibility)
│   └── slip39/             # New SLIP-39 implementation
│       ├── __init__.py     # Public API
│       ├── wordlist.py     # SLIP-39 + BIP-39 wordlists
│       ├── bip39.py        # BIP-39 mnemonic generation
│       ├── gf256.py        # GF(256) arithmetic
│       ├── rs1024.py       # RS1024 checksum
│       ├── cipher.py       # Feistel cipher / encryption
│       ├── share.py        # Share data structure + encoding
│       ├── shamir.py       # SLIP-39 SSS core
│       └── cli.py          # CLI commands
└── tests/
    ├── test_sss.py         # Existing tests
    └── slip39/
        ├── test_gf256.py
        ├── test_rs1024.py
        ├── test_cipher.py
        ├── test_share.py
        ├── test_shamir.py
        └── test_vectors.py # Official SLIP-39 test vectors
```

### Separation of Responsibilities

#### Layer 1: Fundamental Mathematics
- `gf256.py`: Field operations, interpolation
- `rs1024.py`: Checksum and validation

#### Layer 2: Cryptography
- `cipher.py`: Encrypt/decrypt master secret
- `wordlist.py`: Word ↔ index conversions

#### Layer 3: Secret Sharing
- `shamir.py`: Split/recover over GF(256)
- `share.py`: Data structure and encoding

#### Layer 4: BIP-39 Integration
- `bip39.py`: Generation and validation of seed phrases

#### Layer 5: User Interface
- `cli.py`: Commands for end user

### Data Flow

#### Generate:
```
BIP-39 Mnemonic (or hex)
    ↓
Master Secret (entropy)
    ↓ (+ passphrase, identifier, e)
Encrypted Master Secret
    ↓ (split GT-of-G)
Group Shares
    ↓ (split Ti-of-Ni per group)
Member Shares (bytes)
    ↓ (encode)
SLIP-39 Mnemonics (words)
```

#### Recover:
```
SLIP-39 Mnemonics (words)
    ↓ (decode)
Member Shares (bytes)
    ↓ (recover Ti-of-Ni per group)
Group Shares
    ↓ (recover GT-of-G)
Encrypted Master Secret
    ↓ (decrypt with passphrase)
Master Secret
    ↓ (optional)
BIP-39 Mnemonic
```

---

## Implementation Strategy

### Approach: Bottom-Up with Incremental Validation

1. **Foundations First**: GF(256), RS1024, wordlists
   - Each module tested in isolation
   - Validation with known values from specification

2. **Core SSS Next**: Split/recover over GF(256)
   - Round-trip tests
   - Threshold validation

3. **Cryptography and Encoding**: Cipher + Share structure
   - Encrypt/decrypt tests
   - Encoding/decoding tests

4. **High Level and CLI**: User-friendly API + user interface
   - End-to-end tests
   - UX validation

5. **Interoperability**: Cross-testing with other implementations
   - python-shamir-mnemonic
   - Official test vectors

### Development Principles

1. **Test-Driven Development (TDD)**:
   - Write tests before implementation
   - Use official test vectors as guide
   - 100% coverage of critical functions

2. **Compatibility First**:
   - Follow SLIP-39 specification rigorously
   - Use same variable/function names as spec
   - Validate against python-shamir-mnemonic frequently

3. **Security by Design**:
   - Use `secrets` module (not `random`)
   - Validate all inputs
   - Don't log/display secrets inadvertently
   - Clear memory where possible (Python limitation)

4. **Incremental Delivery**:
   - Functional MVP in 2-3 weeks
   - Advanced features iteratively
   - Each phase delivers value

---

## Use Cases and Examples

### Case 1: Simple Personal Backup
**Scenario**: User wants to protect personal wallet with redundancy

**Setup**:
```bash
# Generate BIP-39 seed
secreon slip39 generate-seed --out my-seed.txt

# Create 3-of-5 shares
secreon slip39 generate --seed-file my-seed.txt --threshold 3 --shares 5 --out shares/

# Distribute:
# - 1 at home
# - 1 at work
# - 1 in bank vault
# - 2 with trusted friends
```

**Recovery**:
```bash
# Gather any 3 shares
secreon slip39 recover --mnemonics shares/share-1.txt shares/share-3.txt shares/share-5.txt
```

### Case 2: Family Backup (Two Levels)
**Scenario**: You can recover alone OR family can recover together

**Setup**:
```bash
secreon slip39 generate --seed-file my-seed.txt \
  --group-threshold 1 \
  --group 2 2 \  # You: 2-of-2 (both needed)
  --group 3 5 \  # Family: 3-of-5
  --out shares/

# You keep Group 1 shares (2 different locations)
# Family receives Group 2 shares (5 people)
```

**Recovery**:
- **You alone**: Use 2 shares from Group 1
- **Family**: Gather 3 shares from Group 2

### Case 3: Corporate Multi-Sig
**Scenario**: Company needs approval from multiple departments

**Setup**:
```bash
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \  # Directors: 2-of-3
  --group 3 5 \  # Technical: 3-of-5
  --group 2 3 \  # Compliance: 2-of-3
  --passphrase "company-master-key" \
  --out shares/
```

**Recovery**: Any 2 complete groups + passphrase

---

## Risks and Mitigations

### Risk 1: Cryptographic Bugs
**Probability**: MEDIUM | **Impact**: CRITICAL

**Mitigations**:
- Follow reference implementation (python-shamir-mnemonic)
- Extensive testing (unit, integration, property-based)
- Security-focused code review
- Validation with official test vectors
- Cross-implementation testing
- External audit (desirable)

### Risk 2: Incompatibility
**Probability**: MEDIUM | **Impact**: HIGH

**Mitigations**:
- Follow SLIP-39 specification rigorously
- Cross-testing with python-shamir-mnemonic
- Use same test vectors
- Validate with hardware wallets (Trezor/Ledger) if possible

### Risk 3: Complexity for Users
**Probability**: HIGH | **Impact**: MEDIUM

**Mitigations**:
- Simple mode by default (T-of-N, 1 group)
- Clear documentation with examples
- Intuitive CLI with input validation
- Warnings about share distribution
- Step-by-step tutorial

### Risk 4: Performance
**Probability**: LOW | **Impact**: LOW

**Mitigations**:
- PBKDF2 dominant (expected, part of security)
- Pre-compute tables (GF256)
- Allow iteration exponent configuration
- Continuous benchmarking

---

## Success Criteria

### Technical:
- ✅ Passes 100% of official test vectors
- ✅ Interoperable with python-shamir-mnemonic
- ✅ Test coverage >80%
- ✅ No obvious vulnerabilities (code review)
- ✅ Acceptable performance (<10s for operations)

### Functional:
- ✅ User can generate BIP-39 seed
- ✅ User can create SLIP-39 shares (simple and advanced)
- ✅ User can recover master secret
- ✅ Passphrase support
- ✅ Intuitive CLI

### Quality:
- ✅ Complete documentation (user + tech)
- ✅ Clean and well-organized code
- ✅ Complete type hints
- ✅ Functional examples

---

## Estimates and Timeline

### MVP (Basic Functionality):
**Time**: 2-3 weeks full-time (80-120 hours)

**Includes**:
- GF(256), RS1024, wordlists
- Core SSS over GF(256)
- Cipher + Share encoding
- Basic CLI (generate-seed, generate, recover)
- Basic official test vectors
- Usage documentation

### Complete Feature:
**Time**: 5-6 weeks full-time (200-240 hours)

**Includes everything from MVP, plus**:
- Complete two-level scheme
- Configurable passphrase and iteration exponent
- Utility commands (info, validate)
- Cross-implementation testing
- Property-based tests
- Complete technical documentation
- Examples and demos
- Audit preparation

### Part-Time:
- **4h/day**: ~10-12 weeks for complete feature
- **2h/day**: ~20-24 weeks for complete feature

---

## Recommended Next Steps

### Immediate (Before Starting):
1. ✅ **Review this documentation** with stakeholders
2. ✅ **Environment setup** for development
3. ✅ **Download resources**:
   - SLIP-39 wordlist
   - BIP-39 wordlist
   - Official test vectors
   - python-shamir-mnemonic (reference)

### First Week:
1. **Day 1-2**: Implement GF(256) + tests
2. **Day 3**: Implement RS1024 + tests
3. **Day 4**: Implement wordlists + tests
4. **Day 5**: Phase 1 review and adjustments

### Second Week:
1. **Day 1-2**: Implement Feistel cipher + tests
2. **Day 3-4**: Implement Share structure + encoding
3. **Day 5**: Implement core SSS over GF(256)

### Third Week:
1. **Day 1**: BIP-39 support
2. **Day 2-3**: Basic CLI (generate-seed, generate, recover)
3. **Day 4-5**: Test vectors and validation

**MVP Delivered!** 🎉

---

## Conclusion

The implementation of SLIP-39 in secreon is **feasible and valuable**. Despite the technical complexity (GF(256), RS1024, Feistel cipher), following the specification rigorously and using the reference implementation as a guide makes the project manageable.

**Main Benefits**:
- Interoperability with modern crypto ecosystem
- Superior UX (mnemonics vs large numbers)
- Enhanced security (checksum + digest + encryption)
- Flexibility (two-level scheme)

**Main Challenges**:
- Specification complexity (many details)
- Ensure 100% compatibility
- Avoid cryptographic bugs

**Success Strategy**:
- Incremental and tested implementation
- Continuous validation (test vectors + cross-implementation)
- Focus on quality and security
- Clear documentation

With the detailed implementation plan provided, an experienced team or developer can deliver a functional MVP in 2-3 weeks and a complete implementation in 5-6 weeks of dedicated work.

---

**Last Updated**: 2025-12-06  
**Author**: AI Assistant (Claude Sonnet 4.5)  
**Status**: READY FOR REVIEW AND DEVELOPMENT

