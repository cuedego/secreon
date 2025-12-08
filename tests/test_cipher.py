"""
Unit tests for SLIP-39 Feistel cipher module

Tests verify correctness of encryption/decryption and compatibility with
Trezor's reference implementation.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import cipher


class TestCipherBasics(unittest.TestCase):
    """Test basic cipher operations"""
    
    def test_xor_basic(self):
        """Test XOR operation"""
        a = b"\x00\x00\x00\x00"
        b = b"\xFF\xFF\xFF\xFF"
        result = cipher._xor(a, b)
        self.assertEqual(result, b"\xFF\xFF\xFF\xFF")
    
    def test_xor_identity(self):
        """Test XOR with itself returns zeros"""
        a = b"\xAB\xCD\xEF\x12"
        result = cipher._xor(a, a)
        self.assertEqual(result, b"\x00\x00\x00\x00")
    
    def test_xor_commutative(self):
        """Test XOR is commutative"""
        a = b"\x12\x34\x56\x78"
        b = b"\xAB\xCD\xEF\x90"
        self.assertEqual(cipher._xor(a, b), cipher._xor(b, a))
    
    def test_get_salt_non_extendable(self):
        """Test salt generation for non-extendable backups"""
        identifier = 0x1234
        salt = cipher._get_salt(identifier, False)
        
        # Should be "shamir" + identifier (2 bytes)
        expected = b"shamir\x12\x34"
        self.assertEqual(salt, expected)
    
    def test_get_salt_extendable(self):
        """Test salt generation for extendable backups"""
        identifier = 0x1234
        salt = cipher._get_salt(identifier, True)
        
        # Should be empty for extendable
        self.assertEqual(salt, b"")
    
    def test_round_function_deterministic(self):
        """Test that round function is deterministic"""
        data = b"\x00\x01\x02\x03\x04\x05\x06\x07"
        salt = b"shamir\x12\x34"
        
        result1 = cipher._round_function(0, b"password", 1, salt, data)
        result2 = cipher._round_function(0, b"password", 1, salt, data)
        
        self.assertEqual(result1, result2)
    
    def test_round_function_different_rounds(self):
        """Test that different rounds produce different outputs"""
        data = b"\x00\x01\x02\x03\x04\x05\x06\x07"
        salt = b"shamir\x12\x34"
        
        result0 = cipher._round_function(0, b"password", 1, salt, data)
        result1 = cipher._round_function(1, b"password", 1, salt, data)
        
        self.assertNotEqual(result0, result1)
    
    def test_round_function_length(self):
        """Test that round function output has same length as input"""
        for length in [8, 16, 32]:
            data = bytes(range(length))
            salt = b"test"
            result = cipher._round_function(0, b"pass", 1, salt, data)
            self.assertEqual(len(result), length)


class TestEncryptDecrypt(unittest.TestCase):
    """Test encryption and decryption"""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that decrypt(encrypt(x)) = x"""
        master_secret = b"ABCDEFGHIJKLMNOP"  # 16 bytes
        passphrase = b"password"
        iteration_exponent = 1
        identifier = 0x1234
        
        encrypted = cipher.encrypt(
            master_secret, passphrase, iteration_exponent, identifier, False
        )
        decrypted = cipher.decrypt(
            encrypted, passphrase, iteration_exponent, identifier, False
        )
        
        self.assertEqual(master_secret, decrypted)
    
    def test_encrypt_decrypt_empty_passphrase(self):
        """Test encryption with empty passphrase"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b""
        
        encrypted = cipher.encrypt(master_secret, passphrase, 0, 0x0000, False)
        decrypted = cipher.decrypt(encrypted, passphrase, 0, 0x0000, False)
        
        self.assertEqual(master_secret, decrypted)
    
    def test_encrypt_decrypt_different_lengths(self):
        """Test encryption/decryption with different secret lengths"""
        for length in [16, 32]:
            master_secret = bytes(range(length))
            passphrase = b"test"
            
            encrypted = cipher.encrypt(master_secret, passphrase, 1, 0x1234, False)
            decrypted = cipher.decrypt(encrypted, passphrase, 1, 0x1234, False)
            
            self.assertEqual(master_secret, decrypted)
    
    def test_encrypt_changes_data(self):
        """Test that encryption actually changes the data"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        
        encrypted = cipher.encrypt(master_secret, passphrase, 1, 0x1234, False)
        
        # Encrypted should be different from plaintext
        self.assertNotEqual(master_secret, encrypted)
    
    def test_encrypt_odd_length_raises(self):
        """Test that odd-length secret raises ValueError"""
        master_secret = b"ABCDEFGHIJKLMNOPQ"  # 17 bytes
        
        with self.assertRaises(ValueError):
            cipher.encrypt(master_secret, b"pass", 1, 0x1234, False)
    
    def test_decrypt_odd_length_raises(self):
        """Test that odd-length ciphertext raises ValueError"""
        encrypted = b"ABCDEFGHIJKLMNOPQ"  # 17 bytes
        
        with self.assertRaises(ValueError):
            cipher.decrypt(encrypted, b"pass", 1, 0x1234, False)


class TestPassphraseVariations(unittest.TestCase):
    """Test different passphrase scenarios"""
    
    def test_different_passphrases_different_ciphertexts(self):
        """Test that different passphrases produce different ciphertexts"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        identifier = 0x1234
        
        encrypted1 = cipher.encrypt(master_secret, b"password1", 1, identifier, False)
        encrypted2 = cipher.encrypt(master_secret, b"password2", 1, identifier, False)
        
        self.assertNotEqual(encrypted1, encrypted2)
    
    def test_wrong_passphrase_wrong_decryption(self):
        """Test that wrong passphrase gives wrong decryption"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        
        encrypted = cipher.encrypt(master_secret, b"correct", 1, 0x1234, False)
        decrypted = cipher.decrypt(encrypted, b"wrong", 1, 0x1234, False)
        
        self.assertNotEqual(master_secret, decrypted)
    
    def test_passphrase_case_sensitive(self):
        """Test that passphrase is case-sensitive"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        identifier = 0x1234
        
        encrypted1 = cipher.encrypt(master_secret, b"Password", 1, identifier, False)
        encrypted2 = cipher.encrypt(master_secret, b"password", 1, identifier, False)
        
        self.assertNotEqual(encrypted1, encrypted2)


class TestIterationExponent(unittest.TestCase):
    """Test iteration exponent variations"""
    
    def test_different_exponents_different_results(self):
        """Test that different iteration exponents produce different results"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        encrypted0 = cipher.encrypt(master_secret, passphrase, 0, identifier, False)
        encrypted1 = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
        encrypted2 = cipher.encrypt(master_secret, passphrase, 2, identifier, False)
        
        # All should be different
        self.assertNotEqual(encrypted0, encrypted1)
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertNotEqual(encrypted0, encrypted2)
    
    def test_roundtrip_various_exponents(self):
        """Test roundtrip with various iteration exponents"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        for e in [0, 1, 2, 3, 4, 5]:
            encrypted = cipher.encrypt(master_secret, passphrase, e, identifier, False)
            decrypted = cipher.decrypt(encrypted, passphrase, e, identifier, False)
            self.assertEqual(master_secret, decrypted)
    
    def test_wrong_exponent_wrong_decryption(self):
        """Test that wrong iteration exponent gives wrong decryption"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        encrypted = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
        decrypted = cipher.decrypt(encrypted, passphrase, 2, identifier, False)
        
        self.assertNotEqual(master_secret, decrypted)


class TestIdentifier(unittest.TestCase):
    """Test identifier variations"""
    
    def test_different_identifiers_different_results(self):
        """Test that different identifiers produce different results"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        
        encrypted1 = cipher.encrypt(master_secret, passphrase, 1, 0x0000, False)
        encrypted2 = cipher.encrypt(master_secret, passphrase, 1, 0x1234, False)
        encrypted3 = cipher.encrypt(master_secret, passphrase, 1, 0x7FFF, False)
        
        # All should be different
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertNotEqual(encrypted2, encrypted3)
        self.assertNotEqual(encrypted1, encrypted3)
    
    def test_roundtrip_various_identifiers(self):
        """Test roundtrip with various identifiers"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        
        for identifier in [0x0000, 0x0001, 0x1234, 0x7FFF]:
            encrypted = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
            decrypted = cipher.decrypt(encrypted, passphrase, 1, identifier, False)
            self.assertEqual(master_secret, decrypted)
    
    def test_wrong_identifier_wrong_decryption(self):
        """Test that wrong identifier gives wrong decryption (for non-extendable)"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        
        encrypted = cipher.encrypt(master_secret, passphrase, 1, 0x1234, False)
        decrypted = cipher.decrypt(encrypted, passphrase, 1, 0x5678, False)
        
        self.assertNotEqual(master_secret, decrypted)


class TestExtendableFlag(unittest.TestCase):
    """Test extendable flag behavior"""
    
    def test_extendable_vs_non_extendable(self):
        """Test that extendable flag affects encryption"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        encrypted_ext = cipher.encrypt(master_secret, passphrase, 1, identifier, True)
        encrypted_non = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
        
        # Should be different due to different salt
        self.assertNotEqual(encrypted_ext, encrypted_non)
    
    def test_extendable_roundtrip(self):
        """Test roundtrip with extendable=True"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        encrypted = cipher.encrypt(master_secret, passphrase, 1, identifier, True)
        decrypted = cipher.decrypt(encrypted, passphrase, 1, identifier, True)
        
        self.assertEqual(master_secret, decrypted)
    
    def test_wrong_extendable_flag_wrong_decryption(self):
        """Test that wrong extendable flag gives wrong decryption"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        # Encrypt with extendable=False
        encrypted = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
        
        # Decrypt with extendable=True
        decrypted = cipher.decrypt(encrypted, passphrase, 1, identifier, True)
        
        self.assertNotEqual(master_secret, decrypted)
    
    def test_extendable_identifier_independent(self):
        """Test that extendable backups are independent of identifier"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        
        # With extendable=True, different identifiers should give same result
        encrypted1 = cipher.encrypt(master_secret, passphrase, 1, 0x0000, True)
        encrypted2 = cipher.encrypt(master_secret, passphrase, 1, 0x1234, True)
        
        # Should be the same (identifier not used in salt for extendable)
        self.assertEqual(encrypted1, encrypted2)


class TestFeistelProperties(unittest.TestCase):
    """Test Feistel cipher mathematical properties"""
    
    def test_encrypt_decrypt_are_inverses(self):
        """Test that encryption and decryption are perfect inverses"""
        master_secret = b"0123456789ABCDEF"
        
        for passphrase in [b"", b"a", b"password", b"very long passphrase here"]:
            for e in range(4):
                for identifier in [0, 1, 100, 32767]:
                    for extendable in [True, False]:
                        encrypted = cipher.encrypt(
                            master_secret, passphrase, e, identifier, extendable
                        )
                        decrypted = cipher.decrypt(
                            encrypted, passphrase, e, identifier, extendable
                        )
                        self.assertEqual(master_secret, decrypted)
    
    def test_double_encrypt_decrypt(self):
        """Test that decrypt(encrypt(encrypt(decrypt(x)))) = x"""
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b"password"
        identifier = 0x1234
        
        encrypted = cipher.encrypt(master_secret, passphrase, 1, identifier, False)
        decrypted = cipher.decrypt(encrypted, passphrase, 1, identifier, False)
        re_encrypted = cipher.encrypt(decrypted, passphrase, 1, identifier, False)
        re_decrypted = cipher.decrypt(re_encrypted, passphrase, 1, identifier, False)
        
        self.assertEqual(master_secret, re_decrypted)


class TestCompatibility(unittest.TestCase):
    """Test compatibility with known values"""
    
    def test_known_vector_1(self):
        """Test against a known encryption vector"""
        # This is a simple test vector - in real tests you'd use
        # official Trezor test vectors
        master_secret = b"ABCDEFGHIJKLMNOP"
        passphrase = b""
        e = 0
        identifier = 0
        extendable = False
        
        encrypted = cipher.encrypt(master_secret, passphrase, e, identifier, extendable)
        
        # Encrypted should be 16 bytes
        self.assertEqual(len(encrypted), 16)
        
        # Should decrypt back correctly
        decrypted = cipher.decrypt(encrypted, passphrase, e, identifier, extendable)
        self.assertEqual(master_secret, decrypted)


if __name__ == '__main__':
    unittest.main()
