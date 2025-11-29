#!/usr/bin/env python3
"""
Vaultix - Shamir's Secret Sharing for secure secret management

Usage:
    vaultix generate --secret "my secret" --out shares.json
    vaultix recover --shares-file shares.json --as-str
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from sss import main

if __name__ == '__main__':
    sys.exit(main())
