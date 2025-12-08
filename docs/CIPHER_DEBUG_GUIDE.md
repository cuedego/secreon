# Cipher Implementation Debug Guide

## Current Problem

The Feistel cipher is producing incorrect decryption output. All test vectors that require secret recovery are failing.

## Test Vector 1 (Simplest Case)

**Input Mnemonic:**
```
duckling enlarge academic academic agency result length educator timezone apart evident mast
```

**Share Properties:**
- Identifier: 7945 (0x1f09)
- Iteration Exponent: 0
- Extendable: False
- Member Index: 0
- Member Threshold: 1
- Group Index: 0
- Group Threshold: 1

**Expected Output:**
```
Secret: bb54aac4b89dc868ba37d9cc21b2cece
```

**Our Output:**
```
Secret: 3972a9318cf16a33ee9b0564c5a0bd0b
```

## Debugging Steps Completed

### 1. RS1024 Checksum ✅
- Fixed API mismatch (was passing bytes, should pass bool)
- All checksums now validate correctly
- Polymod returns 1 for valid mnemonics

### 2. Share Parsing ✅
- Identifier extracted correctly: 7945
- All share properties parsed correctly
- Share value extracted: 11bc609d21747c49ba78c0701293e417

### 3. Salt Formation ✅
- Salt: b'shamir\x1f\t' (correctly formed)
- Identifier encoded as big-endian: 0x1f09 → \x1f\x09

### 4. Cipher Structure ✅
- 4 rounds (correct)
- PBKDF2-HMAC-SHA256 (correct)
- Iterations per round: 2500 (correct for exponent=0)
- L/R split (correct)

### 5. Manual Trace of Vector 1
```python
Encrypted: 11bc609d21747c49ba78c0701293e417
Initial L: 11bc609d21747c49
Initial R: ba78c0701293e417

Round 0:
  PBKDF2(salt, R, 2500, 8) → e5d8c46be1e78b38
  New L = ba78c0701293e417
  New R = 11bc609d21747c49 ⊕ e5d8c46be1e78b38 → f46454263091ff71

Round 1:
  PBKDF2(salt, R, 2500, 8) → 86ecd45d9ff6e00a
  New L = f46454263091ff71
  New R = ba78c0701293e417 ⊕ 86ecd45d9ff6e00a → 3c94143dcbc5e41d

Round 2:
  PBKDF2(salt, R, 2500, 8) → cc4640117dd7bb36
  New L = 3c94143dcbc5e41d
  New R = f46454263091ff71 ⊕ cc4640117dd7bb36 → 38201437ed464447

Round 3:
  PBKDF2(salt, R, 2500, 8) → 04b4a80ed2a2d84c
  New L = 38201437ed464447
  New R = 3c94143dcbc5e41d ⊕ 04b4a80ed2a2d84c → 3820143f1f673c51

Final: 38201437ed464447 || 3820143f1f673c51 = 38201437ed4644473820143f1f673c51
Our output: 3972a9318cf16a33ee9b0564c5a0bd0b

WRONG! Why is final assembly wrong?
```

## Suspicious Areas

### 1. Share Value Extraction
**Question:** Is the encrypted master secret the same as the share value?

In `share.py`, we extract:
```python
self.share_value = mnemonic_data[4:20]  # 16 bytes
```

**Need to verify:**
- Is this the encrypted master secret directly?
- Or does it need further processing?
- Check Trezor's `share.py` for comparison

### 2. Identifier Encoding
**Current implementation:**
```python
identifier_bytes = identifier.to_bytes(2, byteorder='big')
salt = b"shamir" + identifier_bytes
```

**Need to verify:**
- Is big-endian correct? (probably yes, matches Trezor)
- Does extendable flag affect salt? (no, it's in the identifier bits)

### 3. XOR Operations
**Current implementation:**
```python
new_right = bytes(a ^ b for a, b in zip(left, f_output))
```

**Need to verify:**
- Byte order of XOR operation
- Are we XORing the correct operands?

### 4. PBKDF2 Usage
**Current implementation:**
```python
f_output = hashlib.pbkdf2_hmac('sha256', salt, right, iterations, dklen=8)
```

**Trezor implementation:**
```python
return hashlib.pbkdf2_hmac("sha256", salt, i_data, iterations, dklen=len(i_data))
```

**WAIT! Trezor uses `dklen=len(i_data)` but we use `dklen=8`**

This might be the bug! If `i_data` (our `right`) is 8 bytes, then it's the same.
But if share value is 16 bytes, then L/R are 8 bytes each, so dklen=8 is correct.

### 5. Final Assembly
**Current implementation:**
```python
# After all rounds
return left + right  # Concatenate to get decrypted value
```

**Manual trace shows wrong final assembly**

The final L/R we compute don't match what we return. This suggests:
- Bug in the cipher loop
- Bug in how we track L/R across rounds
- Bug in return statement

## Next Debugging Steps

### Priority 1: Check Share Value vs Encrypted Master Secret
```python
# In share.py, line ~270
print(f"Share value (hex): {self.share_value.hex()}")
print(f"Length: {len(self.share_value)} bytes")

# In cipher.py
print(f"Cipher input (hex): {encrypted_master_secret.hex()}")
print(f"Length: {len(encrypted_master_secret)} bytes")
```

Verify they are the same!

### Priority 2: Add Detailed Cipher Logging
```python
def decrypt(encrypted_master_secret, passphrase, identifier, extendable, iteration_exponent):
    print(f"\n=== CIPHER DECRYPT ===")
    print(f"Input: {encrypted_master_secret.hex()}")
    print(f"Passphrase: {passphrase!r}")
    print(f"Identifier: {identifier} (0x{identifier:04x})")
    
    # ... existing code ...
    
    left = encrypted_master_secret[:8]
    right = encrypted_master_secret[8:]
    print(f"Initial L: {left.hex()}")
    print(f"Initial R: {right.hex()}")
    
    for round_num in range(4):
        f_output = hashlib.pbkdf2_hmac('sha256', salt, right, iterations, dklen=8)
        print(f"\nRound {round_num}:")
        print(f"  Input R: {right.hex()}")
        print(f"  PBKDF2 output: {f_output.hex()}")
        
        new_right = bytes(a ^ b for a, b in zip(left, f_output))
        print(f"  L XOR F: {new_right.hex()}")
        
        left = right
        right = new_right
        print(f"  New L: {left.hex()}")
        print(f"  New R: {right.hex()}")
    
    result = left + right
    print(f"\nFinal result: {result.hex()}")
    return result
```

### Priority 3: Install Trezor Library for Comparison
```bash
# Create a test venv
python -m venv /tmp/trezor-test
source /tmp/trezor-test/bin/activate
pip install shamir-mnemonic

# Test with their library
python -c "from shamir_mnemonic import shamir; print(shamir.combine_mnemonics([...]))"
```

### Priority 4: Review SLIP-39 Specification
- Re-read the cipher section
- Check for any special cases or edge conditions
- Verify our understanding of the algorithm

## Theories to Test

1. **Theory: Wrong dklen in PBKDF2**
   - Trezor uses `dklen=len(i_data)`
   - We use `dklen=8`
   - If input is 8 bytes, these are the same
   - But verify!

2. **Theory: L/R swap direction wrong**
   - Maybe we should swap before the round, not after?
   - Check Trezor's exact loop structure

3. **Theory: Share value needs processing**
   - Maybe share value isn't the encrypted master secret directly
   - Check if there's a digest or checksum to remove

4. **Theory: Extendable flag affects cipher**
   - Even though it's in the identifier, maybe it affects the algorithm
   - Check Trezor for any conditional logic based on extendable

5. **Theory: Final round doesn't swap**
   - Some Feistel ciphers don't swap on the last round
   - Check SLIP-39 spec

## Files to Review

- `src/slip39/cipher.py` - Our implementation
- Trezor's `cipher.py` - Reference implementation
- `src/slip39/share.py` - Share value extraction
- SLIP-39 spec section on encryption

## Success Criteria

When we fix the bug:
- Vector 1 should output: `bb54aac4b89dc868ba37d9cc21b2cece`
- All 15 valid vectors should pass
- Test should show: 45/45 passed

