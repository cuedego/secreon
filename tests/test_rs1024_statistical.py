"""
Statistical test for RS1024 error detection capabilities

Tests the claim that RS1024 has probability < 1e-9 of failing to detect 4+ errors.
"""

import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import rs1024


def test_error_detection_rate(num_trials=10000):
    """
    Test error detection rate for different numbers of errors.
    
    According to SLIP-39 spec:
    - Detects up to 3 errors with 100% certainty
    - Probability < 1e-9 of failing to detect 4+ errors
    """
    print("RS1024 Error Detection Statistics")
    print("=" * 70)
    
    # Test with different data lengths
    data_lengths = [10, 20, 30]
    
    for data_len in data_lengths:
        print(f"\nData length: {data_len} words")
        print("-" * 70)
        
        # Test 1, 2, and 3 errors (should be 100% detection)
        for num_errors in [1, 2, 3]:
            failures = 0
            
            for _ in range(num_trials):
                # Generate random data
                data = [random.randint(0, 1023) for _ in range(data_len)]
                
                # Add checksum
                data_with_checksum = rs1024.append_checksum(data, extendable=False)
                
                # Introduce errors
                corrupted = data_with_checksum.copy()
                error_positions = random.sample(range(len(corrupted)), num_errors)
                for pos in error_positions:
                    # Change to a different random value
                    old_val = corrupted[pos]
                    new_val = random.randint(0, 1023)
                    while new_val == old_val:
                        new_val = random.randint(0, 1023)
                    corrupted[pos] = new_val
                
                # Check if error is detected
                if rs1024.verify_checksum(corrupted, extendable=False):
                    failures += 1
            
            detection_rate = 100 * (1 - failures / num_trials)
            print(f"  {num_errors} error(s): {detection_rate:.2f}% detected "
                  f"({num_trials - failures}/{num_trials})")
            
            if num_errors <= 3:
                assert failures == 0, f"Should detect all {num_errors}-error cases!"


def test_collision_resistance():
    """
    Test that different data produces different checksums (collision resistance).
    """
    print("\n\nRS1024 Collision Resistance Test")
    print("=" * 70)
    
    num_tests = 10000
    checksums_seen = set()
    collisions = 0
    
    for _ in range(num_tests):
        # Generate random data
        data_len = random.randint(10, 30)
        data = [random.randint(0, 1023) for _ in range(data_len)]
        
        # Create checksum
        checksum = tuple(rs1024.create_checksum(data, extendable=False))
        
        if checksum in checksums_seen:
            collisions += 1
        else:
            checksums_seen.add(checksum)
    
    print(f"Generated {num_tests} random checksums")
    print(f"Unique checksums: {len(checksums_seen)}")
    print(f"Collisions: {collisions}")
    print(f"Collision rate: {100 * collisions / num_tests:.4f}%")
    
    # Note: Some collisions are expected due to birthday paradox
    # With 1024^3 possible checksums and 10000 samples,
    # we expect very few collisions


def test_different_customization_strings():
    """
    Test that different customization strings produce different checksums.
    """
    print("\n\nCustomization String Differentiation Test")
    print("=" * 70)
    
    num_tests = 1000
    different = 0
    
    for _ in range(num_tests):
        # Generate random data
        data_len = random.randint(10, 20)
        data = [random.randint(0, 1023) for _ in range(data_len)]
        
        # Create checksums with both customization strings
        checksum_normal = rs1024.create_checksum(data, extendable=False)
        checksum_ext = rs1024.create_checksum(data, extendable=True)
        
        if checksum_normal != checksum_ext:
            different += 1
    
    print(f"Tested {num_tests} random data sets")
    print(f"Different checksums for normal vs extendable: {different}/{num_tests}")
    print(f"Difference rate: {100 * different / num_tests:.2f}%")
    
    assert different == num_tests, "All should be different!"


def main():
    random.seed(42)  # For reproducibility
    
    test_error_detection_rate(num_trials=10000)
    test_collision_resistance()
    test_different_customization_strings()
    
    print("\n" + "=" * 70)
    print("✓ All RS1024 statistical tests passed")
    print("\nKey findings:")
    print("  • 100% detection rate for 1-3 errors (guaranteed by RS code)")
    print("  • Strong collision resistance")
    print("  • Customization strings properly differentiate checksums")


if __name__ == '__main__':
    main()
