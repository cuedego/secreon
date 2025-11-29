"""
Unit tests for Shamir's Secret Sharing implementation.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import sss


def test_basic_share_generation_and_recovery():
    """Test that we can generate shares and recover the secret."""
    secret = 12345
    minimum = 3
    shares_count = 5
    
    shares = sss.make_random_shares(secret, minimum=minimum, shares=shares_count)
    
    assert len(shares) == shares_count
    
    # Recover with exactly minimum shares
    recovered = sss.recover_secret(shares[:minimum])
    assert recovered == secret
    
    # Recover with more than minimum
    recovered = sss.recover_secret(shares)
    assert recovered == secret
    
    # Recover with a different subset
    recovered = sss.recover_secret(shares[-minimum:])
    assert recovered == secret


def test_insufficient_shares_still_works_but_may_fail():
    """Test that recovery with fewer than minimum shares doesn't work correctly."""
    secret = 99999
    minimum = 4
    shares_count = 6
    
    shares = sss.make_random_shares(secret, minimum=minimum, shares=shares_count)
    
    # With minimum shares it should work
    recovered = sss.recover_secret(shares[:minimum])
    assert recovered == secret
    
    # With fewer shares, result will be wrong (not enough to determine polynomial)
    # This test just ensures it doesn't crash
    recovered_wrong = sss.recover_secret(shares[:2])
    # recovered_wrong will likely be different from secret


def test_json_serialization():
    """Test JSON serialization and deserialization of shares."""
    secret = 42
    minimum = 2
    shares_count = 4
    
    shares = sss.make_random_shares(secret, minimum=minimum, shares=shares_count)
    meta = {'minimum': minimum, 'shares': shares_count, 'prime': sss._PRIME}
    
    # Serialize
    json_str = sss._serialize_shares_json(shares, meta)
    
    # Deserialize
    recovered_shares, recovered_meta = sss._deserialize_shares_json(json_str)
    
    assert len(recovered_shares) == len(shares)
    assert recovered_meta['minimum'] == minimum
    assert recovered_meta['shares'] == shares_count
    
    # Recover secret from deserialized shares
    recovered_secret = sss.recover_secret(recovered_shares)
    assert recovered_secret == secret


def test_kdf_sha256():
    """Test SHA-256 KDF application."""
    passphrase = b'test passphrase'
    secret_int, meta = sss._kdf_apply('sha256', passphrase)
    
    assert isinstance(secret_int, int)
    assert secret_int > 0
    assert meta is not None
    assert meta['kdf'] == 'sha256'
    
    # Same passphrase should produce same result (deterministic)
    secret_int2, _ = sss._kdf_apply('sha256', passphrase)
    assert secret_int == secret_int2


def test_kdf_pbkdf2():
    """Test PBKDF2 KDF application."""
    passphrase = b'test passphrase'
    secret_int, meta = sss._kdf_apply('pbkdf2:100000', passphrase)
    
    assert isinstance(secret_int, int)
    assert secret_int > 0
    assert meta is not None
    assert meta['kdf'] == 'pbkdf2'
    assert meta['iterations'] == 100000
    assert 'salt' in meta
    
    # Different salt should produce different result
    secret_int2, meta2 = sss._kdf_apply('pbkdf2:100000', passphrase)
    assert secret_int != secret_int2  # Random salt makes it different


def test_no_kdf():
    """Test direct conversion without KDF."""
    data = b'hello world'
    secret_int, meta = sss._kdf_apply(None, data)
    
    assert isinstance(secret_int, int)
    assert meta is None
    
    # Should be equivalent to int.from_bytes
    expected = int.from_bytes(data, 'big')
    assert secret_int == expected


def test_string_secret_roundtrip():
    """Test that we can split and recover a string secret."""
    # Use a short string that fits within the prime
    original_str = 'Hello!'  # 6 bytes = 48 bits, well below 127-bit prime
    secret_bytes = original_str.encode('utf-8')
    secret_int = int.from_bytes(secret_bytes, 'big')
    original_len = len(secret_bytes)
    
    # Verify it's below the prime
    assert secret_int < sss._PRIME
    
    shares = sss.make_random_shares(secret_int, minimum=3, shares=5)
    recovered_int = sss.recover_secret(shares[:3])
    
    # Convert back to bytes and string - use original length to preserve leading zeros
    recovered_bytes = recovered_int.to_bytes(original_len, 'big')
    recovered_str = recovered_bytes.decode('utf-8')
    
    assert recovered_str == original_str


def test_cli_generate_and_recover_integration():
    """Integration test for generate and recover commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shares_file = os.path.join(tmpdir, 'shares.json')
        output_file = os.path.join(tmpdir, 'output.txt')
        
        # Generate shares with a short secret that fits in prime
        secret = 'test123'  # Short secret
        argv_gen = [
            '--secret', secret,
            '--minimum', '3',
            '--shares', '5',
            '--out', shares_file
        ]
        exit_code = sss.cmd_generate(argv_gen)
        assert exit_code == 0
        assert os.path.exists(shares_file)
        
        # Verify JSON structure
        with open(shares_file, 'r') as f:
            data = json.load(f)
        assert 'meta' in data
        assert 'shares' in data
        assert data['meta']['minimum'] == 3
        assert len(data['shares']) == 5
        assert 'secret_byte_length' in data['meta']
        
        # Recover secret as string directly
        argv_rec = [
            '--shares-file', shares_file,
            '--as-str',
            '--out', output_file
        ]
        exit_code = sss.cmd_recover(argv_rec)
        assert exit_code == 0
        
        with open(output_file, 'r') as f:
            recovered_str = f.read().strip()
        
        assert recovered_str == secret


def test_cli_generate_with_kdf():
    """Test CLI generate with KDF option."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shares_file = os.path.join(tmpdir, 'shares_kdf.json')
        
        # Use short passphrase; KDF output (32 bytes = 256 bits) exceeds 127-bit prime
        # So we need to use a custom larger prime or accept the validation error
        # Let's use a prime that's large enough (256-bit prime)
        large_prime = 2**256 - 189  # A large prime
        
        argv = [
            '--secret', 'short',  # Short passphrase
            '--kdf', 'pbkdf2:50000',
            '--prime', str(large_prime),
            '--out', shares_file
        ]
        exit_code = sss.cmd_generate(argv)
        assert exit_code == 0
        
        # Check KDF metadata is present
        with open(shares_file, 'r') as f:
            data = json.load(f)
        assert 'kdf' in data['meta']
        assert data['meta']['kdf']['kdf'] == 'pbkdf2'
        assert data['meta']['kdf']['iterations'] == 50000
        assert 'salt' in data['meta']['kdf']


def test_validation_minimum_greater_than_shares():
    """Test that validation catches minimum > shares."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shares_file = os.path.join(tmpdir, 'invalid.json')
        
        argv = [
            '--secret', 'test',
            '--minimum', '5',
            '--shares', '3',
            '--out', shares_file
        ]
        exit_code = sss.cmd_generate(argv)
        assert exit_code == 2  # Error exit code


def test_validation_duplicate_x_values():
    """Test that recovery detects duplicate x-values."""
    shares = [(1, 100), (1, 200), (2, 300)]
    shares_json = sss._serialize_shares_json(shares, {'minimum': 2, 'shares': 3, 'prime': sss._PRIME})
    
    with tempfile.TemporaryDirectory() as tmpdir:
        shares_file = os.path.join(tmpdir, 'dup.json')
        with open(shares_file, 'w') as f:
            f.write(shares_json)
        
        argv = ['--shares-file', shares_file]
        exit_code = sss.cmd_recover(argv)
        assert exit_code == 2  # Error due to duplicate x-values


if __name__ == '__main__':
    # Run all tests
    import traceback
    
    tests = [
        test_basic_share_generation_and_recovery,
        test_insufficient_shares_still_works_but_may_fail,
        test_json_serialization,
        test_kdf_sha256,
        test_kdf_pbkdf2,
        test_no_kdf,
        test_string_secret_roundtrip,
        test_cli_generate_and_recover_integration,
        test_cli_generate_with_kdf,
        test_validation_minimum_greater_than_shares,
        test_validation_duplicate_x_values,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
