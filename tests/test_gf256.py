"""
Unit tests for GF(256) arithmetic module

Tests verify correctness against known values and properties of Galois Field arithmetic.
Compatible with Trezor's python-shamir-mnemonic implementation.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import gf256


class TestGF256BasicOperations(unittest.TestCase):
    """Test basic GF(256) operations"""
    
    def test_add_commutative(self):
        """Test that addition is commutative: a + b = b + a"""
        self.assertEqual(gf256.add(5, 7), gf256.add(7, 5))
        self.assertEqual(gf256.add(100, 200), gf256.add(200, 100))
    
    def test_add_identity(self):
        """Test additive identity: a + 0 = a"""
        for a in [0, 1, 5, 100, 255]:
            self.assertEqual(gf256.add(a, 0), a)
            self.assertEqual(gf256.add(0, a), a)
    
    def test_add_inverse(self):
        """Test additive inverse: a + a = 0 (in GF(256))"""
        for a in range(256):
            self.assertEqual(gf256.add(a, a), 0)
    
    def test_add_known_values(self):
        """Test addition with known values"""
        self.assertEqual(gf256.add(5, 7), 2)  # 0b101 XOR 0b111 = 0b010
        self.assertEqual(gf256.add(15, 15), 0)
        self.assertEqual(gf256.add(255, 1), 254)
        self.assertEqual(gf256.add(128, 127), 255)
    
    def test_subtract_same_as_add(self):
        """Test that subtraction equals addition in GF(256)"""
        for a in [0, 1, 50, 100, 255]:
            for b in [0, 1, 50, 100, 255]:
                self.assertEqual(gf256.subtract(a, b), gf256.add(a, b))
    
    def test_multiply_commutative(self):
        """Test that multiplication is commutative: a * b = b * a"""
        self.assertEqual(gf256.multiply(3, 7), gf256.multiply(7, 3))
        self.assertEqual(gf256.multiply(100, 50), gf256.multiply(50, 100))
    
    def test_multiply_identity(self):
        """Test multiplicative identity: a * 1 = a"""
        for a in range(256):
            self.assertEqual(gf256.multiply(a, 1), a)
            self.assertEqual(gf256.multiply(1, a), a)
    
    def test_multiply_zero(self):
        """Test multiplication by zero: a * 0 = 0"""
        for a in range(256):
            self.assertEqual(gf256.multiply(a, 0), 0)
            self.assertEqual(gf256.multiply(0, a), 0)
    
    def test_multiply_known_values(self):
        """Test multiplication with known values from AES S-box"""
        # Known test vectors from Rijndael field
        self.assertEqual(gf256.multiply(2, 3), 6)
        self.assertEqual(gf256.multiply(3, 7), 9)
        self.assertEqual(gf256.multiply(7, 9), 63)
        self.assertEqual(gf256.multiply(5, 5), 17)  # In GF(256), not regular math
        self.assertEqual(gf256.multiply(16, 16), 27)  # x^4 * x^4 = x^8 mod polynomial
    
    def test_multiply_generator(self):
        """Test that generator 3 generates all non-zero elements"""
        # 3^255 should equal 3^0 = 1 (order of generator is 255)
        result = 1
        for _ in range(255):
            result = gf256.multiply(result, 3)
        self.assertEqual(result, 1)
    
    def test_divide_by_self(self):
        """Test that a / a = 1 for non-zero a"""
        for a in range(1, 256):
            self.assertEqual(gf256.divide(a, a), 1)
    
    def test_divide_zero_numerator(self):
        """Test that 0 / a = 0 for non-zero a"""
        for a in range(1, 256):
            self.assertEqual(gf256.divide(0, a), 0)
    
    def test_divide_zero_denominator(self):
        """Test that division by zero raises exception"""
        with self.assertRaises(ZeroDivisionError):
            gf256.divide(5, 0)
    
    def test_divide_inverse_relationship(self):
        """Test that a / b = a * (1/b)"""
        for a in [1, 5, 10, 100, 255]:
            for b in [1, 3, 7, 50, 200]:
                expected = gf256.multiply(a, gf256.inverse(b))
                self.assertEqual(gf256.divide(a, b), expected)
    
    def test_divide_known_values(self):
        """Test division with known values"""
        # Since multiply(3, 7) = 9, then divide(9, 3) = 7
        self.assertEqual(gf256.divide(9, 3), 7)
        self.assertEqual(gf256.divide(9, 7), 3)
        # Since multiply(5, 5) = 17 in GF(256), then divide(17, 5) = 5
        self.assertEqual(gf256.divide(17, 5), 5)


class TestGF256Inverse(unittest.TestCase):
    """Test multiplicative inverse operations"""
    
    def test_inverse_zero(self):
        """Test that inverse of zero raises exception"""
        with self.assertRaises(ZeroDivisionError):
            gf256.inverse(0)
    
    def test_inverse_identity(self):
        """Test that inverse of 1 is 1"""
        self.assertEqual(gf256.inverse(1), 1)
    
    def test_inverse_property(self):
        """Test that a * inverse(a) = 1 for all non-zero a"""
        for a in range(1, 256):
            inv_a = gf256.inverse(a)
            self.assertEqual(gf256.multiply(a, inv_a), 1)
    
    def test_double_inverse(self):
        """Test that inverse(inverse(a)) = a"""
        for a in range(1, 256):
            self.assertEqual(gf256.inverse(gf256.inverse(a)), a)
    
    def test_inverse_known_values(self):
        """Test inverse with known values"""
        # Known inverses from Rijndael field
        self.assertEqual(gf256.inverse(3), 246)
        self.assertEqual(gf256.inverse(246), 3)
        self.assertEqual(gf256.inverse(5), 82)
        self.assertEqual(gf256.inverse(82), 5)


class TestGF256Interpolation(unittest.TestCase):
    """Test Lagrange interpolation over GF(256)"""
    
    def test_interpolate_single_point(self):
        """Test interpolation with single point (constant polynomial)"""
        shares = [(1, 42)]
        # Constant polynomial f(x) = 42
        self.assertEqual(gf256.interpolate(shares, 0), 42)
        self.assertEqual(gf256.interpolate(shares, 5), 42)
        self.assertEqual(gf256.interpolate(shares, 255), 42)
    
    def test_interpolate_linear(self):
        """Test interpolation with two points (linear polynomial)"""
        # f(x) = 10 + 5*x over GF(256)
        # f(1) = 10 + 5 = 15
        # f(2) = 10 + 10 = 0 (since 10 XOR 10 = 0)
        shares = [(1, 15), (2, 0)]
        # f(0) should be 10
        self.assertEqual(gf256.interpolate(shares, 0), 10)
    
    def test_interpolate_quadratic(self):
        """Test interpolation with three points (quadratic polynomial)"""
        # Create polynomial f(x) = 7 + 3*x + 2*x^2
        # f(1) = 7 + 3 + 2 = 7 XOR 3 XOR 2 = 6
        # f(2) = 7 + 6 + 8 = 7 XOR 6 XOR 8 = 9
        # f(3) = 7 + 9 + 18 = 7 XOR 9 XOR 18 = 20
        
        # Evaluate using GF(256) arithmetic
        def eval_poly(x):
            term0 = 7
            term1 = gf256.multiply(3, x)
            term2 = gf256.multiply(2, gf256.multiply(x, x))
            return gf256.add(gf256.add(term0, term1), term2)
        
        y1 = eval_poly(1)
        y2 = eval_poly(2)
        y3 = eval_poly(3)
        
        shares = [(1, y1), (2, y2), (3, y3)]
        
        # Interpolate at x=0 should give constant term = 7
        self.assertEqual(gf256.interpolate(shares, 0), 7)
        
        # Interpolate at other points should match polynomial
        self.assertEqual(gf256.interpolate(shares, 1), y1)
        self.assertEqual(gf256.interpolate(shares, 2), y2)
        self.assertEqual(gf256.interpolate(shares, 3), y3)
    
    def test_interpolate_empty_shares(self):
        """Test that empty shares list raises ValueError"""
        with self.assertRaises(ValueError):
            gf256.interpolate([], 0)
    
    def test_interpolate_duplicate_x(self):
        """Test that duplicate x-coordinates raise ValueError"""
        shares = [(1, 5), (2, 10), (1, 15)]  # x=1 appears twice
        with self.assertRaises(ValueError):
            gf256.interpolate(shares, 0)
    
    def test_interpolate_at_zero_optimization(self):
        """Test optimized interpolation at x=0"""
        # Create test polynomial
        def eval_poly(x):
            term0 = 42
            term1 = gf256.multiply(7, x)
            term2 = gf256.multiply(3, gf256.multiply(x, x))
            return gf256.add(gf256.add(term0, term1), term2)
        
        shares = [(1, eval_poly(1)), (2, eval_poly(2)), (3, eval_poly(3))]
        
        # Both methods should give same result
        result1 = gf256.interpolate(shares, 0)
        result2 = gf256.interpolate_at_zero(shares)
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, 42)  # Constant term
    
    def test_interpolate_real_sss_scenario(self):
        """Test interpolation in a realistic SSS scenario"""
        # Secret at x=255 (SLIP-39 convention)
        secret = 123
        
        # Create shares using simple polynomial: f(x) = secret + rand*(x-255)
        # This ensures f(255) = secret
        rand_coeff = 77
        
        def eval_poly(x):
            # f(x) = secret + rand_coeff * (x - 255)
            diff = gf256.subtract(x, 255)
            term = gf256.multiply(rand_coeff, diff)
            return gf256.add(secret, term)
        
        # Generate shares at x=1, 2, 3
        shares = [(i, eval_poly(i)) for i in range(1, 4)]
        
        # Recover secret at x=255
        recovered = gf256.interpolate(shares, 255)
        self.assertEqual(recovered, secret)


class TestGF256FieldProperties(unittest.TestCase):
    """Test mathematical properties of GF(256)"""
    
    def test_distributive_property(self):
        """Test distributive property: a * (b + c) = (a * b) + (a * c)"""
        test_cases = [(3, 5, 7), (10, 20, 30), (100, 150, 200)]
        
        for a, b, c in test_cases:
            left = gf256.multiply(a, gf256.add(b, c))
            right = gf256.add(gf256.multiply(a, b), gf256.multiply(a, c))
            self.assertEqual(left, right)
    
    def test_associative_addition(self):
        """Test associative property of addition: (a + b) + c = a + (b + c)"""
        test_cases = [(3, 5, 7), (10, 20, 30), (100, 150, 200)]
        
        for a, b, c in test_cases:
            left = gf256.add(gf256.add(a, b), c)
            right = gf256.add(a, gf256.add(b, c))
            self.assertEqual(left, right)
    
    def test_associative_multiplication(self):
        """Test associative property of multiplication: (a * b) * c = a * (b * c)"""
        test_cases = [(3, 5, 7), (10, 20, 30), (2, 3, 4)]
        
        for a, b, c in test_cases:
            left = gf256.multiply(gf256.multiply(a, b), c)
            right = gf256.multiply(a, gf256.multiply(b, c))
            self.assertEqual(left, right)
    
    def test_field_size(self):
        """Test that field has exactly 256 elements"""
        # All operations should produce results in range [0, 255]
        for a in range(256):
            for b in range(256):
                result_add = gf256.add(a, b)
                result_mul = gf256.multiply(a, b)
                
                self.assertGreaterEqual(result_add, 0)
                self.assertLess(result_add, 256)
                self.assertGreaterEqual(result_mul, 0)
                self.assertLess(result_mul, 256)


class TestGF256Aliases(unittest.TestCase):
    """Test convenience function aliases"""
    
    def test_gf256_add_alias(self):
        """Test gf256_add alias"""
        self.assertEqual(gf256.gf256_add(5, 7), gf256.add(5, 7))
    
    def test_gf256_mul_alias(self):
        """Test gf256_mul alias"""
        self.assertEqual(gf256.gf256_mul(3, 7), gf256.multiply(3, 7))
    
    def test_gf256_div_alias(self):
        """Test gf256_div alias"""
        self.assertEqual(gf256.gf256_div(9, 3), gf256.divide(9, 3))
    
    def test_gf256_inv_alias(self):
        """Test gf256_inv alias"""
        self.assertEqual(gf256.gf256_inv(3), gf256.inverse(3))


if __name__ == '__main__':
    unittest.main()
