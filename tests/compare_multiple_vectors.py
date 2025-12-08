#!/usr/bin/env python3
"""
Test multiple vectors with Trezor's library to see if test vectors are wrong.
"""
import json
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from shamir_mnemonic import shamir as trezor_shamir
from slip39 import combine_mnemonics as our_combine

# Load test vectors
with open('tests/slip39-vectors.json') as f:
    vectors = json.load(f)

print("Testing first 5 valid vectors with both libraries:\n")

valid_count = 0
for i, vector in enumerate(vectors):
    desc, mnemonics, expected_secret, _ = vector
    
    # Skip invalid vectors
    if "Invalid" in desc or "invalid" in desc:
        continue
    
    valid_count += 1
    if valid_count > 5:
        break
    
    print(f"Vector {i}: {desc[:60]}...")
    print(f"Expected: {expected_secret}")
    
    # Test with Trezor
    try:
        trezor_result = trezor_shamir.combine_mnemonics(mnemonics)
        print(f"Trezor:   {trezor_result.hex()}")
        print(f"Match:    {trezor_result.hex() == expected_secret}")
    except Exception as e:
        print(f"Trezor error: {e}")
    
    # Test with ours
    try:
        our_result = our_combine(mnemonics)
        print(f"Ours:     {our_result.hex()}")
        print(f"Match:    {our_result.hex() == expected_secret}")
    except Exception as e:
        print(f"Our error: {e}")
    
    # Compare Trezor vs ours
    try:
        if trezor_result == our_result:
            print("✓ Trezor and our implementation AGREE")
        else:
            print("✗ Trezor and our implementation DISAGREE")
    except:
        pass
    
    print()
