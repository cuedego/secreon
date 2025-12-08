"""
Unit tests for SLIP-39 wordlist module

Tests verify the official wordlist and conversion functions.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import wordlist


class TestWordlistValidation(unittest.TestCase):
    """Test wordlist structure and properties"""
    
    def test_wordlist_length(self):
        """Test that wordlist has exactly 1024 words"""
        self.assertEqual(len(wordlist.WORDLIST), 1024)
    
    def test_wordlist_unique(self):
        """Test that all words are unique"""
        self.assertEqual(len(set(wordlist.WORDLIST)), 1024)
    
    def test_wordlist_sorted(self):
        """Test that words are sorted alphabetically"""
        self.assertEqual(wordlist.WORDLIST, sorted(wordlist.WORDLIST))
    
    def test_four_letter_prefixes_unique(self):
        """Test that all 4-letter prefixes are unique"""
        prefixes = [word[:4] for word in wordlist.WORDLIST]
        self.assertEqual(len(set(prefixes)), 1024)
    
    def test_validate_wordlist_function(self):
        """Test the validate_wordlist function"""
        self.assertTrue(wordlist.validate_wordlist())
    
    def test_first_word(self):
        """Test first word is 'academic'"""
        self.assertEqual(wordlist.WORDLIST[0], "academic")
    
    def test_last_word(self):
        """Test last word is 'zero'"""
        self.assertEqual(wordlist.WORDLIST[-1], "zero")


class TestWordToIndex(unittest.TestCase):
    """Test word to index conversion"""
    
    def test_first_word(self):
        """Test conversion of first word"""
        self.assertEqual(wordlist.word_to_index("academic"), 0)
    
    def test_last_word(self):
        """Test conversion of last word"""
        self.assertEqual(wordlist.word_to_index("zero"), 1023)
    
    def test_middle_word(self):
        """Test conversion of middle word"""
        idx = wordlist.word_to_index("machine")
        self.assertIsNotNone(idx)
        self.assertGreaterEqual(idx, 0)
        self.assertLess(idx, 1024)
    
    def test_case_insensitive(self):
        """Test that conversion is case-insensitive"""
        self.assertEqual(wordlist.word_to_index("ACADEMIC"), 0)
        self.assertEqual(wordlist.word_to_index("Academic"), 0)
        self.assertEqual(wordlist.word_to_index("aCaDeMiC"), 0)
    
    def test_four_letter_prefix(self):
        """Test that 4-letter prefix works"""
        full_idx = wordlist.word_to_index("academic")
        prefix_idx = wordlist.word_to_index("acad")
        self.assertEqual(full_idx, prefix_idx)
    
    def test_invalid_word(self):
        """Test that invalid word returns None"""
        self.assertIsNone(wordlist.word_to_index("notaword"))
        self.assertIsNone(wordlist.word_to_index("xyz"))
    
    def test_whitespace_handling(self):
        """Test that whitespace is handled"""
        self.assertEqual(wordlist.word_to_index("  academic  "), 0)


class TestIndexToWord(unittest.TestCase):
    """Test index to word conversion"""
    
    def test_first_index(self):
        """Test conversion of first index"""
        self.assertEqual(wordlist.index_to_word(0), "academic")
    
    def test_last_index(self):
        """Test conversion of last index"""
        self.assertEqual(wordlist.index_to_word(1023), "zero")
    
    def test_middle_index(self):
        """Test conversion of middle index"""
        word = wordlist.index_to_word(512)
        self.assertIsInstance(word, str)
        self.assertIn(word, wordlist.WORDLIST)
    
    def test_negative_index(self):
        """Test that negative index raises error"""
        with self.assertRaises(IndexError):
            wordlist.index_to_word(-1)
    
    def test_out_of_range_index(self):
        """Test that index >= 1024 raises error"""
        with self.assertRaises(IndexError):
            wordlist.index_to_word(1024)
        with self.assertRaises(IndexError):
            wordlist.index_to_word(2000)


class TestBidirectionalConversion(unittest.TestCase):
    """Test that conversions are reversible"""
    
    def test_word_to_index_to_word(self):
        """Test word -> index -> word roundtrip"""
        for word in ["academic", "machine", "zero", "python", "bitcoin"]:
            if word in wordlist.WORDLIST:
                idx = wordlist.word_to_index(word)
                recovered = wordlist.index_to_word(idx)
                self.assertEqual(word, recovered)
    
    def test_index_to_word_to_index(self):
        """Test index -> word -> index roundtrip"""
        for idx in [0, 100, 500, 1000, 1023]:
            word = wordlist.index_to_word(idx)
            recovered = wordlist.word_to_index(word)
            self.assertEqual(idx, recovered)
    
    def test_all_indices_bidirectional(self):
        """Test all indices are bidirectionally convertible"""
        for idx in range(1024):
            word = wordlist.index_to_word(idx)
            recovered_idx = wordlist.word_to_index(word)
            self.assertEqual(idx, recovered_idx)


class TestWordsIndicesConversion(unittest.TestCase):
    """Test bulk conversion functions"""
    
    def test_words_to_indices(self):
        """Test converting multiple words to indices"""
        words = ["academic", "acid", "acne"]
        indices = wordlist.words_to_indices(words)
        self.assertEqual(indices, [0, 1, 2])
    
    def test_indices_to_words(self):
        """Test converting multiple indices to words"""
        indices = [0, 1, 2]
        words = wordlist.indices_to_words(indices)
        self.assertEqual(words, ["academic", "acid", "acne"])
    
    def test_words_indices_roundtrip(self):
        """Test words -> indices -> words roundtrip"""
        original = ["academic", "machine", "zero"]
        indices = wordlist.words_to_indices(original)
        recovered = wordlist.indices_to_words(indices)
        self.assertEqual(original, recovered)
    
    def test_invalid_word_in_list(self):
        """Test that invalid word in list raises error"""
        with self.assertRaises(ValueError):
            wordlist.words_to_indices(["academic", "notaword", "zero"])


class TestMnemonicConversion(unittest.TestCase):
    """Test mnemonic phrase conversion"""
    
    def test_mnemonic_to_indices(self):
        """Test converting mnemonic phrase to indices"""
        mnemonic = "academic acid acne"
        indices = wordlist.mnemonic_to_indices(mnemonic)
        self.assertEqual(indices, [0, 1, 2])
    
    def test_indices_to_mnemonic(self):
        """Test converting indices to mnemonic phrase"""
        indices = [0, 1, 2]
        mnemonic = wordlist.indices_to_mnemonic(indices)
        self.assertEqual(mnemonic, "academic acid acne")
    
    def test_mnemonic_roundtrip(self):
        """Test mnemonic -> indices -> mnemonic roundtrip"""
        original = "academic machine zero python"
        indices = wordlist.mnemonic_to_indices(original)
        recovered = wordlist.indices_to_mnemonic(indices)
        self.assertEqual(original, recovered)
    
    def test_mnemonic_with_extra_whitespace(self):
        """Test mnemonic with extra whitespace"""
        mnemonic = "  academic   acid  acne  "
        indices = wordlist.mnemonic_to_indices(mnemonic)
        self.assertEqual(indices, [0, 1, 2])
    
    def test_long_mnemonic(self):
        """Test typical SLIP-39 mnemonic length (20-33 words)"""
        # Create a 20-word mnemonic
        indices = list(range(20))
        mnemonic = wordlist.indices_to_mnemonic(indices)
        
        # Should have 20 words
        self.assertEqual(len(mnemonic.split()), 20)
        
        # Roundtrip should work
        recovered = wordlist.mnemonic_to_indices(mnemonic)
        self.assertEqual(indices, recovered)


class TestIntegerConversion(unittest.TestCase):
    """Test integer to/from indices conversion"""
    
    def test_int_to_indices_simple(self):
        """Test converting small integer to indices"""
        # 5 in base-1024 with 3 words: [0, 0, 5]
        indices = wordlist.int_to_indices(5, 3)
        self.assertEqual(indices, [0, 0, 5])
    
    def test_int_to_indices_larger(self):
        """Test converting larger integer"""
        # 1025 = 1*1024 + 1 -> [1, 1]
        indices = wordlist.int_to_indices(1025, 2)
        self.assertEqual(indices, [1, 1])
    
    def test_indices_to_int_simple(self):
        """Test converting indices to integer"""
        value = wordlist.indices_to_int([0, 0, 5])
        self.assertEqual(value, 5)
    
    def test_indices_to_int_larger(self):
        """Test converting larger indices"""
        # [1, 1] = 1*1024 + 1 = 1025
        value = wordlist.indices_to_int([1, 1])
        self.assertEqual(value, 1025)
    
    def test_int_conversion_roundtrip(self):
        """Test integer conversion roundtrip"""
        for original in [0, 1, 100, 1024, 10000, 1000000]:
            word_count = 3  # Enough for values up to 1024^3-1
            indices = wordlist.int_to_indices(original, word_count)
            recovered = wordlist.indices_to_int(indices)
            self.assertEqual(original, recovered)
    
    def test_int_to_indices_negative(self):
        """Test that negative integer raises error"""
        with self.assertRaises(ValueError):
            wordlist.int_to_indices(-1, 3)
    
    def test_indices_to_int_out_of_range(self):
        """Test that out-of-range index raises error"""
        with self.assertRaises(ValueError):
            wordlist.indices_to_int([0, 1024])


class TestSpecificWords(unittest.TestCase):
    """Test specific known words from SLIP-39"""
    
    def test_satoshi_in_wordlist(self):
        """Test that 'satoshi' is in the wordlist"""
        idx = wordlist.word_to_index("satoshi")
        self.assertIsNotNone(idx)
        self.assertEqual(wordlist.index_to_word(idx), "satoshi")
    
    def test_bitcoin_not_in_wordlist(self):
        """Test that 'bitcoin' is NOT in SLIP-39 wordlist"""
        # Note: BIP-39 has 'bitcoin', but SLIP-39 does not
        idx = wordlist.word_to_index("bitcoin")
        self.assertIsNone(idx)
    
    def test_common_words(self):
        """Test several common words"""
        common = ["academic", "acquire", "algebra", "alpha", "amazing",
                  "simple", "sister", "solution", "space", "standard"]
        
        for word in common:
            if word in wordlist.WORDLIST:
                idx = wordlist.word_to_index(word)
                self.assertIsNotNone(idx, f"Word '{word}' should be in wordlist")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_mnemonic(self):
        """Test empty mnemonic"""
        indices = wordlist.mnemonic_to_indices("")
        self.assertEqual(indices, [])
    
    def test_single_word_mnemonic(self):
        """Test single-word mnemonic"""
        mnemonic = "academic"
        indices = wordlist.mnemonic_to_indices(mnemonic)
        self.assertEqual(indices, [0])
    
    def test_maximum_index_value(self):
        """Test maximum index value (1023)"""
        word = wordlist.index_to_word(1023)
        self.assertEqual(word, "zero")
        self.assertEqual(wordlist.word_to_index(word), 1023)
    
    def test_zero_integer_conversion(self):
        """Test converting zero"""
        indices = wordlist.int_to_indices(0, 3)
        self.assertEqual(indices, [0, 0, 0])
        value = wordlist.indices_to_int([0, 0, 0])
        self.assertEqual(value, 0)


if __name__ == '__main__':
    unittest.main()
