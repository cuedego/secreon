#!/usr/bin/env python3
"""
Detailed trace of encrypt and decrypt to find the bug.
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.cipher import encrypt, decrypt

# Test secret
SECRET = bytes.fromhex("bb54aac4b89dc868ba37d9cc21b2cece")
IDENTIFIER = 7945
ITERATION_EXP = 0
EXTENDABLE = False
PASSPHRASE = b""

print("=== ENCRYPT ===")
encrypted = encrypt(SECRET, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Encrypted: {encrypted.hex()}")
print()

print("=== DECRYPT ===")
decrypted = decrypt(encrypted, PASSPHRASE, ITERATION_EXP, IDENTIFIER, EXTENDABLE)
print(f"Decrypted: {decrypted.hex()}")
print()

print(f"Match: {decrypted == SECRET}")
