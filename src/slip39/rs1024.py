"""
Reed-Solomon RS1024 Checksum for SLIP-39

Implements Reed-Solomon error detection code over GF(1024) using generator
polynomial (x - α)(x - α²)(x - α³) where α is a root of x^10 + x^3 + 1.

The checksum provides strong error detection:
- Detects up to 3 errors with 100% certainty
- Probability < 1e-9 of failing to detect 4+ errors

Compatible with Trezor's python-shamir-mnemonic implementation.
"""

from typing import List, Sequence


# GF(1024) parameters
# Irreducible polynomial: x^10 + x^3 + 1 (binary: 10000001001 = 0x409)
_GF1024_EXP = []  # Exponential table
_GF1024_LOG = []  # Logarithm table


def _init_gf1024_tables() -> None:
    """
    Initialize GF(1024) logarithm and exponential tables.
    
    Uses generator element 2 and irreducible polynomial x^10 + x^3 + 1.
    """
    global _GF1024_EXP, _GF1024_LOG
    
    _GF1024_EXP = [0] * 1024
    _GF1024_LOG = [0] * 1024
    
    # Generator is 2 (x in polynomial representation)
    poly = 1
    for i in range(1023):
        _GF1024_EXP[i] = poly
        _GF1024_LOG[poly] = i
        
        # Multiply by generator (x): shift left by 1
        poly = poly << 1
        
        # If degree >= 10, reduce by irreducible polynomial x^10 + x^3 + 1
        if poly & 0x400:  # If bit 10 is set
            poly ^= 0x409  # XOR with x^10 + x^3 + 1
    
    _GF1024_EXP[1023] = _GF1024_EXP[0]
    _GF1024_LOG[0] = 0


# Initialize tables on module import
_init_gf1024_tables()


def _gf1024_mul(a: int, b: int) -> int:
    """
    Multiply two elements in GF(1024).
    
    Args:
        a: First element (0-1023)
        b: Second element (0-1023)
    
    Returns:
        Product in GF(1024) (0-1023)
    """
    if a == 0 or b == 0:
        return 0
    
    # Use logarithm property: log(a*b) = log(a) + log(b) mod 1023
    log_sum = (_GF1024_LOG[a] + _GF1024_LOG[b]) % 1023
    return _GF1024_EXP[log_sum]


def _polymod(values: Sequence[int]) -> int:
    """
    Compute the Reed-Solomon checksum (polymod) over GF(1024).
    
    This implements the generator polynomial evaluation:
    g(x) = (x - α)(x - α²)(x - α³)
    
    where α is a primitive element of GF(1024).
    
    Args:
        values: Sequence of 10-bit integers (0-1023)
    
    Returns:
        Checksum value (0-1023^3-1, but we use only lower 30 bits)
    """
    # Generator polynomial coefficients for (x - α)(x - α²)(x - α³)
    # These are pre-computed constants from the SLIP-39 specification
    GEN = [
        0x00E0E040,  # Coefficient for x^3
        0x01C1C080,  # Coefficient for x^2  
        0x03838100,  # Coefficient for x^1
        0x07070200,  # Coefficient for x^0
        0x0E0E0009,  # Coefficient for x^-1
        0x1C0C2412,  # Coefficient for x^-2
        0x38086C24,  # Coefficient for x^-3
        0x3090FC48,  # Coefficient for x^-4
        0x21B1F890,  # Coefficient for x^-5
        0x03F3F120,  # Coefficient for x^-6
    ]
    
    chk = 1
    for value in values:
        # Get top 10 bits
        b = chk >> 20
        
        # Shift checksum left by 10 bits and add new value
        chk = ((chk & 0xFFFFF) << 10) ^ value
        
        # Apply generator polynomial based on top bits
        for i in range(10):
            if b & (1 << i):
                chk ^= GEN[i]
    
    return chk


def _create_checksum(data: Sequence[int], customization_string: str) -> List[int]:
    """
    Create RS1024 checksum for the given data.
    
    Args:
        data: Sequence of 10-bit integers (0-1023)
        customization_string: Either "shamir" or "shamir_extendable"
    
    Returns:
        List of 3 checksum values (10-bit integers each)
    """
    # Encode customization string as sequence of 10-bit values
    customization_ints = [ord(c) for c in customization_string]
    
    # Compute polymod over: customization || data || [0, 0, 0]
    values = list(customization_ints) + list(data) + [0, 0, 0]
    polymod_result = _polymod(values) ^ 1  # XOR with 1 as per spec
    
    # Extract three 10-bit checksum values
    checksum = [
        (polymod_result >> 20) & 0x3FF,  # Top 10 bits
        (polymod_result >> 10) & 0x3FF,  # Middle 10 bits
        polymod_result & 0x3FF,          # Bottom 10 bits
    ]
    
    return checksum


def _verify_checksum(data: Sequence[int], customization_string: str) -> bool:
    """
    Verify RS1024 checksum of the given data.
    
    The data should include the 3 checksum values at the end.
    
    Args:
        data: Sequence of 10-bit integers including checksum (0-1023)
        customization_string: Either "shamir" or "shamir_extendable"
    
    Returns:
        True if checksum is valid, False otherwise
    """
    # Encode customization string
    customization_ints = [ord(c) for c in customization_string]
    
    # Compute polymod over: customization || data (including checksum)
    values = list(customization_ints) + list(data)
    polymod_result = _polymod(values)
    
    # Valid checksum should result in polymod == 1
    return polymod_result == 1


# Public API functions

def create_checksum(data: Sequence[int], extendable: bool = False) -> List[int]:
    """
    Create RS1024 checksum for SLIP-39 share data.
    
    Args:
        data: Sequence of 10-bit integers (indices in SLIP-39 wordlist)
        extendable: If True, use "shamir_extendable"; otherwise "shamir"
    
    Returns:
        List of 3 checksum values (10-bit integers, 0-1023 each)
    
    Example:
        >>> data = [123, 456, 789, 321, 654]
        >>> checksum = create_checksum(data, extendable=False)
        >>> len(checksum)
        3
    """
    customization = "shamir_extendable" if extendable else "shamir"
    return _create_checksum(data, customization)


def verify_checksum(data: Sequence[int], extendable: bool = False) -> bool:
    """
    Verify RS1024 checksum of SLIP-39 share data.
    
    The last 3 values in data should be the checksum.
    
    Args:
        data: Sequence of 10-bit integers including checksum at end
        extendable: If True, use "shamir_extendable"; otherwise "shamir"
    
    Returns:
        True if checksum is valid, False otherwise
    
    Example:
        >>> data = [123, 456, 789, 321, 654]
        >>> checksum = create_checksum(data, extendable=False)
        >>> data_with_checksum = list(data) + checksum
        >>> verify_checksum(data_with_checksum, extendable=False)
        True
    """
    if len(data) < 3:
        return False
    
    customization = "shamir_extendable" if extendable else "shamir"
    return _verify_checksum(data, customization)


def append_checksum(data: Sequence[int], extendable: bool = False) -> List[int]:
    """
    Append RS1024 checksum to data.
    
    Args:
        data: Sequence of 10-bit integers
        extendable: If True, use "shamir_extendable"; otherwise "shamir"
    
    Returns:
        New list with data + checksum (3 additional values)
    
    Example:
        >>> data = [123, 456, 789]
        >>> data_with_checksum = append_checksum(data)
        >>> len(data_with_checksum)
        6
        >>> verify_checksum(data_with_checksum)
        True
    """
    checksum = create_checksum(data, extendable)
    return list(data) + checksum


# Export public API
__all__ = [
    'create_checksum',
    'verify_checksum',
    'append_checksum',
]
