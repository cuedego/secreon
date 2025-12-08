#!/usr/bin/env python3
"""
Test SLIP-39 implementation against official test vectors

These are the official test vectors from Trezor's python-shamir-mnemonic:
https://github.com/trezor/python-shamir-mnemonic/blob/master/vectors.json

Test vector format: [description, [mnemonics...], expected_secret_hex, expected_xprv]
- If expected_secret is empty string, the test should fail (invalid mnemonic)
- If expected_secret is non-empty, recovery should succeed and match
"""

import sys
import json
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import combine_mnemonics, MnemonicError


class TestOfficialVectors(unittest.TestCase):
    """Test against official SLIP-39 test vectors"""
    
    @classmethod
    def setUpClass(cls):
        """Load test vectors"""
        vector_file = Path(__file__).parent / 'slip39-vectors-corrected.json'
        with open(vector_file) as f:
            cls.vectors = json.load(f)
        print(f"\nLoaded {len(cls.vectors)} official test vectors")
    
    def test_all_vectors(self):
        """Test all official vectors"""
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for i, vector in enumerate(self.vectors, 1):
            description = vector[0]
            mnemonics = vector[1]
            expected_secret_hex = vector[2]
            expected_xprv = vector[3]  # We don't test XPRV derivation
            
            # Determine if this should be valid or invalid
            should_be_valid = bool(expected_secret_hex)
            
            try:
                # Attempt to recover secret
                recovered_secret = combine_mnemonics(mnemonics, b"")
                recovered_hex = recovered_secret.hex()
                
                if not should_be_valid:
                    # This should have failed but didn't
                    errors.append(f"Vector {i} ({description}): Expected failure but succeeded")
                    print(f"✗ Vector {i}: {description}")
                    print(f"  Expected: FAILURE")
                    print(f"  Got: {recovered_hex}")
                elif recovered_hex != expected_secret_hex:
                    # Valid but wrong result
                    errors.append(f"Vector {i} ({description}): Secret mismatch")
                    print(f"✗ Vector {i}: {description}")
                    print(f"  Expected: {expected_secret_hex}")
                    print(f"  Got:      {recovered_hex}")
                else:
                    # Success!
                    valid_count += 1
                    print(f"✓ Vector {i}: {description}")
                    
            except MnemonicError as e:
                if should_be_valid:
                    # This should have succeeded but failed
                    errors.append(f"Vector {i} ({description}): Expected success but failed: {e}")
                    print(f"✗ Vector {i}: {description}")
                    print(f"  Expected: {expected_secret_hex}")
                    print(f"  Got error: {e}")
                else:
                    # Expected failure
                    invalid_count += 1
                    print(f"✓ Vector {i}: {description} (correctly rejected)")
            except Exception as e:
                errors.append(f"Vector {i} ({description}): Unexpected error: {e}")
                print(f"✗ Vector {i}: {description}")
                print(f"  Unexpected error: {e}")
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"SUMMARY: {valid_count} valid, {invalid_count} invalid (correctly rejected)")
        print(f"Total vectors: {len(self.vectors)}")
        print(f"Passed: {valid_count + invalid_count}/{len(self.vectors)}")
        
        if errors:
            print(f"\nFAILED: {len(errors)} vectors")
            for error in errors:
                print(f"  - {error}")
            print("=" * 70)
            self.fail(f"{len(errors)} test vectors failed")
        else:
            print(f"✓ ALL {len(self.vectors)} VECTORS PASSED!")
            print("=" * 70)


def main():
    """Run tests"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
