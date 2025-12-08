"""
Unit tests for SLIP-39 Shamir's Secret Sharing

Tests verify split/recover functionality and compatibility.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import shamir


class TestBasicSharing(unittest.TestCase):
    """Test basic secret sharing functionality"""
    
    def test_basic_2of3(self):
        """Test basic 2-of-3 sharing"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # Generate shares
        groups = shamir.generate_mnemonics(1, [(2, 3)], secret)
        
        # Should have 1 group with 3 shares
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 3)
        
        # Any 2 shares should recover the secret
        self.assertEqual(shamir.combine_mnemonics(groups[0][:2]), secret)
        self.assertEqual(shamir.combine_mnemonics(groups[0][1:]), secret)
        self.assertEqual(shamir.combine_mnemonics([groups[0][0], groups[0][2]]), secret)
    
    def test_basic_3of5(self):
        """Test basic 3-of-5 sharing"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret)
        
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 5)
        
        # Any 3 shares should work
        self.assertEqual(shamir.combine_mnemonics(groups[0][:3]), secret)
        self.assertEqual(shamir.combine_mnemonics(groups[0][2:]), secret)
        self.assertEqual(shamir.combine_mnemonics([groups[0][0], groups[0][2], groups[0][4]]), secret)
    
    def test_insufficient_shares(self):
        """Test that insufficient shares fail to recover"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret)
        
        # Only 2 shares when 3 required should fail
        with self.assertRaises(shamir.MnemonicError):
            shamir.combine_mnemonics(groups[0][:2])


class TestPassphraseProtection(unittest.TestCase):
    """Test passphrase-protected secrets"""
    
    def test_with_passphrase(self):
        """Test recovery with passphrase"""
        secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"my secret passphrase"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret, passphrase)
        
        # Should recover with correct passphrase
        recovered = shamir.combine_mnemonics(groups[0][:3], passphrase)
        self.assertEqual(secret, recovered)
    
    def test_wrong_passphrase(self):
        """Test that wrong passphrase gives wrong result"""
        secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"correct"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret, passphrase)
        
        # Wrong passphrase should give wrong result
        recovered = shamir.combine_mnemonics(groups[0][:3], b"wrong")
        self.assertNotEqual(secret, recovered)
    
    def test_empty_passphrase(self):
        """Test with empty passphrase"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret, b"")
        
        recovered = shamir.combine_mnemonics(groups[0][:3], b"")
        self.assertEqual(secret, recovered)


class TestGroupSharing(unittest.TestCase):
    """Test multi-group sharing"""
    
    def test_2of3_groups(self):
        """Test 2-of-3 group sharing"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # 2-of-3 groups, each with 2-of-3 members
        groups = shamir.generate_mnemonics(
            2, [(2, 3), (2, 3), (2, 3)], secret
        )
        
        self.assertEqual(len(groups), 3)
        
        # Any 2 groups with 2 members each should work
        mnemonics = groups[0][:2] + groups[1][:2]
        self.assertEqual(shamir.combine_mnemonics(mnemonics), secret)
        
        mnemonics = groups[1][:2] + groups[2][:2]
        self.assertEqual(shamir.combine_mnemonics(mnemonics), secret)
    
    def test_mixed_thresholds(self):
        """Test groups with different thresholds"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # 2-of-3 groups: (2-of-3), (3-of-5), (1-of-1)
        groups = shamir.generate_mnemonics(
            2, [(2, 3), (3, 5), (1, 1)], secret
        )
        
        # Groups 0 and 2
        mnemonics = groups[0][:2] + [groups[2][0]]
        self.assertEqual(shamir.combine_mnemonics(mnemonics), secret)
        
        # Groups 1 and 2
        mnemonics = groups[1][:3] + [groups[2][0]]
        self.assertEqual(shamir.combine_mnemonics(mnemonics), secret)


class TestIterationExponent(unittest.TestCase):
    """Test different iteration exponents"""
    
    def test_exponent_0(self):
        """Test with iteration exponent 0"""
        secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"test"
        
        groups = shamir.generate_mnemonics(
            1, [(3, 5)], secret, passphrase, iteration_exponent=0
        )
        
        recovered = shamir.combine_mnemonics(groups[0][:3], passphrase)
        self.assertEqual(secret, recovered)
    
    def test_exponent_2(self):
        """Test with iteration exponent 2"""
        secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"test"
        
        groups = shamir.generate_mnemonics(
            1, [(3, 5)], secret, passphrase, iteration_exponent=2
        )
        
        recovered = shamir.combine_mnemonics(groups[0][:3], passphrase)
        self.assertEqual(secret, recovered)


class TestExtendableFlag(unittest.TestCase):
    """Test extendable backup flag"""
    
    def test_extendable_true(self):
        """Test with extendable=True"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(
            1, [(3, 5)], secret, extendable=True
        )
        
        recovered = shamir.combine_mnemonics(groups[0][:3])
        self.assertEqual(secret, recovered)
    
    def test_extendable_false(self):
        """Test with extendable=False"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(
            1, [(3, 5)], secret, extendable=False
        )
        
        recovered = shamir.combine_mnemonics(groups[0][:3])
        self.assertEqual(secret, recovered)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def test_1of1_sharing(self):
        """Test trivial 1-of-1 sharing"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(1, [(1, 1)], secret)
        
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 1)
        
        recovered = shamir.combine_mnemonics(groups[0])
        self.assertEqual(secret, recovered)
    
    def test_secret_lengths(self):
        """Test different secret lengths"""
        for length in [16, 32]:
            secret = bytes(range(length))
            
            groups = shamir.generate_mnemonics(1, [(3, 5)], secret)
            recovered = shamir.combine_mnemonics(groups[0][:3])
            
            self.assertEqual(secret, recovered)
    
    def test_invalid_threshold(self):
        """Test that invalid threshold raises error"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # Threshold > count
        with self.assertRaises(ValueError):
            shamir.generate_mnemonics(1, [(4, 3)], secret)
        
        # Threshold = 0
        with self.assertRaises(ValueError):
            shamir.generate_mnemonics(1, [(0, 3)], secret)
    
    def test_invalid_group_threshold(self):
        """Test that invalid group threshold raises error"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # Group threshold > group count
        with self.assertRaises(ValueError):
            shamir.generate_mnemonics(3, [(2, 3), (2, 3)], secret)
    
    def test_invalid_1ofN(self):
        """Test that 1-of-N with N>1 is rejected"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        # 1-of-3 is not allowed
        with self.assertRaises(ValueError):
            shamir.generate_mnemonics(1, [(1, 3)], secret)
    
    def test_short_secret(self):
        """Test that short secrets are rejected"""
        secret = b"SHORT"  # Only 5 bytes
        
        with self.assertRaises(ValueError):
            shamir.generate_mnemonics(1, [(3, 5)], secret)
    
    def test_empty_mnemonics(self):
        """Test that empty mnemonic list raises error"""
        with self.assertRaises(shamir.MnemonicError):
            shamir.combine_mnemonics([])
    
    def test_mixed_share_sets(self):
        """Test that shares from different sets cannot be mixed"""
        secret1 = b"ABCDEFGHIJKLMNOP"
        secret2 = b"1234567890123456"
        
        groups1 = shamir.generate_mnemonics(1, [(3, 5)], secret1)
        groups2 = shamir.generate_mnemonics(1, [(3, 5)], secret2)
        
        # Mixing shares from different sets should fail
        mixed = [groups1[0][0], groups1[0][1], groups2[0][0]]
        with self.assertRaises(shamir.MnemonicError):
            shamir.combine_mnemonics(mixed)


class TestDeterminism(unittest.TestCase):
    """Test deterministic behavior"""
    
    def test_recovery_deterministic(self):
        """Test that recovery is deterministic"""
        secret = b"ABCDEFGHIJKLMNOP"
        
        groups = shamir.generate_mnemonics(1, [(3, 5)], secret)
        
        # Multiple recoveries should give same result
        recovered1 = shamir.combine_mnemonics(groups[0][:3])
        recovered2 = shamir.combine_mnemonics(groups[0][:3])
        
        self.assertEqual(recovered1, recovered2)
        self.assertEqual(secret, recovered1)


if __name__ == '__main__':
    unittest.main()
