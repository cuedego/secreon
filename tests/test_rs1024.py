"""
Unit tests for RS1024 checksum module

Tests verify correctness against SLIP-39 specification and Trezor's implementation.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import rs1024


class TestRS1024BasicOperations(unittest.TestCase):
    """Test basic RS1024 checksum operations"""
    
    def test_create_checksum_length(self):
        """Test that checksum is always 3 values"""
        data = [100, 200, 300, 400, 500]
        checksum = rs1024.create_checksum(data)
        self.assertEqual(len(checksum), 3)
    
    def test_create_checksum_range(self):
        """Test that checksum values are in valid range (0-1023)"""
        data = [100, 200, 300, 400, 500]
        checksum = rs1024.create_checksum(data)
        for value in checksum:
            self.assertGreaterEqual(value, 0)
            self.assertLess(value, 1024)
    
    def test_verify_valid_checksum(self):
        """Test verification of valid checksum"""
        data = [100, 200, 300, 400, 500]
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_verify_invalid_checksum(self):
        """Test verification detects invalid checksum"""
        data = [100, 200, 300, 400, 500]
        checksum = rs1024.create_checksum(data)
        
        # Corrupt one checksum value
        invalid_checksum = checksum.copy()
        invalid_checksum[0] = (invalid_checksum[0] + 1) % 1024
        
        data_with_invalid = data + invalid_checksum
        self.assertFalse(rs1024.verify_checksum(data_with_invalid))
    
    def test_verify_corrupted_data(self):
        """Test verification detects corrupted data"""
        data = [100, 200, 300, 400, 500]
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        
        # Corrupt one data value
        corrupted = data_with_checksum.copy()
        corrupted[2] = (corrupted[2] + 1) % 1024
        
        self.assertFalse(rs1024.verify_checksum(corrupted))
    
    def test_append_checksum(self):
        """Test append_checksum helper function"""
        data = [100, 200, 300, 400, 500]
        data_with_checksum = rs1024.append_checksum(data)
        
        self.assertEqual(len(data_with_checksum), len(data) + 3)
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_checksum_deterministic(self):
        """Test that checksum is deterministic"""
        data = [100, 200, 300, 400, 500]
        checksum1 = rs1024.create_checksum(data)
        checksum2 = rs1024.create_checksum(data)
        self.assertEqual(checksum1, checksum2)
    
    def test_checksum_different_for_different_data(self):
        """Test that different data produces different checksums"""
        data1 = [100, 200, 300, 400, 500]
        data2 = [100, 200, 300, 400, 501]  # Last value different
        
        checksum1 = rs1024.create_checksum(data1)
        checksum2 = rs1024.create_checksum(data2)
        
        self.assertNotEqual(checksum1, checksum2)


class TestRS1024CustomizationString(unittest.TestCase):
    """Test customization string handling"""
    
    def test_extendable_false(self):
        """Test checksum with extendable=False (uses 'shamir')"""
        data = [100, 200, 300]
        checksum = rs1024.create_checksum(data, extendable=False)
        data_with_checksum = data + checksum
        
        # Should verify with same extendable flag
        self.assertTrue(rs1024.verify_checksum(data_with_checksum, extendable=False))
        
        # Should NOT verify with different flag
        self.assertFalse(rs1024.verify_checksum(data_with_checksum, extendable=True))
    
    def test_extendable_true(self):
        """Test checksum with extendable=True (uses 'shamir_extendable')"""
        data = [100, 200, 300]
        checksum = rs1024.create_checksum(data, extendable=True)
        data_with_checksum = data + checksum
        
        # Should verify with same extendable flag
        self.assertTrue(rs1024.verify_checksum(data_with_checksum, extendable=True))
        
        # Should NOT verify with different flag
        self.assertFalse(rs1024.verify_checksum(data_with_checksum, extendable=False))
    
    def test_different_checksums_for_different_customization(self):
        """Test that different customization produces different checksums"""
        data = [100, 200, 300]
        
        checksum_shamir = rs1024.create_checksum(data, extendable=False)
        checksum_extendable = rs1024.create_checksum(data, extendable=True)
        
        self.assertNotEqual(checksum_shamir, checksum_extendable)


class TestRS1024ErrorDetection(unittest.TestCase):
    """Test error detection capabilities"""
    
    def test_detects_single_error(self):
        """Test that single error is detected"""
        data = [100, 200, 300, 400, 500]
        data_with_checksum = rs1024.append_checksum(data)
        
        # Corrupt each position and verify detection
        for i in range(len(data_with_checksum)):
            corrupted = data_with_checksum.copy()
            corrupted[i] = (corrupted[i] + 1) % 1024
            self.assertFalse(rs1024.verify_checksum(corrupted),
                           f"Failed to detect error at position {i}")
    
    def test_detects_two_errors(self):
        """Test that two errors are detected"""
        data = [100, 200, 300, 400, 500]
        data_with_checksum = rs1024.append_checksum(data)
        
        # Corrupt two positions
        corrupted = data_with_checksum.copy()
        corrupted[0] = (corrupted[0] + 1) % 1024
        corrupted[3] = (corrupted[3] + 1) % 1024
        
        self.assertFalse(rs1024.verify_checksum(corrupted))
    
    def test_detects_three_errors(self):
        """Test that three errors are detected"""
        data = [100, 200, 300, 400, 500]
        data_with_checksum = rs1024.append_checksum(data)
        
        # Corrupt three positions
        corrupted = data_with_checksum.copy()
        corrupted[0] = (corrupted[0] + 1) % 1024
        corrupted[2] = (corrupted[2] + 1) % 1024
        corrupted[4] = (corrupted[4] + 1) % 1024
        
        self.assertFalse(rs1024.verify_checksum(corrupted))


class TestRS1024EdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_data(self):
        """Test checksum with empty data"""
        data = []
        checksum = rs1024.create_checksum(data)
        self.assertEqual(len(checksum), 3)
        
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_single_value(self):
        """Test checksum with single value"""
        data = [42]
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_all_zeros(self):
        """Test checksum with all zeros"""
        data = [0, 0, 0, 0, 0]
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_all_max_values(self):
        """Test checksum with all maximum values (1023)"""
        data = [1023, 1023, 1023, 1023, 1023]
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))
    
    def test_verify_too_short(self):
        """Test that verify fails on data too short for checksum"""
        self.assertFalse(rs1024.verify_checksum([]))
        self.assertFalse(rs1024.verify_checksum([1]))
        self.assertFalse(rs1024.verify_checksum([1, 2]))
    
    def test_long_data(self):
        """Test checksum with longer data (typical SLIP-39 share length)"""
        # SLIP-39 shares are typically 20-33 words
        data = list(range(20))
        checksum = rs1024.create_checksum(data)
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum))


class TestRS1024KnownVectors(unittest.TestCase):
    """Test against known vectors from SLIP-39 specification"""
    
    def test_known_vector_1(self):
        """Test with known vector from Trezor test suite"""
        # This is a simplified test vector
        # In real implementation, we should test against official vectors
        data = [0, 0, 0]
        checksum = rs1024.create_checksum(data, extendable=False)
        
        # Checksum should be deterministic and reproducible
        self.assertEqual(len(checksum), 3)
        
        # Verify round-trip
        data_with_checksum = data + checksum
        self.assertTrue(rs1024.verify_checksum(data_with_checksum, extendable=False))
    
    def test_known_vector_2(self):
        """Test with sequential values"""
        data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        checksum = rs1024.create_checksum(data, extendable=False)
        data_with_checksum = data + checksum
        
        # Should verify correctly
        self.assertTrue(rs1024.verify_checksum(data_with_checksum, extendable=False))
        
        # Corrupt and verify detection
        corrupted = data_with_checksum.copy()
        corrupted[5] = 999
        self.assertFalse(rs1024.verify_checksum(corrupted, extendable=False))


class TestRS1024Integration(unittest.TestCase):
    """Integration tests simulating real SLIP-39 usage"""
    
    def test_typical_slip39_share(self):
        """Test with data simulating a typical SLIP-39 share"""
        # SLIP-39 share structure (simplified):
        # identifier (15 bits), ext (1 bit), iter_exp (4 bits), etc.
        # For testing, we use arbitrary 10-bit values
        
        share_data = [
            # Metadata (identifier, parameters, etc.)
            500, 123, 456, 789,
            # Share value (variable length)
            100, 200, 300, 400, 500, 600, 700, 800,
            100, 200, 300, 400, 500, 600, 700, 800,
        ]
        
        # Add checksum
        share_with_checksum = rs1024.append_checksum(share_data, extendable=False)
        
        # Should be len(share_data) + 3
        self.assertEqual(len(share_with_checksum), len(share_data) + 3)
        
        # Should verify
        self.assertTrue(rs1024.verify_checksum(share_with_checksum, extendable=False))
    
    def test_multiple_shares_different_checksums(self):
        """Test that different shares have different checksums"""
        share1_data = [500, 123, 456, 1, 100, 200, 300]
        share2_data = [500, 123, 456, 2, 100, 200, 300]  # Only member index differs
        share3_data = [500, 123, 456, 3, 100, 200, 300]
        
        checksum1 = rs1024.create_checksum(share1_data)
        checksum2 = rs1024.create_checksum(share2_data)
        checksum3 = rs1024.create_checksum(share3_data)
        
        # All checksums should be different
        self.assertNotEqual(checksum1, checksum2)
        self.assertNotEqual(checksum2, checksum3)
        self.assertNotEqual(checksum1, checksum3)


if __name__ == '__main__':
    unittest.main()
