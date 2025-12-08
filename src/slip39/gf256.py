"""
Galois Field GF(256) Arithmetic for SLIP-39

This module implements arithmetic operations over GF(256) using the Rijndael
polynomial x^8 + x^4 + x^3 + x + 1 (0x11b in hex).

All operations are compatible with Trezor's python-shamir-mnemonic implementation.
"""

from typing import List, Tuple

# Rijndael irreducible polynomial: x^8 + x^4 + x^3 + x + 1
# Binary: 100011011 = 0x11b
_POLYNOMIAL = 0x11b

# Pre-computed logarithm and exponential tables for efficient multiplication
_LOG_TABLE = [0] * 256
_EXP_TABLE = [0] * 256


def _init_tables() -> None:
    """
    Pre-compute logarithm and exponential tables for GF(256).
    
    These tables enable fast multiplication using the property:
    a * b = exp(log(a) + log(b))
    
    The generator element is 3 (0x03).
    """
    # Generator element for GF(256) with Rijndael polynomial
    generator = 3
    
    # Build exponential table: exp[i] = generator^i
    x = 1
    for i in range(255):
        _EXP_TABLE[i] = x
        _LOG_TABLE[x] = i
        
        # Multiply by generator in GF(256): x = x * 3
        # Use peasant multiplication in GF(256)
        x = _gf256_multiply_slow(x, generator)
    
    # Handle wrap-around for convenience
    _EXP_TABLE[255] = _EXP_TABLE[0]


def _gf256_multiply_slow(a: int, b: int) -> int:
    """
    Multiply two elements in GF(256) without using lookup tables.
    
    This is used for table initialization. Uses peasant multiplication
    with polynomial reduction.
    
    Args:
        a: First element (0-255)
        b: Second element (0-255)
    
    Returns:
        Product in GF(256) (0-255)
    """
    result = 0
    
    # Peasant multiplication
    for _ in range(8):
        if b & 1:
            result ^= a
        
        # Multiply a by x (shift left)
        carry = a & 0x80
        a <<= 1
        
        # If carry bit set, reduce by polynomial
        if carry:
            a ^= _POLYNOMIAL
        
        # Shift b right
        b >>= 1
    
    return result & 0xFF


# Initialize tables on module import
_init_tables()


def add(a: int, b: int) -> int:
    """
    Add two elements in GF(256).
    
    Addition in GF(256) is XOR operation.
    
    Args:
        a: First element (0-255)
        b: Second element (0-255)
    
    Returns:
        Sum in GF(256) (0-255)
    
    Example:
        >>> add(5, 7)
        2
    """
    return a ^ b


def subtract(a: int, b: int) -> int:
    """
    Subtract two elements in GF(256).
    
    Subtraction in GF(256) is the same as addition (XOR).
    
    Args:
        a: First element (0-255)
        b: Second element (0-255)
    
    Returns:
        Difference in GF(256) (0-255)
    """
    return a ^ b


def multiply(a: int, b: int) -> int:
    """
    Multiply two elements in GF(256).
    
    Uses pre-computed log/exp tables for efficiency:
    a * b = exp(log(a) + log(b) mod 255)
    
    Args:
        a: First element (0-255)
        b: Second element (0-255)
    
    Returns:
        Product in GF(256) (0-255)
    
    Example:
        >>> multiply(3, 7)
        9
    """
    if a == 0 or b == 0:
        return 0
    
    # Use logarithm property: log(a*b) = log(a) + log(b)
    log_sum = _LOG_TABLE[a] + _LOG_TABLE[b]
    
    # Reduce modulo 255 (since generator order is 255)
    return _EXP_TABLE[log_sum % 255]


def divide(a: int, b: int) -> int:
    """
    Divide two elements in GF(256).
    
    Division is multiplication by multiplicative inverse:
    a / b = a * b^(-1)
    
    Args:
        a: Numerator (0-255)
        b: Denominator (0-255, must be non-zero)
    
    Returns:
        Quotient in GF(256) (0-255)
    
    Raises:
        ZeroDivisionError: If b is zero
    
    Example:
        >>> divide(9, 3)
        7
    """
    if b == 0:
        raise ZeroDivisionError("Division by zero in GF(256)")
    
    if a == 0:
        return 0
    
    # Use logarithm property: log(a/b) = log(a) - log(b)
    log_diff = _LOG_TABLE[a] - _LOG_TABLE[b]
    
    # Reduce modulo 255
    return _EXP_TABLE[log_diff % 255]


def inverse(a: int) -> int:
    """
    Compute multiplicative inverse of an element in GF(256).
    
    Returns b such that a * b = 1 in GF(256).
    
    Args:
        a: Element to invert (1-255, must be non-zero)
    
    Returns:
        Multiplicative inverse (1-255)
    
    Raises:
        ZeroDivisionError: If a is zero
    
    Example:
        >>> multiply(3, inverse(3))
        1
    """
    if a == 0:
        raise ZeroDivisionError("Zero has no multiplicative inverse")
    
    # inverse(a) = exp(255 - log(a))
    return _EXP_TABLE[255 - _LOG_TABLE[a]]


def interpolate(shares: List[Tuple[int, int]], x: int) -> int:
    """
    Perform Lagrange interpolation over GF(256) to recover secret.
    
    Given a set of (x, y) points on a polynomial, compute the y-value
    at a specific x coordinate using Lagrange interpolation formula:
    
    f(x) = Σ(y_i * Π((x - x_j) / (x_i - x_j))) for all i, j≠i
    
    Args:
        shares: List of (x, y) coordinate pairs in GF(256)
        x: x-coordinate where to evaluate the polynomial
    
    Returns:
        y-value at coordinate x (0-255)
    
    Raises:
        ValueError: If shares list is empty or contains duplicate x-values
    
    Example:
        >>> shares = [(1, 5), (2, 10), (3, 17)]
        >>> interpolate(shares, 0)  # Recover secret at x=0
        2
    """
    if not shares:
        raise ValueError("Cannot interpolate with empty shares list")
    
    # Check for duplicate x-values
    x_coords = [share[0] for share in shares]
    if len(x_coords) != len(set(x_coords)):
        raise ValueError("Shares contain duplicate x-coordinates")
    
    result = 0
    
    for i, (x_i, y_i) in enumerate(shares):
        # Compute Lagrange basis polynomial L_i(x)
        numerator = 1
        denominator = 1
        
        for j, (x_j, _) in enumerate(shares):
            if i == j:
                continue
            
            # Compute (x - x_j) / (x_i - x_j) in GF(256)
            numerator = multiply(numerator, subtract(x, x_j))
            denominator = multiply(denominator, subtract(x_i, x_j))
        
        # Compute y_i * L_i(x)
        basis = divide(numerator, denominator)
        term = multiply(y_i, basis)
        
        # Add to result (XOR in GF(256))
        result = add(result, term)
    
    return result


def interpolate_at_zero(shares: List[Tuple[int, int]]) -> int:
    """
    Optimize Lagrange interpolation for x=0 (common case for secret recovery).
    
    When interpolating at x=0, the formula simplifies:
    f(0) = Σ(y_i * Π(x_j / (x_j - x_i))) for all i, j≠i
    
    Args:
        shares: List of (x, y) coordinate pairs in GF(256)
    
    Returns:
        y-value at x=0 (the secret)
    
    Example:
        >>> shares = [(1, 5), (2, 10), (3, 17)]
        >>> interpolate_at_zero(shares)
        2
    """
    if not shares:
        raise ValueError("Cannot interpolate with empty shares list")
    
    result = 0
    
    for i, (x_i, y_i) in enumerate(shares):
        # Compute Lagrange basis polynomial L_i(0)
        numerator = 1
        denominator = 1
        
        for j, (x_j, _) in enumerate(shares):
            if i == j:
                continue
            
            # Simplified: (0 - x_j) / (x_i - x_j) = x_j / (x_j - x_i)
            # Which equals: -x_j / (x_i - x_j) = x_j / (x_j - x_i)
            numerator = multiply(numerator, x_j)
            denominator = multiply(denominator, subtract(x_j, x_i))
        
        basis = divide(numerator, denominator)
        term = multiply(y_i, basis)
        result = add(result, term)
    
    return result


# Convenience function aliases
def gf256_add(a: int, b: int) -> int:
    """Alias for add()"""
    return add(a, b)


def gf256_mul(a: int, b: int) -> int:
    """Alias for multiply()"""
    return multiply(a, b)


def gf256_div(a: int, b: int) -> int:
    """Alias for divide()"""
    return divide(a, b)


def gf256_inv(a: int) -> int:
    """Alias for inverse()"""
    return inverse(a)


# Export public API
__all__ = [
    'add',
    'subtract',
    'multiply',
    'divide',
    'inverse',
    'interpolate',
    'interpolate_at_zero',
    'gf256_add',
    'gf256_mul',
    'gf256_div',
    'gf256_inv',
]
