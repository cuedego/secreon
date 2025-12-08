#!/usr/bin/env python3
"""
Generate correct test vectors using Trezor's library.
"""
import json
from shamir_mnemonic import shamir

# Load the existing vectors to get mnemonics
with open('tests/slip39-vectors.json') as f:
    vectors = json.load(f)

corrected = []
for i, vector in enumerate(vectors):
    desc, mnemonics, old_expected, xprv = vector
    
    # For invalid vectors, keep as-is
    if "Invalid" in desc or "invalid" in desc:
        corrected.append(vector)
        continue
    
    # For valid vectors, compute correct secret
    try:
        correct_secret = shamir.combine_mnemonics(mnemonics).hex()
        corrected.append([desc, mnemonics, correct_secret, xprv])
        print(f"✓ Vector {i}: {desc[:50]}")
        if correct_secret != old_expected:
            print(f"  Fixed: {old_expected} → {correct_secret}")
    except Exception as e:
        # Keep invalid vectors as-is
        corrected.append(vector)
        print(f"✗ Vector {i}: {desc[:50]} - {e}")

# Save corrected vectors
with open('tests/slip39-vectors-corrected.json', 'w') as f:
    json.dump(corrected, f, indent=2)

print(f"\nWrote {len(corrected)} vectors to tests/slip39-vectors-corrected.json")
