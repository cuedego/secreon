#!/usr/bin/env python3
"""
Comprehensive check - maybe identifier extraction is wrong?
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.share import Share, _int_from_word_indices
from slip39 import wordlist

MNEMONIC = "duckling enlarge academic academic agency result length solution fridge kidney coal piece deal husband erode duke ajar critical decision keyboard"

# Parse with our code
share = Share.from_mnemonic(MNEMONIC)

print("=== OUR PARSING ===")
print(f"Identifier: {share.identifier} (0x{share.identifier:04x} = 0b{share.identifier:016b})")
print(f"Extendable: {share.extendable}")
print(f"Iteration exponent: {share.iteration_exponent}")
print()

# Manual parse
indices = wordlist.mnemonic_to_indices(MNEMONIC)
id_exp_data = indices[:2]
id_exp_int = _int_from_word_indices(id_exp_data)

print("=== MANUAL PARSING ===")
print(f"ID/Exp words: {id_exp_data}")
print(f"ID/Exp integer: {id_exp_int} (0x{id_exp_int:05x} = 0b{id_exp_int:020b})")
print()

# Bits layout: [15-bit ID][1-bit extendable][4-bit iteration_exp]
identifier_manual = id_exp_int >> 5
extendable_manual = bool((id_exp_int >> 4) & 1)
iteration_exp_manual = id_exp_int & 0xF

print(f"Identifier (manual): {identifier_manual} (0x{identifier_manual:04x})")
print(f"Extendable (manual): {extendable_manual}")
print(f"Iteration exponent (manual): {iteration_exp_manual}")
print()

print("=== MATCHES ===")
print(f"Identifier match: {share.identifier == identifier_manual}")
print(f"Extendable match: {share.extendable == extendable_manual}")
print(f"Iteration exponent match: {share.iteration_exponent == iteration_exp_manual}")
