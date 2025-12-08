# SLIP-39 Security Policy & Deployment Checklist

## Security Policy

### Reporting Security Vulnerabilities

If you discover a security vulnerability in secreon, **please do not open a public issue**. Instead:

1. **Email**: Send a detailed report to the maintainers with:
   - Vulnerability description
   - Steps to reproduce
   - Impact assessment
   - Proposed fix (if any)

2. **Timeline**:
   - Maintainers will acknowledge receipt within 24 hours
   - Initial assessment within 7 days
   - Fix and coordinated disclosure within 30 days (if critical) or up to 90 days (if non-critical)

3. **Attribution**:
   - Vulnerability researcher will be credited in the fix commit and release notes (unless anonymity is requested)

4. **Scope**:
   - This policy applies to cryptographic implementation bugs, input validation bypasses, and other security-relevant issues
   - It does not apply to feature requests or general code quality improvements

---

## Deployment Checklist

### Pre-Deployment Phase

#### Environment Setup
- [ ] Python 3.8+ installed on target system
- [ ] No conflicting crypto libraries (secreon uses only stdlib)
- [ ] Internet connectivity for initial installation (or offline package available)
- [ ] Administrator privileges for system-wide installation (if deploying to multiple users)

#### Code Review
- [ ] Security audit checklist reviewed: `docs/SECURITY_AUDIT_CHECKLIST.md`
- [ ] Vulnerability analysis reviewed: `docs/VULNERABILITY_ANALYSIS.md`
- [ ] Code review checklist reviewed: `docs/CODE_REVIEW_CHECKLIST.md`
- [ ] Peer review completed (recommended for critical deployments)
- [ ] Final sign-off from security team

#### Testing
- [ ] Run full test suite: `python3 -m pytest tests/ -v`
  - Expected: 218 tests pass
- [ ] Run property-based tests: `python3 -m pytest tests/test_property_based.py -v`
  - Expected: 2 tests pass (300 randomized examples)
- [ ] Run official vector tests: `python3 -m pytest tests/test_slip39_vectors.py -v`
  - Expected: 1 test passes (45 official vectors)
- [ ] Test on target Python version and platform
- [ ] Performance test (if applicable): Measure time for typical operations
  - `generate_mnemonics(group_threshold=2, groups=[(2,3),(2,3)], secret=32bytes)` should complete in < 1 second

#### Documentation
- [ ] User guide prepared: How to generate, split, combine shares
- [ ] Security limitations documented: Timing side-channels, memory cleanup
- [ ] Deployment instructions prepared: Installation, configuration, operation
- [ ] Troubleshooting guide prepared: Common errors and solutions
- [ ] Glossary prepared: Explain technical terms (group threshold, member threshold, etc.)

---

### Deployment Phase

#### Installation
- [ ] Install secreon from source or package
  ```bash
  # From source:
  cd /path/to/secreon
  python3 -m pip install -e .
  
  # Or from package:
  python3 -m pip install secreon
  ```
- [ ] Verify installation:
  ```bash
  python3 -c "import slip39; print(slip39.__version__)"
  secreon --version
  ```

#### Configuration
- [ ] Set appropriate permissions on secreon directories (if sensitive)
- [ ] (Optional) Configure logging level for errors/warnings
- [ ] (Optional) Set up monitoring for errors in production

#### Initial Testing (Post-Installation)
- [ ] Test CLI commands:
  ```bash
  secreon slip39 generate --help
  secreon slip39 recover --help
  secreon slip39 info --help
  ```
- [ ] Test generate→recover roundtrip (test data, not production):
  ```bash
  secreon slip39 generate --secret-hex "deadbeef" --group-threshold 2 --groups 2-of-3 2-of-3 --output /tmp/shares.txt
  secreon slip39 info /tmp/shares.txt
  secreon slip39 recover /tmp/shares.txt --input-file
  ```
- [ ] Verify shares are generated correctly and recovery works

---

### Post-Deployment Phase

#### Monitoring
- [ ] Monitor for errors in error logs (if logging is enabled)
- [ ] Monitor for unusual CPU usage (PBKDF2 can be slow; expected for high iteration exponents)
- [ ] Monitor for memory usage (no memory leaks expected)
- [ ] Monitor for network activity (secreon is offline-only; any network activity is unexpected)

#### Maintenance
- [ ] Subscribe to security advisories/mailing list
- [ ] Plan for regular security updates
- [ ] Document version in use for compliance/auditing
- [ ] Keep backups of generated shares in secure offline storage

#### User Training
- [ ] Provide training on:
  - How to generate shares
  - How to store shares securely (offline, geographically distributed, etc.)
  - How to recover secrets
  - What to do if shares are compromised
  - Passphrase best practices
- [ ] Conduct dry-run recovery exercises (testing disaster recovery procedures)

---

## Production Deployment Guidelines

### Recommended Deployment Scenarios

#### Scenario 1: Offline Seed Generation (Recommended for Most Users)
**Use Case**: Generate SLIP-39 shares from a master seed for blockchain wallet recovery

**Setup**:
- Air-gapped machine (no network)
- secreon installed from secure media (USB drive, offline package)
- Shares printed or written to offline media

**Security Benefits**:
- No network exposure
- No memory cleanup required (air-gapped system is destroyed after use)
- Timing side-channels are acceptable (air-gapped system)

**Checklist**:
- [ ] Air-gapped machine tested and verified (no network interfaces enabled)
- [ ] secreon installed on air-gapped machine
- [ ] Shares generated and stored offline
- [ ] Machine powered off and destroyed after use (or wiped)

---

#### Scenario 2: Server-Side Share Generation (High-Security Deployments)
**Use Case**: Enterprise key management system, custodial wallet backend

**Setup**:
- Isolated server (no internet, limited physical access)
- secreon installed in secure container or VM
- Hardware security module (HSM) for key storage

**Security Requirements**:
- [ ] Server is hardened (minimal services, strong authentication)
- [ ] Logging is enabled and monitored for errors
- [ ] Memory cleanup is implemented (ctypes + mlock) for sensitive data
- [ ] Rate limiting on share generation (prevent brute-force attacks)
- [ ] Audit logging for all operations (generate, recover, access)
- [ ] Regular security updates applied

**Additional Measures**:
- [ ] Consider C/Rust implementation instead of Python for constant-time operations
- [ ] Use HSM for passphrase verification (if applicable)
- [ ] Implement multi-signature approval for key operations
- [ ] Monitor for timing side-channels (if adversarial environment)

---

#### Scenario 3: Client-Side Integration (Web/Mobile Apps)
**Use Case**: Non-custodial wallet, self-custody tools

**Setup**:
- secreon integrated into client application (Python library or wrapped in JS/Rust)
- Shares generated and stored locally (device storage, iCloud Keychain, etc.)

**Security Considerations**:
- [ ] Review application's secret handling practices
- [ ] Ensure no secrets are logged or transmitted
- [ ] Implement secure storage (encrypted at-rest)
- [ ] Use secreon as-is (Python timing side-channels are low-risk for client use)
- [ ] Regular updates to secreon

---

## Operational Procedures

### Share Generation

```bash
# Generate 2-of-3 groups with 2-of-3 members each
secreon slip39 generate \
  --secret-hex "0123456789abcdef0123456789abcdef" \
  --group-threshold 2 \
  --groups 2-of-3 2-of-3 2-of-3 \
  --passphrase "my strong passphrase" \
  --output /path/to/shares.txt
```

**Operational Notes**:
- Passphrase is required for decryption; store separately from shares
- Shares should be distributed geographically (at least 3 locations)
- Consider splitting shares across multiple people or HSMs
- Document the metadata: group threshold, member threshold, secret length (stored in shares)

---

### Share Recovery

```bash
# Combine 2 out of 3 groups (each with 2 out of 3 members)
secreon slip39 recover \
  --input-file /path/to/share1.txt /path/to/share2.txt \
  --passphrase "my strong passphrase"
```

**Operational Notes**:
- Ensure correct shares are provided (metadata: group threshold, member threshold)
- Passphrase must match the original; wrong passphrase → wrong secret (no integrity check)
- Recovered secret is printed to stdout (redirect to secure location or HSM)
- Consider air-gapping the recovery process for sensitive secrets

---

### Share Info

```bash
# Inspect share properties without combining
secreon slip39 info /path/to/share1.txt
```

**Output**: Group threshold, member threshold, group index, member index, extendable flag, iteration exponent

---

## Contingency Plans

### If Shares Are Lost
- **Impact**: Permanent loss of ability to recover the secret
- **Prevention**: Distribute shares geographically; store redundantly
- **Mitigation**: None (design is threshold-based; below-threshold shares are useless)

### If Shares Are Compromised
- **Impact**: Attacker can recover the secret (if sufficient shares)
- **Prevention**: Distribute shares across secure locations; use high-threshold (3-of-5 or higher)
- **Mitigation**: Regenerate shares with new secret; use high iteration exponent to slow brute-force

### If Passphrase Is Compromised
- **Impact**: Attacker can decrypt shares (if sufficient shares)
- **Prevention**: Use strong, unique passphrase; store separately from shares
- **Mitigation**: Regenerate shares with new passphrase; higher iteration exponent

### If System Is Compromised
- **Impact**: Attacker may recover timing information or access memory
- **Prevention**: Air-gap critical systems; use dedicated hardware
- **Mitigation**: Assume compromise; use emergency key rotation (if applicable)

---

## Compliance & Auditing

### Recommended Logging

Enable logging of:
- [ ] Share generation events (timestamp, group/member config, user)
- [ ] Share recovery events (timestamp, which shares used, user)
- [ ] Errors and exceptions (timestamp, error type, context)
- [ ] Administrative actions (install, update, configuration changes)

**Do NOT log**:
- Secrets, passphrases, or shares
- Sensitive metadata (unless anonymized)

### Retention

- **Logs**: Retain for 1-2 years (compliance requirement varies by jurisdiction)
- **Shares**: Retain indefinitely (or until secret is no longer needed)
- **Audit trail**: Retain alongside shares

### Compliance Standards

Secreon's design aligns with:
- SLIP-39 standard (Shamir's Secret Sharing for SLIP-0039)
- BIP-39 standard (for mnemonic encoding)
- NIST SP 800-132 (PBKDF2 recommendations)
- FIPS 180-4 (SHA-256, HMAC, PBKDF2)

---

## Incident Response

### If a Vulnerability Is Found

1. **Assessment** (immediate):
   - Determine severity (critical, high, medium, low)
   - Estimate impact (how many deployments affected)

2. **Communication** (within 24 hours):
   - Notify all affected users via security advisory
   - Provide temporary mitigations (if any)
   - Estimate fix timeline

3. **Fix & Test** (within 7-30 days):
   - Develop and test fix
   - Verify against test suite
   - Peer review fix

4. **Release** (coordinated):
   - Release patched version
   - Update security advisory with fix details
   - Request users to upgrade

5. **Post-Mortem** (after fix):
   - Document root cause
   - Identify lessons learned
   - Improve processes to prevent similar issues

---

## Appendix: Test Verification

After deployment, run these tests to verify integrity:

```bash
# Full test suite (should pass: 218 tests)
python3 -m pytest tests/ -v

# Official vectors (should pass: 45 vectors in 1 test)
python3 -m pytest tests/test_slip39_vectors.py -v

# Property-based tests (should pass: 2 tests with 300 examples)
python3 -m pytest tests/test_property_based.py -v

# Quick sanity check (generate and recover)
python3 -c "
from slip39 import generate_mnemonics, combine_mnemonics
secret = b'\\x00' * 32
mnemonics = generate_mnemonics(group_threshold=2, groups=[(2,3),(2,3)], master_secret=secret)
shares = mnemonics[0][:2] + mnemonics[1][:2]
recovered = combine_mnemonics(shares, b'')
assert recovered == secret, 'Recovery failed!'
print('✓ Sanity check passed')
"
```

---

**Policy Version**: 1.0
**Last Updated**: December 8, 2025
**Status**: ✓ **ACTIVE**
