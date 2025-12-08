"""
Feistel cipher for SLIP-39 master secret encryption

The master secret is encrypted using a 4-round Feistel cipher with
PBKDF2-HMAC-SHA256 as the round function.
"""

import hashlib
from typing import Tuple

# Constants
BASE_ITERATION_COUNT = 10000
"""The minimum number of iterations to use in PBKDF2."""

ROUND_COUNT = 4
"""The number of rounds to use in the Feistel cipher."""

CUSTOMIZATION_STRING = b"shamir"
"""The customization string used in the PBKDF2 salt for non-extendable shares."""

ID_LENGTH_BYTES = 2
"""The length of the identifier in bytes (15 bits = 2 bytes)."""


def _xor(a: bytes, b: bytes) -> bytes:
    """XOR two byte sequences of equal length."""
    return bytes(x ^ y for x, y in zip(a, b))


def _round_function(
    round_num: int,
    passphrase: bytes,
    iteration_exponent: int,
    salt: bytes,
    data: bytes
) -> bytes:
    """
    The round function used internally by the Feistel cipher.
    
    Args:
        round_num: The round number (0-3)
        passphrase: The passphrase bytes
        iteration_exponent: The iteration exponent (e)
        salt: The salt for PBKDF2
        data: The data to process
        
    Returns:
        The output of the round function
    """
    # Key for PBKDF2 is round_number || passphrase
    key = bytes([round_num]) + passphrase
    
    # Salt for PBKDF2 is salt || data
    salt_input = salt + data
    
    # Iteration count is (BASE_ITERATION_COUNT * 2^e) / ROUND_COUNT
    iteration_count = (BASE_ITERATION_COUNT << iteration_exponent) // ROUND_COUNT
    
    # Use PBKDF2-HMAC-SHA256 to derive key material
    return hashlib.pbkdf2_hmac(
        'sha256',
        key,
        salt_input,
        iteration_count,
        dklen=len(data)
    )


def _get_salt(identifier: int, extendable: bool) -> bytes:
    """
    Get the salt for the Feistel cipher.
    
    Args:
        identifier: The 15-bit identifier
        extendable: Whether this is an extendable backup
        
    Returns:
        The salt bytes
    """
    if extendable:
        # Extendable backups use empty salt
        return bytes()
    else:
        # Non-extendable backups use "shamir" || identifier
        return CUSTOMIZATION_STRING + identifier.to_bytes(ID_LENGTH_BYTES, 'big')


def encrypt(
    master_secret: bytes,
    passphrase: bytes,
    iteration_exponent: int,
    identifier: int,
    extendable: bool
) -> bytes:
    """
    Encrypt a master secret using a 4-round Feistel cipher.
    
    The master secret is split into left (L) and right (R) halves.
    For each round i (0-3):
        L, R = R, L XOR F(i, passphrase, e, salt, R)
    
    Args:
        master_secret: The master secret to encrypt (must be even length)
        passphrase: The passphrase for encryption
        iteration_exponent: The iteration exponent (0-15)
        identifier: The 15-bit share identifier
        extendable: Whether this is an extendable backup
        
    Returns:
        The encrypted master secret
        
    Raises:
        ValueError: If master_secret length is not even
    """
    if len(master_secret) % 2 != 0:
        raise ValueError(
            "The length of the master secret in bytes must be an even number."
        )
    
    # Split into left and right halves
    half = len(master_secret) // 2
    left = master_secret[:half]
    right = master_secret[half:]
    
    # Get salt for PBKDF2
    salt = _get_salt(identifier, extendable)
    
    # Perform 4 Feistel rounds
    for i in range(ROUND_COUNT):
        f_output = _round_function(i, passphrase, iteration_exponent, salt, right)
        left, right = right, _xor(left, f_output)
    
    # Return R || L (swapped)
    return right + left


def decrypt(
    encrypted_master_secret: bytes,
    passphrase: bytes,
    iteration_exponent: int,
    identifier: int,
    extendable: bool
) -> bytes:
    """
    Decrypt an encrypted master secret using a 4-round Feistel cipher.
    
    The decryption is the inverse of encryption - same operations but
    rounds applied in reverse order (3, 2, 1, 0).
    
    Args:
        encrypted_master_secret: The encrypted master secret (must be even length)
        passphrase: The passphrase for decryption
        iteration_exponent: The iteration exponent (0-15)
        identifier: The 15-bit share identifier
        extendable: Whether this is an extendable backup
        
    Returns:
        The decrypted master secret
        
    Raises:
        ValueError: If encrypted_master_secret length is not even
    """
    if len(encrypted_master_secret) % 2 != 0:
        raise ValueError(
            "The length of the encrypted master secret in bytes must be an even number."
        )
    
    # Split into left and right halves
    half = len(encrypted_master_secret) // 2
    left = encrypted_master_secret[:half]
    right = encrypted_master_secret[half:]
    
    # Get salt for PBKDF2
    salt = _get_salt(identifier, extendable)
    
    # Perform 4 Feistel rounds in reverse order
    for i in reversed(range(ROUND_COUNT)):
        f_output = _round_function(i, passphrase, iteration_exponent, salt, right)
        left, right = right, _xor(left, f_output)
    
    # Return R || L (swapped)
    return right + left
