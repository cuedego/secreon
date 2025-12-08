# SLIP-39 Support - Requirements Document

## Executive Summary

This document defines requirements for implementing SLIP-39 (Shamir's Secret-Sharing for Mnemonic Codes) support in secreon, enabling:
1. Generation of 24-word seed phrases (master secret)
2. Splitting secrets into shares using SLIP-39 mnemonics
3. Recovery of secrets from SLIP-39 mnemonics

## Context and Background

### Current State (Secreon v1)
Secreon currently implements:
- Classic Shamir's Secret Sharing (SSS) using arithmetic over prime field (2^2203-1)
- Conversion of secrets (strings/files) to integers
- Share generation as (x, y) pairs
- JSON serialization
- KDF support (SHA-256, PBKDF2) for passphrases

### SLIP-39 Overview
SLIP-39 is a standard for hierarchical deterministic wallet backup (BIP-32) using SSS, defined in:
- Specification: https://github.com/satoshilabs/slips/blob/master/slip-0039.md
- Reference Implementation: https://github.com/trezor/python-shamir-mnemonic

**Key features:**
- Mnemonics of 20-33 words (depending on master secret size)
- Fixed wordlist of 1024 words
- Two-level scheme: groups (GT-of-G) and members (Ti-of-Ni)
- RS1024 checksum (Reed-Solomon)
- Master secret encryption with PBKDF2/Feistel network
- Optional passphrase support
- GF(256) for arithmetic (instead of large prime field)

## Requirements

### FR-1: BIP-39 Seed Phrase Generation
**Priority: HIGH**

#### FR-1.1: Generate 24-word BIP-39 Mnemonic
- Secreon must be able to generate a 24-word BIP-39 seed phrase
- Entropy: 256 bits (32 bytes)
- Wordlist: BIP-39 English (2048 words)
- Format: 24 space-separated words
- Checksum: 8 bits (SHA-256 of first 32 bytes)

#### FR-1.2: BIP-39 to Master Secret Conversion
- Convert BIP-39 mnemonic to master secret (entropy)
- Master secret = first 32 bytes of original entropy
- Validate BIP-39 mnemonic checksum
- Support import of existing mnemonics

**Important note:** For wallet compatibility, the master secret used in SLIP-39 must be the **BIP-32 master seed** (not the seed derived via BIP-39 PBKDF2).

### FR-2: SLIP-39 Share Generation
**Priority: HIGH**

#### FR-2.1: Generate SLIP-39 Shares from Master Secret
- Input: master secret (128-256 bits, multiple of 16 bits)
- Output: set of SLIP-39 mnemonics
- Support single-level scheme (1 group) for simple cases
- Support two-level scheme (multiple groups) for advanced cases

#### FR-2.2: Single-Level Scheme (T-of-N)
- Allow creating shares with threshold T and total N
- Validations:
  - 1 ≤ T ≤ N ≤ 16
  - Master secret length ≥ 128 bits and multiple of 16 bits
- Recommended implementation: 1 group with T1=T and N1=N

#### FR-2.3: Two-Level Scheme (GT-of-G with Ti-of-Ni)
- Group threshold (GT): number of groups needed for recovery
- Per group i: member threshold (Ti) and member count (Ni)
- Validations:
  - 1 ≤ GT ≤ G ≤ 16
  - For each group: 1 ≤ Ti ≤ Ni ≤ 16
  - If Ti = 1, then Ni MUST be 1 (avoid 1-of-N with N > 1)

#### FR-2.4: SLIP-39 Mnemonic Format
- Each share is encoded as 20-33 word mnemonic
- Structure (bits):
  - Identifier (15): random identifier common to all shares
  - Extendable flag (1): extendable backup flag
  - Iteration exponent (4): exponent for PBKDF2 (10000×2^e iterations)
  - Group index (4): group index
  - Group threshold (4): GT-1
  - Group count (4): G-1
  - Member index (4): member index in group
  - Member threshold (4): Ti-1
  - Share value (variable): share value with padding
  - Checksum (30): RS1024 checksum
- Wordlist: SLIP-39 wordlist of 1024 words
- Encoding: each 10 bits = 1 word

### FR-3: SLIP-39 Share Recovery
**Priority: HIGH**

#### FR-3.1: Recover Master Secret from SLIP-39 Mnemonics
- Input: set of SLIP-39 mnemonics + optional passphrase
- Output: original master secret
- Validate all shares belong to same backup (same identifier)
- Validate sufficient number of groups and members
- Verify checksum of each mnemonic

#### FR-3.2: Incremental Share Collection
- Allow adding shares incrementally
- Report how many shares/groups are still needed
- Detect invalid or incompatible shares

### FR-4: Encryption and Security
**Priority: HIGH**

#### FR-4.1: Master Secret Encryption
- Use 4-round Feistel cipher with PBKDF2 as round function
- PBKDF2 parameters:
  - PRF: HMAC-SHA256
  - Password: (round_number || passphrase)
  - Salt: ("shamir" || identifier) || R (when ext=0) or just R (when ext=1)
  - Iterations: 2500 × 2^e (where e = iteration exponent)
  - dkLen: n/2 bytes (half the master secret size)

#### FR-4.2: Passphrase Support
- Optional passphrase (printable ASCII, characters 32-126)
- Empty passphrase by default
- No verification of correct passphrase (plausible deniability)

#### FR-4.3: Digest Verification
- For threshold ≥ 2, include shared secret digest
- Digest = first 4 bytes of HMAC-SHA256(key=R, msg=S)
- Allows detection of malicious or incorrect shares

### FR-5: GF(256) Arithmetic
**Priority: HIGH**

#### FR-5.1: Galois Field Operations
- Implement GF(256) using polynomial representation
- Irreducible polynomial: x^8 + x^4 + x^3 + x + 1 (Rijndael)
- Operations: addition (XOR), multiplication, division (multiplicative inverse)
- Pre-compute log/exp tables for efficiency

#### FR-5.2: Secret Splitting on GF(256)
- Apply SSS byte-by-byte over the secret
- For each byte, create polynomial of degree (threshold-1)
- Secret stored at x=255
- Digest stored at x=254 (when threshold ≥ 2)

### FR-6: Checksum and Validation
**Priority: HIGH**

#### FR-6.1: RS1024 Checksum
- Implement Reed-Solomon code over GF(1024)
- Generator polynomial: (x-a)(x-a²)(x-a³) where a is root of x^10 + x^3 + 1
- Length: 3 words (30 bits)
- Customization strings:
  - "shamir" when ext=0
  - "shamir_extendable" when ext=1

#### FR-6.2: Mnemonic Validation
- Validate checksum of each mnemonic
- Validate minimum length (20 words)
- Validate padding bits (must be zeros and ≤ 8 bits)
- Validate parameter consistency between shares

### FR-7: User Interface and CLI
**Priority: MEDIUM**

#### FR-7.1: Generate Command Extensions
```bash
# Generate BIP-39 seed (24 words)
secreon slip39 generate-seed --out seed.txt

# Generate SLIP-39 shares from BIP-39 seed
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 --out shares/

# Generate SLIP-39 shares from hex master secret
secreon slip39 generate --master-secret <hex> --threshold 3 --shares 5 --out shares/

# Advanced scheme (2 groups)
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \
  --group 3 5 \
  --out shares/

# With passphrase
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 \
  --passphrase "my secure passphrase" --out shares/
```

#### FR-7.2: Recover Command
```bash
# Recover from mnemonics
secreon slip39 recover --mnemonics mnemonic1.txt mnemonic2.txt mnemonic3.txt

# Recover from directory
secreon slip39 recover --shares-dir shares/ --passphrase "my secure passphrase"

# Recover interactively
secreon slip39 recover --interactive
```

#### FR-7.3: Display Formats
- Display shares as mnemonics (words)
- Support JSON export for compatibility
- Display share information (group, threshold, etc.)
- Clear warnings about secure share distribution

### FR-8: Compatibility and Interoperability
**Priority: HIGH**

#### FR-8.1: SLIP-39 Standard Compliance
- Implementation 100% compatible with SLIP-39 specification
- Pass all official test vectors
- Interoperable with Trezor, Ledger, and other implementations

#### FR-8.2: Wordlist Management
- Include official SLIP-39 wordlist
- Support word validation
- Support unique 4-letter prefixes

#### FR-8.3: BIP-39 Compatibility
- Include BIP-39 wordlist (English)
- Support bidirectional conversion between BIP-39 and entropy
- **Important:** SLIP-39 and BIP-39 are not directly convertible
  - SLIP-39 uses master seed (entropy)
  - BIP-39 uses seed derived via PBKDF2

### FR-9: Testing and Quality
**Priority: HIGH**

#### FR-9.1: Unit Tests
- Tests for all GF(256) operations
- Encryption/decryption tests
- Share generation and recovery tests
- Validation and checksum tests

#### FR-9.2: Integration Tests
- Official SLIP-39 test vectors
- Interoperability tests with python-shamir-mnemonic
- Edge case tests (threshold=1, maximum shares, etc.)

#### FR-9.3: Property-Based Tests
- Any valid set of T shares recovers the secret
- Fewer than T shares doesn't leak information
- Shares from different groups don't work alone

### FR-10: Documentation
**Priority: MEDIUM**

#### FR-10.1: User Documentation
- Step-by-step tutorial for creating backup
- Use case examples (personal, family, business)
- Best practices for share distribution
- Security and trade-offs explanation

#### FR-10.2: Technical Documentation
- Architecture documentation
- API reference
- Algorithms and data structures
- Differences between classic SSS and SLIP-39

## Non-Functional Requirements

### NFR-1: Performance
- Share generation: < 5 seconds for 256-bit master secret
- Share recovery: < 10 seconds (due to PBKDF2)
- Time dominated by PBKDF2 (10000+ iterations)

### NFR-2: Security
- Use cryptographically secure randomness source (`secrets` module)
- Never log or display master secret without explicit confirmation
- Warnings about secure share distribution
- Support memory zeroing where possible (Python limitation)

### NFR-3: Usability
- Clear and intuitive CLI interface
- Descriptive error messages
- Input validation before expensive operations
- Batch operation support

### NFR-4: Maintainability
- Modular and well-organized code
- Complete type hints
- Tests with good coverage (>80%)
- Inline documentation

## Technical Architecture

### Module Structure
```
secreon/
├── src/
│   ├── sss.py              # Existing SSS implementation
│   ├── slip39/
│   │   ├── __init__.py
│   │   ├── wordlist.py     # SLIP-39 wordlist
│   │   ├── bip39.py        # BIP-39 wordlist and operations
│   │   ├── gf256.py        # GF(256) arithmetic
│   │   ├── rs1024.py       # RS1024 checksum
│   │   ├── cipher.py       # Feistel cipher / encryption
│   │   ├── share.py        # Share class and encoding/decoding
│   │   ├── shamir.py       # SLIP-39 SSS implementation
│   │   └── cli.py          # CLI commands for SLIP-39
│   └── ...
├── tests/
│   ├── test_sss.py         # Existing tests
│   ├── slip39/
│   │   ├── test_gf256.py
│   │   ├── test_rs1024.py
│   │   ├── test_cipher.py
│   │   ├── test_shamir.py
│   │   └── test_vectors.py # Official SLIP-39 test vectors
│   └── ...
└── ...
```

### Dependencies
- **No external dependencies** for core functionality (stdlib only)
- Optional: `click` for advanced CLI (already used in python-shamir-mnemonic)
- For tests: `pytest`, `hypothesis` (property-based testing)

## Migration and Compatibility

### Backward Compatibility
- Existing secreon continues working without changes
- SLIP-39 is added as new subcommand
- JSON format of classic shares remains unchanged

### Forward Compatibility
- Implement ext=1 (extendable backup flag) by default
- Support future SLIP-39 versions via ext flag

## Risk Assessment

### High Risk Items
1. **SLIP-39 specification complexity**: many details, easy to make mistakes
   - Mitigation: incremental implementation, test vectors, code review

2. **Interoperability**: incompatibility with other implementations
   - Mitigation: cross-testing with python-shamir-mnemonic, Trezor

3. **Cryptographic security**: bugs can compromise secrets
   - Mitigation: code audit, extensive testing, use reference implementation as guide

### Medium Risk Items
1. **PBKDF2 performance**: may be slow on limited hardware
   - Mitigation: allow iteration exponent configuration

2. **Complex UX**: two-level scheme may confuse users
   - Mitigation: clear documentation, examples, simple mode by default

## Success Criteria

### Minimum Viable Product (MVP)
1. ✅ Geração de BIP-39 seed de 24 palavras
2. ✅ Conversão BIP-39 → master secret
3. ✅ Geração de SLIP-39 shares (esquema de nível único)
4. ✅ Recuperação de master secret de SLIP-39 shares
5. ✅ Passar test vectors oficiais básicos
6. ✅ CLI funcional para operações básicas

### Full Feature Set
1. ✅ Two-level scheme support (groups)
2. ✅ Passphrase support
3. ✅ Iteration exponent configuration
4. ✅ Extendable backup flag
5. ✅ Complete interoperability with other implementations
6. ✅ Complete documentation
7. ✅ Test coverage >80%

## References

1. **SLIP-39 Specification**: https://github.com/satoshilabs/slips/blob/master/slip-0039.md
2. **Reference Implementation**: https://github.com/trezor/python-shamir-mnemonic
3. **BIP-39**: https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
4. **BIP-32**: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
5. **Test Vectors**: https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json
6. **SLIP-39 Wordlist**: https://github.com/satoshilabs/slips/blob/master/slip-0039/wordlist.txt

## Glossary

- **Master Secret (MS)**: O secret original a ser protegido (128-256 bits)
- **Encrypted Master Secret (EMS)**: Master secret após criptografia com Feistel cipher
- **Share**: Um único ponto (x, y) no esquema SSS
- **Mnemonic**: Representação de um share como palavras
- **Group**: Conjunto de member shares no esquema de dois níveis
- **Threshold**: Número mínimo de shares necessárias para recuperação
- **GF(256)**: Galois Field com 256 elementos, usado para aritmética
- **RS1024**: Reed-Solomon code sobre GF(1024) para checksum
- **Identifier**: ID aleatório de 15 bits comum a todas as shares de um backup

## Appendix A: Example Scenarios

### Scenario 1: Personal Backup (Simple)
**Goal**: Protect a personal wallet with redundancy

**Setup**:
- Generate 24-word BIP-39 seed
- Create 3-of-5 SLIP-39 shares
- Store: 1 at home, 1 at work, 1 in safe, 2 with friends

**Commands**:
```bash
secreon slip39 generate-seed --out seed.txt
secreon slip39 generate --seed-file seed.txt --threshold 3 --shares 5 --out shares/
```

### Scenario 2: Family Backup (Two-Level)
**Goal**: You can recover alone OR your family can recover together

**Setup**:
- Group 1: 2-of-2 (your personal shares)
- Group 2: 3-of-5 (family shares)
- Group threshold: 1 (any complete group)

**Commands**:
```bash
secreon slip39 generate --seed-file seed.txt \
  --group-threshold 1 \
  --group 2 2 \
  --group 3 5 \
  --out shares/
```

### Scenario 3: Corporate Backup (Advanced)
**Goal**: Require approval from multiple departments

**Setup**:
- Group 1: 2-of-3 (directors)
- Group 2: 3-of-5 (technical team)
- Group 3: 2-of-3 (compliance)
- Group threshold: 2 (two departments must agree)

**Commands**:
```bash
secreon slip39 generate --master-secret <hex> \
  --group-threshold 2 \
  --group 2 3 \
  --group 3 5 \
  --group 2 3 \
  --out shares/
```

## Appendix B: Migration Path from Legacy SSS

For existing secreon users using classic SSS:

1. **No direct conversion**: Classic SSS and SLIP-39 are incompatible
2. **Recommendation**: 
   - Recover original secret using old shares
   - Generate new SLIP-39 shares from the secret
   - Securely destroy old shares
3. **Coexistence**: both systems can coexist in secreon

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | AI Assistant | Initial requirements document |

---
**Document Status**: DRAFT
**Last Update**: 2025-12-06

