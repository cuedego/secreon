#!/usr/bin/env python3
"""
Manually trace mnemonic to share value extraction.
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39 import wordlist

MNEMONIC = "duckling enlarge academic academic agency result length solution fridge kidney coal piece deal husband erode duke ajar critical decision keyboard"

words = MNEMONIC.split()
print(f"Total words: {len(words)}")
print()

# Convert to indices
indices = wordlist.mnemonic_to_indices(MNEMONIC)
print(f"Word indices ({len(indices)} words):")
for i, idx in enumerate(indices):
    print(f"  {i:2d}: {idx:4d} '{words[i]}'")
print()

# According to SLIP-39:
# - Words 0-1: ID + iteration exponent (2 words = 20 bits)
# - Words 2-3: Share parameters (2 words = 20 bits)  
# - Words 4-17: Share value (14 words)
# - Words 18-20: Checksum (3 words)

print("Metadata:")
print(f"  ID/Exp words (0-1): {indices[0:2]}")
print(f"  Params words (2-3): {indices[2:4]}")
print(f"  Value words (4-17): {indices[4:18]}")
print(f"  Checksum words (18-20): {indices[18:21]}")
print()

# Extract value data
# Value words: from (ID_EXP_LENGTH_WORDS + 2) to end excluding checksum
# ID_EXP_LENGTH_WORDS = 2
# Params = 2 words
# Checksum = 3 words
# So: from word 4 to word (total - 3)
ID_EXP_LENGTH_WORDS = 2
CHECKSUM_LENGTH_WORDS = 3

value_start = ID_EXP_LENGTH_WORDS + 2
value_end = len(indices) - CHECKSUM_LENGTH_WORDS
value_data = indices[value_start:value_end]

print(f"Value extraction: words[{value_start}:{value_end}]")
print(f"Value data: {value_data}")
print(f"Value data length: {len(value_data)} words")
print()

# Convert to integer
from slip39.share import _int_from_word_indices, bits_to_bytes

value_int = _int_from_word_indices(value_data)
print(f"Value as integer: {value_int}")
print(f"Value as hex: {hex(value_int)}")
print()

# Convert to bytes
# Total mnemonic: 20 words (including 3 checksum words)
# Mnemonic data: 20 words
# Metadata: 4 words (ID/exp + params)
# Checksum: 3 words
# Value: 20 - 4 - 3 = 13 words

# Actually, let's recalculate from mnemonic_data
mnemonic_data_len = len(indices)
print(f"Mnemonic data length: {mnemonic_data_len} words")

# METADATA_LENGTH_WORDS = 4 (ID/exp + params)
METADATA_LENGTH_WORDS = 4
RADIX_BITS = 10

# Padding formula from SLIP-39
padding_len = (RADIX_BITS * (mnemonic_data_len - METADATA_LENGTH_WORDS)) % 16
print(f"Padding bits (from formula): {padding_len}")

# Value words are from ID_EXP (2) + PARAMS (2) to end - CHECKSUM (3)
# = from word 4 to word (20-3) = words 4 to 17 (13 words)
value_data_len = len(value_data)
print(f"Value data length: {value_data_len} words")

# Value byte count
value_byte_count = bits_to_bytes(RADIX_BITS * value_data_len - padding_len)
print(f"Value bytes: {value_byte_count}")
print()

value_bytes = value_int.to_bytes(value_byte_count, 'big')
print(f"Share value: {value_bytes.hex()}")
