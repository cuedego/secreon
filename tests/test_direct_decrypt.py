#!/usr/bin/env python3
"""
Test direct decryption of share value (no Shamir recovery needed for single share).
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.cipher import decrypt

# From the test vector
SHARE_VALUE = bytes.fromhex("11bc609d21747c49ba78c0701293e417")
IDENTIFIER = 7945
ITERATION_EXP = 0
EXTENDABLE = False
PASSPHRASE = b""
EXPECTED_SECRET = bytes.fromhex("bb54aac4b89dc868ba37d9cc21b2cece")

print("Direct decryption of share value:")
print(f"Share value: {SHARE_VALUE.hex()}")
print(f"Expected: {EXPECTED_SECRET.hex()}")
print()

result = decrypt(SHARE_VALUE, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Result: {result.hex()}")
print(f"Match: {result == EXPECTED_SECRET}")
