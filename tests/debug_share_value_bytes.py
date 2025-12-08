#!/usr/bin/env python3
"""
Check the exact bytes stored in Share.value
"""
import sys
sys.path.insert(0, '/home/cuedego/secreon/src')

from slip39.share import Share

MNEMONIC = "duckling enlarge academic academic agency result length solution fridge kidney coal piece deal husband erode duke ajar critical decision keyboard"

share = Share.from_mnemonic(MNEMONIC)
print(f"Share value: {share.value.hex()}")
print(f"Length: {len(share.value)}")
print(f"As list: {list(share.value)}")
