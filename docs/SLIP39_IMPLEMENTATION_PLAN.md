# SLIP-39 Implementation Plan

## Overview

This document presents a detailed plan, divided into incremental steps, to implement SLIP-39 support in secreon. Each step is independent and testable, allowing iterative development with functional deliverables.

---

## PHASE 1: Foundations and Infrastructure
**Objective**: Establish the mathematical foundation and necessary data structures

### Step 1.1: GF(256) Arithmetic Implementation
**Estimated duration**: 2-3 days
**Priority**: CRITICAL

**Tasks**:
1. Create module `src/slip39/gf256.py`
2. Implement basic GF(256) operations:
   - Addition (XOR)
   - Multiplication using Rijndael polynomial
   - Multiplicative inverse (for division)
3. Pre-compute log/exp tables for optimization
4. Implement Lagrange interpolation over GF(256)

**Deliverables**:
- [x] `gf256.py` with functions: `add()`, `multiply()`, `divide()`, `interpolate()`
- [x] Unit tests for all operations
- [x] Performance benchmark (should be fast, <1ms for typical operations)

**Acceptance Criteria**:
- [x] All tests pass (35 tests)
- [x] Multiplication/division correct according to AES table
- [x] Interpolation recovers secret from valid shares

**Dependencies**: None
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 1.2: RS1024 Checksum Implementation
**Estimated duration**: 2 days
**Priority**: CRITICAL

**Tasks**:
1. Create module `src/slip39/rs1024.py`
2. Implement generator polynomial for RS1024
3. Implement checksum functions:
   - `create_checksum(data, customization_string)`
   - `verify_checksum(data, customization_string)`
4. Support customization strings: "shamir" and "shamir_extendable"

**Deliverables**:
- [x] `rs1024.py` with checksum functions
- [x] Tests with known values from specification
- [x] Error detection verification (up to 3 words)

**Acceptance Criteria**:
- [x] Checksum compatible with reference implementation
- [x] Detects up to 3 errors with 100% certainty (verified with 30,000 trials)
- [x] Probability <1e-9 of failing to detect more errors

**Dependencies**: None
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 1.3: Wordlist Management
**Estimated duration**: 1 day
**Priority**: HIGH

**Tasks**:
1. Create module `src/slip39/wordlist.py`
2. Include official SLIP-39 wordlist (1024 words)
3. Implement conversions:
   - Words → indices
   - Indices → words
   - Integer → list of indices
   - List of indices → integer

**Deliverables**:
- [x] `wordlist.py` with SLIP-39 wordlist
- [x] Conversion functions
- [x] Validation of unique 4-letter prefixes
- [x] Bidirectional conversion tests

**Acceptance Criteria**:
- [x] Wordlist identical to official specification (1024 words)
- [x] All 4-letter prefixes are unique
- [x] Bidirectional conversions without loss (45 tests)

**Dependencies**: None
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 1.4: BIP-39 Support
**Estimated duration**: 1-2 days
**Priority**: HIGH

**Tasks**:
1. Create module `src/slip39/bip39.py`
2. Include BIP-39 wordlist (English, 2048 words)
3. Implement mnemonic generation:
   - Generate 256 bits of entropy
   - Calculate checksum (SHA-256)
   - Convert to 24 words
4. Implement mnemonic validation and conversion to entropy

**Deliverables**:
- [x] `bip39.py` with generation and validation functions
- [x] Tests with BIP-39 test vectors
- [x] Function to generate random 24-word seed

**Acceptance Criteria**:
- [x] Generation compatible with BIP-39
- [x] Checksum validation works
- [x] Conversion mnemonic → entropy → mnemonic preserves data

**Dependencies**: None
**Status**: ✅ COMPLETE (2025-12-07)

---

## PHASE 2: Cryptography and Secret Sharing
**Objective**: Implement the core of SLIP-39

### Step 2.1: Feistel Cipher Implementation
**Estimated duration**: 2-3 days
**Priority**: CRITICAL

**Tasks**:
1. Create module `src/slip39/cipher.py`
2. Implement round function using PBKDF2-HMAC-SHA256
3. Implement encryption (4 Feistel rounds)
4. Implement decryption (4 reverse rounds)
5. Support salt customization (ext flag)

**Deliverables**:
- [x] `cipher.py` with `encrypt()` and `decrypt()` functions
- [x] Round-trip tests (encrypt → decrypt = identity)
- [x] Tests with different iteration exponents
- [x] Tests with/without extendable flag

**Acceptance Criteria**:
- [x] Encrypt/decrypt are perfect inverses
- [x] Compatible with python-shamir-mnemonic
- [x] Acceptable performance (~5-10s for e=1)

**Dependencies**: None (uses stdlib hashlib, hmac)
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 2.2: SLIP-39 Share Data Structure
**Estimated duration**: 2 days
**Priority**: CRITICAL

**Tasks**:
1. Create module `src/slip39/share.py`
2. Define `Share` class with all fields:
   - identifier, extendable, iteration_exponent
   - group_index, group_threshold, group_count
   - member_index, member_threshold
   - share_value
3. Implement encoding: Share → mnemonic
4. Implement decoding: mnemonic → Share
5. Implement validations

**Deliverables**:
- [x] `share.py` with `Share` class
- [x] Methods `to_mnemonic()` and `from_mnemonic()`
- [x] Encoding/decoding round-trip tests
- [x] Validation of all fields

**Acceptance Criteria**:
- [x] Share → mnemonic → Share preserves data
- [x] Checksum validated on decode
- [x] Format compatible with specification

**Dependencies**: 1.2 (RS1024), 1.3 (Wordlist)
**Status**: ✅ COMPLETE (2025-12-07)
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 2.3: SLIP-39 Core SSS Implementation
**Estimated duration**: 3-4 days
**Priority**: CRITICAL

**Tasks**:
1. Create module `src/slip39/shamir.py`
2. Implement split over GF(256):
   - `split_secret(threshold, count, secret)` → shares
   - Byte-by-byte SSS
   - Include digest when threshold ≥ 2
3. Implement recover:
   - `recover_secret(shares)` → secret
   - Validate digest
   - Interpolation over GF(256)
4. Implement two-level scheme:
   - `split_ems(group_threshold, groups, ems)` → grouped shares
   - `recover_ems(grouped_shares)` → ems

**Deliverables**:
- [x] `shamir.py` with split/recover functions
- [x] `EncryptedMasterSecret` class
- [x] Split/recover round-trip tests
- [x] Threshold tests (T shares work, T-1 fail)
- [x] Two-level scheme tests

**Acceptance Criteria**:
- [x] Any set of T shares recovers secret
- [x] T-1 shares do not recover secret
- [x] Digest detects invalid shares
- [x] Compatible with python-shamir-mnemonic

**Dependencies**: 1.1 (GF256), 2.1 (Cipher), 2.2 (Share)
**Status**: ✅ COMPLETE (2025-12-07)

---

### Step 2.4: High-Level API
**Estimated duration**: 2 days
**Priority**: HIGH

**Tasks**:
1. Implement high-level functions in `shamir.py`:
   - `generate_mnemonics(group_threshold, groups, master_secret, passphrase, ...)`
   - `combine_mnemonics(mnemonics, passphrase)`
2. Implement input validations
3. Implement random identifier generation
4. User-friendly error handling

**Deliverables**:
- [ ] Documented high-level API
- [ ] End-to-end tests (generate → combine)
- [ ] Parameter validation
- [ ] Clear error messages

**Acceptance Criteria**:
- Simple and intuitive API
- Validations prevent incorrect usage
- Compatible with official test vectors

**Dependencies**: 2.3 (Core SSS)

---

## PHASE 3: CLI Integration and User Experience
**Objective**: Make functionality accessible via command line

### Step 3.1: CLI - Generate Seed Command
**Estimated duration**: 1 day
**Priority**: HIGH

**Tasks**:
1. Create `src/slip39/cli.py` or extend `secreon.py`
2. Implement `slip39 generate-seed` command:
   - Generate BIP-39 mnemonic of 24 words
   - Save to file or display
   - Option to provide custom entropy

**Deliverables**:
- [ ] Command `secreon slip39 generate-seed`
- [ ] Options: `--out`, `--entropy`
- [ ] Warnings about storing seed securely

**Acceptance Criteria**:
- Generates valid BIP-39 seed
- Saves correctly to file
- Clear and intuitive UI

**Dependencies**: 1.4 (BIP-39)

---

### Step 3.2: CLI - Generate Shares Command
**Estimated duration**: 2-3 days
**Priority**: CRITICAL

**Tasks**:
1. Implement `slip39 generate` command:
   - Accept master secret from multiple sources:
     - `--seed-file` (BIP-39 mnemonic)
     - `--master-secret` (hex string)
   - Simple scheme: `--threshold`, `--shares`
   - Advanced scheme: `--group-threshold`, `--group` (multiple)
   - Options: `--passphrase`, `--iteration-exponent`, `--extendable`
2. Display shares as mnemonics
3. Save to individual files or JSON

**Deliverables**:
- [ ] Command `secreon slip39 generate`
- [ ] Support for simple and advanced schemes
- [ ] Readable and organized output
- [ ] Option to split shares into separate files

**Acceptance Criteria**:
- Generates valid shares from all sources
- Intuitive UI for both schemes
- Well-organized output files
- Warnings about secure distribution

**Dependencies**: 2.4 (High-Level API), 3.1 (Generate Seed)

---

### Step 3.3: CLI - Recover Command
**Estimated duration**: 2 days
**Priority**: CRITICAL

**Tasks**:
1. Implement `slip39 recover` command:
   - Accept mnemonics from multiple sources:
     - Individual files
     - Directory with shares
     - Interactive input
   - Option `--passphrase`
   - Validate shares before attempting recovery
2. Report progress (how many shares/groups are missing)
3. Display master secret or save to file

**Deliverables**:
- [ ] Command `secreon slip39 recover`
- [ ] Multiple input methods
- [ ] Progress feedback
- [ ] Validation and clear error messages

**Acceptance Criteria**:
- Recovers master secret from valid shares
- Detects insufficient or invalid shares
- Clear UI with progress feedback
- Does not display secret by default (`--show` option)

**Dependencies**: 2.4 (High-Level API)

---

### Step 3.4: CLI - Utility Commands
**Estimated duration**: 1-2 days
**Priority**: MEDIUM

**Tasks**:
1. Implement `slip39 info` command:
   - Display information about a share
   - Show parameters (threshold, groups, etc.)
   - Do not reveal share value
2. Implement `slip39 validate` command:
   - Validate mnemonics without recovering secret
   - Verify checksums
   - Check compatibility between shares

**Deliverables**:
- [ ] Command `secreon slip39 info`
- [ ] Command `secreon slip39 validate`
- [ ] Formatted and readable output

**Acceptance Criteria**:
- Displays useful information without compromising security
- Validation detects common problems
- Helps users organize shares

**Dependencies**: 2.2 (Share)

---

## PHASE 4: Testing and Quality
**Objective**: Ensure correctness, security, and interoperability

### Step 4.1: Official Test Vectors
**Estimated duration**: 2 days
**Priority**: CRITICAL

**Tasks**:
1. Download official test vectors: vectors.json
2. Create `tests/slip39/test_vectors.py`
3. Implement tests for all cases:
   - Valid mnemonics (various sizes)
   - Invalid mnemonics (various error types)
   - Group sharing
   - Passphrases
   - Extendable backups

**Deliverables**:
- [ ] `test_vectors.py` with all official cases
- [ ] 100% of test vectors pass
- [ ] Compatibility report

**Acceptance Criteria**:
- All valid test vectors generate expected result
- All invalid test vectors are detected
- 100% compatibility with specification

**Dependencies**: 2.4 (High-Level API)

---

### Step 4.2: Cross-Implementation Testing
**Estimated duration**: 2-3 days
**Priority**: HIGH

**Tasks**:
1. Create interoperability tests with python-shamir-mnemonic:
   - Generate shares in secreon, recover with python-shamir-mnemonic
   - Generate shares in python-shamir-mnemonic, recover with secreon
2. Test multiple scenarios:
   - Different secret sizes
   - Different thresholds
   - With/without passphrase
   - Multiple groups
3. Document any incompatibilities

**Deliverables**:
- [ ] Cross-testing script
- [ ] Compatibility report
- [ ] Fix of incompatibilities found

**Acceptance Criteria**:
- 100% interoperability with python-shamir-mnemonic
- Shares are interchangeable between implementations
- Documentation of differences (if any)

**Dependencies**: 2.4 (High-Level API), 4.1 (Test Vectors)

---

### Step 4.3: Property-Based Testing
**Estimated duration**: 2 days
**Priority**: MEDIUM

**Tasks**:
1. Use `hypothesis` for property-based testing
2. Test fundamental properties:
   - Round-trip: generate → recover = identity
   - Threshold: T shares work, T-1 don't
   - Security: random shares don't reveal information
   - Independence: change in 1 share doesn't affect others
3. Test automatically generated edge cases

**Deliverables**:
- [ ] Property-based tests with `hypothesis`
- [ ] Coverage of fundamental properties
- [ ] Report of edge cases found

**Acceptance Criteria**:
- All properties verified
- No edge case breaks the system
- High confidence in correctness

**Dependencies**: 2.4 (High-Level API)

---

### Step 4.4: Security Audit Preparation
**Estimated duration**: 2-3 days
**Priority**: HIGH

**Tasks**:
1. Security-focused code review:
   - Correct use of randomness (secrets.token_bytes)
   - No secret leaks in logs/errors
   - Complete input validation
   - Side-channel considerations (Python limitation)
2. Verify handling of edge cases
3. Document security decisions
4. Prepare checklist for external audit

**Deliverables**:
- [ ] Security code review report
- [ ] List of improvements implemented
- [ ] Security decision documentation
- [ ] Checklist for external audit

**Acceptance Criteria**:
- No obvious vulnerabilities found
- Follow cryptography best practices
- Code ready for audit

**Dependencies**: All previous steps

---

## PHASE 5: Documentation and Release
**Objective**: Prepare for production and public use

### Step 5.1: User Documentation
**Estimated duration**: 2-3 days
**Priority**: HIGH

**Tasks**:
1. Write complete tutorial in README
2. Create quick start guide
3. Document common use cases
4. Write FAQ
5. Document differences between classic SSS and SLIP-39
6. Security best practices

**Deliverables**:
- [ ] Updated README tutorial
- [ ] Quick start guide
- [ ] Use case documentation
- [ ] FAQ
- [ ] Security guide

**Acceptance Criteria**:
- Clear and comprehensible documentation
- Cover main use cases
- Appropriate security warnings

**Dependencies**: 3.3 (Complete CLI)

---

### Step 5.2: Technical Documentation
**Estimated duration**: 2 days
**Priority**: MEDIUM

**Tasks**:
1. Update docs/TECHNICAL.md
2. Document SLIP-39 architecture
3. Document APIs of each module
4. Create flow diagrams
5. Document design decisions

**Deliverables**:
- [ ] Updated TECHNICAL.md
- [ ] Architecture documentation
- [ ] Complete API reference
- [ ] Flow diagrams

**Acceptance Criteria**:
- Developers can understand code
- Well-documented APIs
- Justified design decisions

**Dependencies**: All previous phases

---

### Step 5.3: Release Preparation
**Estimated duration**: 1-2 days
**Priority**: HIGH

**Tasks**:
1. Update CHANGELOG.md
2. Create RELEASE_NOTES for SLIP-39 version
3. Verify test coverage
4. Run linters and formatters
5. Prepare release notes for GitHub

**Deliverables**:
- [ ] Updated CHANGELOG
- [ ] Specific RELEASE_NOTES
- [ ] Test coverage >80%
- [ ] Formatted code without warnings

**Acceptance Criteria**:
- Complete and clear changelog
- Tests with good coverage
- Clean code without warnings

**Dependencies**: 5.1 (User Docs), 5.2 (Tech Docs)

---

### Step 5.4: Examples and Demos
**Estimated duration**: 1 day
**Priority**: LOW

**Tasks**:
1. Create practical examples in examples/
2. Demo script for common cases
3. Example of usage as Python library
4. Video or GIF demonstrating CLI

**Deliverables**:
- [ ] Example scripts
- [ ] Demo script
- [ ] Library usage example
- [ ] Visual material (optional)

**Acceptance Criteria**:
- Examples work out-of-the-box
- Cover main use cases
- Easy to follow for beginners

**Dependencies**: 5.1 (User Docs)

---

## Total Time Estimate

### By Phase:
- **Phase 1** (Foundations): 6-8 days
- **Phase 2** (Core SSS): 9-13 days
- **Phase 3** (CLI): 6-8 days
- **Phase 4** (Testing): 8-10 days
- **Phase 5** (Documentation): 6-8 days

### Total: 35-47 days of development

### With dedication:
- **Full-time** (8h/day): 5-6 weeks
- **Part-time** (4h/day): 10-12 weeks
- **Casual** (2h/day): 20-24 weeks

---

## Prioritization for MVP

If the goal is to deliver a functional MVP quickly, the following order is recommended:

### MVP Path (2-3 weeks full-time):
1. ✅ **Step 1.1**: GF(256) - CRITICAL
2. ✅ **Step 1.2**: RS1024 - CRITICAL
3. ✅ **Step 1.3**: Wordlist - CRITICAL
4. ✅ **Step 1.4**: BIP-39 - HIGH
5. ✅ **Step 2.1**: Cipher - CRITICAL
6. ✅ **Step 2.2**: Share - CRITICAL
7. ✅ **Step 2.3**: Core SSS - CRITICAL
8. ✅ **Step 2.4**: High-Level API - HIGH
9. ✅ **Step 3.1**: Generate Seed CLI - HIGH
10. ✅ **Step 3.2**: Generate Shares CLI - CRITICAL
11. ✅ **Step 3.3**: Recover CLI - CRITICAL
12. ✅ **Step 4.1**: Test Vectors - CRITICAL
13. ✅ **Step 5.1**: User Docs (basic) - HIGH

The rest can be added iteratively after the MVP.

---

## Risks and Mitigations

### Risk 1: Specification Complexity
**Probability**: High | **Impact**: High

**Mitigation**:
- Incremental implementation with tests at each step
- Use python-shamir-mnemonic as reference
- Official test vectors from the beginning
- Detailed code review

### Risk 2: Cryptography Bugs
**Probability**: Medium | **Impact**: Critical

**Mitigation**:
- Follow reference implementation faithfully
- Extensive testing (unit, integration, property-based)
- Cross-implementation testing
- Security audit before release

### Risk 3: Unsatisfactory Performance
**Probability**: Low | **Impact**: Medium

**Mitigation**:
- Pre-compute tables (log/exp for GF256)
- Allow iteration exponent configuration
- Benchmarking at each step
- Optimizations after functional MVP

### Risk 4: Incompatibility with Other Implementations
**Probability**: Medium | **Impact**: High

**Mitigation**:
- Frequent cross-testing
- Follow specification rigorously
- Use same test vectors
- Validation with multiple implementations (Trezor, Ledger, etc.)

---

## Validation Checkpoints

### Checkpoint 1: After Phase 1
**Validate**: Mathematical infrastructure works
- [ ] GF(256) passes arithmetic tests
- [ ] RS1024 detects errors correctly
- [ ] Wordlists complete and correct

### Checkpoint 2: After Phase 2
**Validate**: Core SSS works
- [ ] Generate → recover works (round-trip)
- [ ] Threshold respected (T ok, T-1 fails)
- [ ] Digest detects invalid shares

### Checkpoint 3: After Phase 3
**Validate**: Functional CLI
- [ ] User can generate seed
- [ ] User can create shares
- [ ] User can recover secret

### Checkpoint 4: After Phase 4
**Validate**: Quality and compatibility
- [ ] All official test vectors pass
- [ ] Interoperable with python-shamir-mnemonic
- [ ] Property tests pass

### Checkpoint 5: After Phase 5
**Validate**: Ready for release
- [ ] Complete documentation
- [ ] Clean and well-organized code
- [ ] Functional examples

---

## Final Success Criteria

### Must Have (Minimum Requirements):
- ✅ Generation of BIP-39 seed with 24 words
- ✅ Conversion BIP-39 → master secret
- ✅ Generation of SLIP-39 shares (simple T-of-N scheme)
- ✅ Recovery of master secret from shares
- ✅ Pass all basic official test vectors
- ✅ Functional CLI for basic operations
- ✅ Usage documentation

### Should Have (Highly Desirable):
- ✅ Two-level scheme (groups)
- ✅ Passphrase support
- ✅ Interoperability with python-shamir-mnemonic
- ✅ Property-based tests
- ✅ Complete technical documentation

### Nice to Have (Optional):
- ⭕ Utility commands (info, validate)
- ⭕ Examples and demos
- ⭕ Visual material
- ⭕ External security audit

---

## Required Resources

### Development Tools:
- Python 3.8+
- pytest (testing)
- hypothesis (property-based testing)
- mypy (type checking)
- black/ruff (formatting)

### External Resources:
- SLIP-39 specification
- python-shamir-mnemonic (reference and cross-testing)
- Official test vectors
- BIP-39/BIP-32 specifications

### Hardware:
- Development machine (any modern PC works)
- Optional: Hardware wallet for interoperability testing

---

## Immediate Next Steps

### To Start Development:

1. **Initial Setup** (30 min):
   ```bash
   mkdir -p src/slip39 tests/slip39
   touch src/slip39/__init__.py tests/slip39/__init__.py
   pip install pytest hypothesis
   ```

2. **Start with Step 1.1** (GF256):
   - Create `src/slip39/gf256.py`
   - Implement basic operations
   - Create `tests/slip39/test_gf256.py`
   - Pass all tests

3. **Iterate through Steps**:
   - Complete one step at a time
   - Test exhaustively before proceeding
   - Document as you go

4. **Regular Checkpoints**:
   - Validate after each phase
   - Adjust plan if necessary
   - Keep stakeholders informed

---

## Conclusion

This plan provides a detailed roadmap to implement SLIP-39 in secreon in an incremental and testable manner. Each step is independent and produces verifiable artifacts, allowing iterative development with functional deliverables.

The MVP can be delivered in 2-3 weeks with full-time dedication, and the complete implementation in 5-6 weeks. Prioritization by phases allows delivering value quickly while building a solid foundation for advanced features.

---

**Last Updated**: 2025-12-06  
**Status**: READY FOR DEVELOPMENT

