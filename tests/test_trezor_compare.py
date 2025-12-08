#!/usr/bin/env python3
"""
Compare our SLIP-39 implementation with Trezor's reference implementation.
This script tests the first vector.
"""

# Test vector 1 from official test vectors
MNEMONIC = [
    "duckling enlarge academic academic agency result length solution fridge kidney coal piece deal husband erode duke ajar critical decision keyboard"
]
EXPECTED_SECRET = "bb54aac4b89dc868ba37d9cc21b2cece"

print("Testing vector 1:")
print(f"Mnemonic: {MNEMONIC[0]}")
print(f"Expected secret: {EXPECTED_SECRET}")
print()

# Try with Trezor's library
print("=== TREZOR LIBRARY ===")
try:
    from shamir_mnemonic import shamir
    result = shamir.combine_mnemonics(MNEMONIC)
    print(f"Result: {result.hex()}")
    print(f"Match: {result.hex() == EXPECTED_SECRET}")
except ImportError:
    print("shamir-mnemonic not installed")
    print("Install with: pip install shamir-mnemonic")
except Exception as e:
    print(f"Error: {e}")

print()

# Try with our library
print("=== OUR LIBRARY ===")
try:
    import sys
    sys.path.insert(0, '/home/cuedego/secreon/src')
    from slip39 import combine_mnemonics
    
    result = combine_mnemonics(MNEMONIC)
    print(f"Result: {result.hex()}")
    print(f"Match: {result.hex() == EXPECTED_SECRET}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
