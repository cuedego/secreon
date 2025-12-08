"""
SLIP-39: Shamir's Secret-Sharing for Mnemonic Codes

This package implements SLIP-39 standard for splitting BIP-32 master secrets
into mnemonic shares using Shamir's Secret Sharing over GF(256).

Compatible with Trezor's python-shamir-mnemonic implementation.
"""

__version__ = "0.1.0"

# Import main API
from .shamir import (
    generate_mnemonics,
    combine_mnemonics,
    split_ems,
    recover_ems,
    EncryptedMasterSecret,
    MnemonicError,
)
from .share import Share
from .bip39 import generate_mnemonic, validate_mnemonic, mnemonic_to_seed

__all__ = [
    'generate_mnemonics',
    'combine_mnemonics',
    'split_ems',
    'recover_ems',
    'EncryptedMasterSecret',
    'MnemonicError',
    'Share',
    'generate_mnemonic',
    'validate_mnemonic',
    'mnemonic_to_seed',
]
