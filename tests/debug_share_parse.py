#!/usr/bin/env python3
"""
Debug what values are being extracted from the mnemonic.
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.share import Share

# Test vector 1 mnemonic
MNEMONIC = "duckling enlarge academic academic agency result length solution fridge kidney coal piece deal husband erode duke ajar critical decision keyboard"

print("Parsing mnemonic...")
share = Share.from_mnemonic(MNEMONIC)

print(f"Identifier: {share.identifier} (0x{share.identifier:04x})")
print(f"Extendable: {share.extendable}")
print(f"Iteration exponent: {share.iteration_exponent}")
print(f"Group index: {share.group_index}")
print(f"Group threshold: {share.group_threshold}")
print(f"Group count: {share.group_count}")
print(f"Index: {share.index}")
print(f"Member threshold: {share.member_threshold}")
print(f"Share value length: {len(share.value)}")
print(f"Share value: {share.value.hex()}")
