#!/usr/bin/env python3
"""
Test cipher encryption/decryption to see if they are inverses.
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.cipher import encrypt, decrypt

# Test data from vector 1
EXPECTED_SECRET = bytes.fromhex("bb54aac4b89dc868ba37d9cc21b2cece")
ENCRYPTED_IN_SHARE = bytes.fromhex("11bc609d21747c49ba78c0701293e417")
IDENTIFIER = 7945
ITERATION_EXP = 0
EXTENDABLE = False
PASSPHRASE = b""

print("Test 1: Encrypt expected secret and compare with share value")
print(f"Expected secret: {EXPECTED_SECRET.hex()}")
print(f"Encrypted in share: {ENCRYPTED_IN_SHARE.hex()}")
print()

encrypted = encrypt(EXPECTED_SECRET, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Our encryption of expected: {encrypted.hex()}")
print(f"Matches share value: {encrypted == ENCRYPTED_IN_SHARE}")
print()

print("Test 2: Decrypt share value")
decrypted = decrypt(ENCRYPTED_IN_SHARE, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Our decryption of share: {decrypted.hex()}")
print(f"Matches expected: {decrypted == EXPECTED_SECRET}")
print()

print("Test 3: Encrypt then decrypt (round trip)")
encrypted2 = encrypt(EXPECTED_SECRET, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
decrypted2 = decrypt(encrypted2, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Round trip matches: {decrypted2 == EXPECTED_SECRET}")
print(f"Round trip result: {decrypted2.hex()}")
