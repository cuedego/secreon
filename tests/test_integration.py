"""
End-to-end integration test for SLIP-39

Demonstrates the complete workflow from BIP-39 seed generation
through SLIP-39 share creation and recovery.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from slip39 import bip39, shamir


def test_complete_workflow():
    """Test complete SLIP-39 workflow"""
    
    print("SLIP-39 End-to-End Integration Test")
    print("=" * 50)
    
    # Step 1: Generate BIP-39 seed phrase (24 words)
    print("\n1. Generating BIP-39 seed phrase (24 words)...")
    bip39_mnemonic = bip39.generate_mnemonic(256)
    print(f"   BIP-39: {bip39_mnemonic[:50]}...")
    
    # Step 2: Convert BIP-39 to master secret (entropy)
    print("\n2. Converting to master secret...")
    master_secret, valid = bip39.mnemonic_to_entropy(bip39_mnemonic)
    assert valid, "BIP-39 mnemonic should be valid"
    print(f"   Master secret: {master_secret.hex()}")
    
    # Step 3: Generate SLIP-39 shares (2-of-3 groups)
    print("\n3. Generating SLIP-39 shares...")
    print("   Scheme: 2-of-3 groups")
    print("   - Group 1: 2-of-3 shares")
    print("   - Group 2: 3-of-5 shares")
    print("   - Group 3: 1-of-1 share (backup)")
    
    passphrase = b"my secure passphrase"
    groups = shamir.generate_mnemonics(
        group_threshold=2,
        groups=[(2, 3), (3, 5), (1, 1)],
        master_secret=master_secret,
        passphrase=passphrase,
        extendable=False,
        iteration_exponent=0
    )
    
    print(f"\n   Generated {len(groups)} groups:")
    for i, group in enumerate(groups):
        print(f"   - Group {i+1}: {len(group)} shares")
        print(f"     First share: {group[0][:50]}...")
    
    # Step 4: Recover using Group 1 + Group 2
    print("\n4. Recovering master secret...")
    print("   Using: 2 shares from Group 1 + 3 shares from Group 2")
    
    recovery_shares = groups[0][:2] + groups[1][:3]
    recovered_secret = shamir.combine_mnemonics(recovery_shares, passphrase)
    
    print(f"   Recovered: {recovered_secret.hex()}")
    
    # Step 5: Verify recovery
    print("\n5. Verifying recovery...")
    assert recovered_secret == master_secret, "Recovery failed!"
    print("   ✓ Master secret recovered successfully!")
    
    # Step 6: Convert back to BIP-39
    print("\n6. Converting back to BIP-39...")
    recovered_mnemonic = bip39.entropy_to_mnemonic(recovered_secret)
    assert recovered_mnemonic == bip39_mnemonic, "BIP-39 mnemonic mismatch!"
    print("   ✓ BIP-39 mnemonic matches original!")
    
    # Step 7: Test alternative recovery (Group 2 + Group 3)
    print("\n7. Testing alternative recovery path...")
    print("   Using: 3 shares from Group 2 + 1 share from Group 3")
    
    alt_recovery = groups[1][:3] + groups[2]
    alt_recovered = shamir.combine_mnemonics(alt_recovery, passphrase)
    assert alt_recovered == master_secret, "Alternative recovery failed!"
    print("   ✓ Alternative recovery successful!")
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! SLIP-39 implementation working correctly.")
    print("\nSummary:")
    print(f"  - Master secret: {len(master_secret)} bytes")
    print(f"  - Total shares generated: {sum(len(g) for g in groups)}")
    print(f"  - Groups required: 2 of 3")
    print(f"  - Passphrase protection: Yes")
    print(f"  - BIP-39 compatible: Yes")


def test_without_passphrase():
    """Test workflow without passphrase"""
    
    print("\n\nSimple SLIP-39 Test (No Passphrase)")
    print("=" * 50)
    
    # Generate simple 3-of-5 shares
    master_secret = b"ABCDEFGHIJKLMNOP"
    
    print("\n1. Generating 3-of-5 shares...")
    groups = shamir.generate_mnemonics(
        group_threshold=1,
        groups=[(3, 5)],
        master_secret=master_secret,
        passphrase=b"",
        extendable=True,
        iteration_exponent=0
    )
    
    print(f"   Generated {len(groups[0])} shares")
    
    # Recover with any 3
    print("\n2. Recovering with shares 1, 3, 5...")
    recovered = shamir.combine_mnemonics(
        [groups[0][0], groups[0][2], groups[0][4]]
    )
    
    assert recovered == master_secret, "Recovery failed!"
    print("   ✓ Recovery successful!")
    
    # Try with different combination
    print("\n3. Recovering with shares 2, 3, 4...")
    recovered2 = shamir.combine_mnemonics(groups[0][1:4])
    
    assert recovered2 == master_secret, "Recovery failed!"
    print("   ✓ Recovery successful!")
    
    print("\n" + "=" * 50)
    print("✓ Simple test passed!")


if __name__ == '__main__':
    try:
        test_complete_workflow()
        test_without_passphrase()
        print("\n" + "=" * 50)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
