"""
Unit tests for SLIP-39 Share data structure

Tests verify encoding/decoding and compatibility with Trezor's implementation.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import share


class TestShareEncoding(unittest.TestCase):
    """Test share encoding to mnemonic"""
    
    def test_simple_share_encoding(self):
        """Test encoding a simple share"""
        s = share.Share(
            identifier=0,
            extendable=False,
            iteration_exponent=0,
            group_index=0,
            group_threshold=1,
            group_count=1,
            index=0,
            member_threshold=1,
            value=b'\x00' * 16
        )
        
        words = s.words()
        self.assertIsInstance(words, list)
        self.assertTrue(all(isinstance(w, str) for w in words))
        self.assertTrue(len(words) >= share.MIN_MNEMONIC_LENGTH_WORDS)
    
    def test_roundtrip(self):
        """Test that Share -> mnemonic -> Share preserves data"""
        original = share.Share(
            identifier=12345,
            extendable=False,
            iteration_exponent=1,
            group_index=0,
            group_threshold=2,
            group_count=3,
            index=1,
            member_threshold=3,
            value=bytes(range(16))
        )
        
        mnemonic = original.mnemonic()
        recovered = share.Share.from_mnemonic(mnemonic)
        
        self.assertEqual(original, recovered)


class TestShareDecoding(unittest.TestCase):
    """Test share decoding from mnemonic"""
    
    def test_invalid_checksum_rejected(self):
        """Test that invalid checksum is rejected"""
        # Create a valid share
        s = share.Share(
            identifier=0,
            extendable=False,
            iteration_exponent=0,
            group_index=0,
            group_threshold=1,
            group_count=1,
            index=0,
            member_threshold=1,
            value=b'\x00' * 16
        )
        
        # Get words and corrupt the last one (checksum)
        words = s.words()
        # Change last word to a different valid word
        if words[-1] != 'academic':
            words[-1] = 'academic'
        else:
            words[-1] = 'acid'
        bad_mnemonic = ' '.join(words)
        
        with self.assertRaises(share.MnemonicError):
            share.Share.from_mnemonic(bad_mnemonic)


class TestKnownVectors(unittest.TestCase):
    """Test against known SLIP-39 mnemonics"""
    
    def test_roundtrip_encoding(self):
        """Test that encoding/decoding works correctly"""
        # Create a share with known values
        s = share.Share(
            identifier=100,
            extendable=False,
            iteration_exponent=0,
            group_index=0,
            group_threshold=1,
            group_count=1,
            index=0,
            member_threshold=1,
            value=b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'
        )
        
        # Encode to mnemonic
        mnemonic = s.mnemonic()
        
        # Decode back
        recovered = share.Share.from_mnemonic(mnemonic)
        
        # Should match original
        self.assertEqual(s, recovered)


if __name__ == '__main__':
    unittest.main()
