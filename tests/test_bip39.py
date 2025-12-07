"""
Unit tests for BIP-39 mnemonic module

Tests verify correctness against BIP-39 specification and test vectors.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import bip39


class TestBIP39Wordlist(unittest.TestCase):
    """Test BIP-39 wordlist structure"""
    
    def test_wordlist_length(self):
        """Test that wordlist has exactly 2048 words"""
        self.assertEqual(len(bip39.WORDLIST), 2048)
    
    def test_wordlist_unique(self):
        """Test that all words are unique"""
        self.assertEqual(len(set(bip39.WORDLIST)), 2048)
    
    def test_wordlist_sorted(self):
        """Test that words are sorted alphabetically"""
        self.assertEqual(bip39.WORDLIST, sorted(bip39.WORDLIST))
    
    def test_first_word(self):
        """Test first word is 'abandon'"""
        self.assertEqual(bip39.WORDLIST[0], "abandon")
    
    def test_last_word(self):
        """Test last word is 'zoo'"""
        self.assertEqual(bip39.WORDLIST[-1], "zoo")
    
    def test_specific_words(self):
        """Test that specific known words are present"""
        known_words = ["abandon", "ability", "satoshi", "zero", "zoo"]
        for word in known_words:
            self.assertIn(word, bip39.WORDLIST)


class TestMnemonicGeneration(unittest.TestCase):
    """Test mnemonic generation"""
    
    def test_generate_128_bits(self):
        """Test generating 12-word mnemonic (128 bits)"""
        mnemonic = bip39.generate_mnemonic(128)
        words = mnemonic.split()
        self.assertEqual(len(words), 12)
    
    def test_generate_256_bits(self):
        """Test generating 24-word mnemonic (256 bits)"""
        mnemonic = bip39.generate_mnemonic(256)
        words = mnemonic.split()
        self.assertEqual(len(words), 24)
    
    def test_generate_default(self):
        """Test default generation (256 bits)"""
        mnemonic = bip39.generate_mnemonic()
        words = mnemonic.split()
        self.assertEqual(len(words), 24)
    
    def test_generate_invalid_strength(self):
        """Test that invalid strength raises error"""
        with self.assertRaises(ValueError):
            bip39.generate_mnemonic(100)
        with self.assertRaises(ValueError):
            bip39.generate_mnemonic(512)
    
    def test_generated_mnemonic_valid(self):
        """Test that generated mnemonics are valid"""
        for strength in [128, 160, 192, 224, 256]:
            mnemonic = bip39.generate_mnemonic(strength)
            self.assertTrue(bip39.validate_mnemonic(mnemonic))
    
    def test_generated_mnemonics_different(self):
        """Test that generated mnemonics are different (random)"""
        mnemonics = [bip39.generate_mnemonic(256) for _ in range(10)]
        # All should be unique
        self.assertEqual(len(set(mnemonics)), 10)


class TestEntropyConversion(unittest.TestCase):
    """Test entropy to/from mnemonic conversion"""
    
    def test_entropy_to_mnemonic_128(self):
        """Test converting 128-bit entropy to mnemonic"""
        entropy = bytes([0] * 16)  # 128 bits of zeros
        mnemonic = bip39.entropy_to_mnemonic(entropy)
        words = mnemonic.split()
        self.assertEqual(len(words), 12)
    
    def test_entropy_to_mnemonic_256(self):
        """Test converting 256-bit entropy to mnemonic"""
        entropy = bytes([0] * 32)  # 256 bits of zeros
        mnemonic = bip39.entropy_to_mnemonic(entropy)
        words = mnemonic.split()
        self.assertEqual(len(words), 24)
    
    def test_entropy_to_mnemonic_invalid_length(self):
        """Test that invalid entropy length raises error"""
        with self.assertRaises(ValueError):
            bip39.entropy_to_mnemonic(bytes([0] * 10))
    
    def test_mnemonic_to_entropy_roundtrip(self):
        """Test entropy -> mnemonic -> entropy roundtrip"""
        original_entropy = bytes([i % 256 for i in range(32)])
        mnemonic = bip39.entropy_to_mnemonic(original_entropy)
        recovered_entropy, valid = bip39.mnemonic_to_entropy(mnemonic)
        
        self.assertTrue(valid)
        self.assertEqual(original_entropy, recovered_entropy)
    
    def test_mnemonic_to_entropy_invalid_word_count(self):
        """Test that invalid word count raises error"""
        with self.assertRaises(ValueError):
            bip39.mnemonic_to_entropy("word1 word2 word3")
    
    def test_mnemonic_to_entropy_invalid_word(self):
        """Test that invalid word raises error"""
        # 12 words, but one is invalid
        mnemonic = " ".join(["abandon"] * 11 + ["notaword"])
        with self.assertRaises(ValueError):
            bip39.mnemonic_to_entropy(mnemonic)


class TestMnemonicValidation(unittest.TestCase):
    """Test mnemonic validation"""
    
    def test_validate_valid_mnemonic(self):
        """Test validation of known valid mnemonic"""
        # Known valid 12-word BIP-39 mnemonic
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        self.assertTrue(bip39.validate_mnemonic(mnemonic))
    
    def test_validate_invalid_checksum(self):
        """Test that invalid checksum is detected"""
        # Last word wrong (checksum invalid)
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
        self.assertFalse(bip39.validate_mnemonic(mnemonic))
    
    def test_validate_invalid_word(self):
        """Test that invalid word is detected"""
        mnemonic = "abandon abandon abandon notaword abandon abandon abandon abandon abandon abandon abandon about"
        self.assertFalse(bip39.validate_mnemonic(mnemonic))
    
    def test_validate_invalid_length(self):
        """Test that invalid length is detected"""
        mnemonic = "abandon abandon abandon"
        self.assertFalse(bip39.validate_mnemonic(mnemonic))
    
    def test_validate_generated_mnemonics(self):
        """Test that all generated mnemonics are valid"""
        for _ in range(10):
            mnemonic = bip39.generate_mnemonic(256)
            self.assertTrue(bip39.validate_mnemonic(mnemonic))


class TestBIP39TestVectors(unittest.TestCase):
    """Test against official BIP-39 test vectors"""
    
    def test_vector_1(self):
        """Test vector 1: all zeros entropy"""
        entropy = bytes([0] * 16)
        expected_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        
        mnemonic = bip39.entropy_to_mnemonic(entropy)
        self.assertEqual(mnemonic, expected_mnemonic)
        
        recovered, valid = bip39.mnemonic_to_entropy(mnemonic)
        self.assertTrue(valid)
        self.assertEqual(entropy, recovered)
    
    def test_vector_2(self):
        """Test vector 2: all 0xFF entropy"""
        entropy = bytes([0xFF] * 16)
        mnemonic = bip39.entropy_to_mnemonic(entropy)
        
        # Should be 12 words
        self.assertEqual(len(mnemonic.split()), 12)
        
        # Should validate
        self.assertTrue(bip39.validate_mnemonic(mnemonic))
        
        # Roundtrip should work
        recovered, valid = bip39.mnemonic_to_entropy(mnemonic)
        self.assertTrue(valid)
        self.assertEqual(entropy, recovered)
    
    def test_vector_3(self):
        """Test vector 3: sequential bytes"""
        entropy = bytes(range(16))
        mnemonic = bip39.entropy_to_mnemonic(entropy)
        
        self.assertTrue(bip39.validate_mnemonic(mnemonic))
        
        recovered, valid = bip39.mnemonic_to_entropy(mnemonic)
        self.assertTrue(valid)
        self.assertEqual(entropy, recovered)


class TestSeedGeneration(unittest.TestCase):
    """Test BIP-39 seed generation"""
    
    def test_mnemonic_to_seed_length(self):
        """Test that seed is 64 bytes (512 bits)"""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        seed = bip39.mnemonic_to_seed(mnemonic)
        self.assertEqual(len(seed), 64)
    
    def test_mnemonic_to_seed_deterministic(self):
        """Test that seed generation is deterministic"""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        seed1 = bip39.mnemonic_to_seed(mnemonic)
        seed2 = bip39.mnemonic_to_seed(mnemonic)
        self.assertEqual(seed1, seed2)
    
    def test_mnemonic_to_seed_with_passphrase(self):
        """Test seed generation with passphrase"""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        seed_no_pass = bip39.mnemonic_to_seed(mnemonic, "")
        seed_with_pass = bip39.mnemonic_to_seed(mnemonic, "mypassphrase")
        
        # Seeds should be different
        self.assertNotEqual(seed_no_pass, seed_with_pass)
    
    def test_mnemonic_to_seed_official_vector(self):
        """Test against official BIP-39 test vector"""
        mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        seed = bip39.mnemonic_to_seed(mnemonic, "TREZOR")
        
        # Expected seed from BIP-39 specification
        expected_hex = "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
        expected_seed = bytes.fromhex(expected_hex)
        
        self.assertEqual(seed, expected_seed)
    
    def test_seed_from_generated_mnemonic(self):
        """Test seed generation from generated mnemonic"""
        mnemonic = bip39.generate_mnemonic(256)
        seed = bip39.mnemonic_to_seed(mnemonic)
        
        # Should be 64 bytes
        self.assertEqual(len(seed), 64)
        
        # Should be deterministic
        seed2 = bip39.mnemonic_to_seed(mnemonic)
        self.assertEqual(seed, seed2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_mnemonic_with_extra_whitespace(self):
        """Test mnemonic with extra whitespace"""
        mnemonic = "  abandon   abandon  abandon  abandon  abandon abandon abandon abandon abandon abandon abandon about  "
        self.assertTrue(bip39.validate_mnemonic(mnemonic))
    
    def test_mnemonic_case_insensitive(self):
        """Test that mnemonic validation is case-insensitive"""
        mnemonic_lower = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
        mnemonic_upper = "ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABANDON ABOUT"
        mnemonic_mixed = "Abandon Abandon Abandon Abandon Abandon Abandon Abandon Abandon Abandon Abandon Abandon About"
        
        self.assertTrue(bip39.validate_mnemonic(mnemonic_lower))
        self.assertTrue(bip39.validate_mnemonic(mnemonic_upper))
        self.assertTrue(bip39.validate_mnemonic(mnemonic_mixed))
    
    def test_different_word_counts(self):
        """Test generation and validation of different word counts"""
        strengths = {128: 12, 160: 15, 192: 18, 224: 21, 256: 24}
        
        for strength, expected_words in strengths.items():
            mnemonic = bip39.generate_mnemonic(strength)
            words = mnemonic.split()
            self.assertEqual(len(words), expected_words)
            self.assertTrue(bip39.validate_mnemonic(mnemonic))


if __name__ == '__main__':
    unittest.main()
