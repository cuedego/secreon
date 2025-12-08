#!/usr/bin/env python3
"""
Test vector 20 - 256-bit single share
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39 import combine_mnemonics

MNEMONIC = ["theory painting academic academic armed sweater year military elder discuss acne wildlife boring employer fused large satoshi bundle carbon diagnose anatomy hamster leaves tracks paces beyond phantom capital marvel lips brave detect luck"]
EXPECTED = "989baf9dcaad5b10ca33dfd8cc75e42477025dce88ae83e75a230086a0e00e92"

print("Testing vector 20 (256-bit single share)")
print(f"Expected: {EXPECTED}")

try:
    result = combine_mnemonics(MNEMONIC, b"")
    print(f"Got:      {result.hex()}")
    print(f"Match: {result.hex() == EXPECTED}")
except Exception as e:
    print(f"Error: {e}")
