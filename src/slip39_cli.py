#!/usr/bin/env python3
"""
SLIP-39 CLI commands for Secreon

Provides commands for generating and recovering SLIP-39 shares
"""

import sys
import os
import argparse
import json
from typing import List, Optional, Dict, Any
from pathlib import Path

# Import SLIP-39 implementation
from slip39 import (
    generate_mnemonics,
    combine_mnemonics,
    split_ems,
    recover_ems,
    EncryptedMasterSecret,
    MnemonicError,
    generate_mnemonic,
    mnemonic_to_seed,
    validate_mnemonic
)


def main():
    """Main entry point for SLIP-39 CLI"""
    prog_name = 'secreon slip39'
    argv = sys.argv[1:]  # Remove script name
    
    # Check if user wants help at top level
    if not argv or argv[0] in ['-h', '--help']:
        print_help()
        return 0
    
    # Get subcommand
    if argv[0] not in ['generate-seed', 'generate', 'recover', 'info', 'validate']:
        print(f"Unknown command: {argv[0]}", file=sys.stderr)
        print_help()
        return 2
    
    cmd = argv[0]
    rest = argv[1:]
    
    if cmd == 'generate-seed':
        return cmd_generate_seed(rest)
    elif cmd == 'generate':
        return cmd_generate(rest)
    elif cmd == 'recover':
        return cmd_recover(rest)
    elif cmd == 'info':
        return cmd_info(rest)
    elif cmd == 'validate':
        return cmd_validate(rest)
    
    return 0


def print_help():
    """Print top-level help"""
    help_text = """usage: secreon slip39 [-h] command

SLIP-39 Shamir's Secret Sharing for cryptocurrency wallets

positional arguments:
  generate-seed         Generate a new BIP-39 seed phrase
  generate              Generate SLIP-39 shares from a secret
  recover               Recover secret from SLIP-39 shares
  info                  Display information about SLIP-39 shares
  validate              Validate SLIP-39 share mnemonics

options:
  -h, --help            show this help message and exit

Examples:
  # Generate a new BIP-39 seed
  secreon slip39 generate-seed --words 24
  
  # Generate SLIP-39 shares from a BIP-39 seed
  secreon slip39 generate --bip39 "word1 word2 ... word24" --groups "2,3" "3,5" "1,1"
  
  # Recover secret from shares
  secreon slip39 recover --shares shares.json
"""
    print(help_text)


def cmd_generate_seed(argv: List[str]) -> int:
    """Generate a new BIP-39 seed phrase"""
    parser = argparse.ArgumentParser(
        prog='secreon slip39 generate-seed',
        description='Generate a new BIP-39 seed phrase'
    )
    parser.add_argument(
        '--words', '-w',
        type=int,
        choices=[12, 15, 18, 21, 24],
        default=24,
        help='Number of words in the seed phrase (default: 24)'
    )
    parser.add_argument(
        '--passphrase', '-p',
        help='Optional BIP-39 passphrase'
    )
    parser.add_argument(
        '--out', '-o',
        help='Output file for seed phrase (default: stdout)'
    )
    parser.add_argument(
        '--show-seed',
        action='store_true',
        help='Display the master seed (64 bytes hex) along with mnemonic'
    )
    
    args = parser.parse_args(argv)
    
    # Generate BIP-39 mnemonic
    try:
        mnemonic = generate_mnemonic(strength=(args.words * 32 // 3))
        
        output_lines = [f"BIP-39 Mnemonic ({args.words} words):", mnemonic]
        
        if args.show_seed:
            passphrase = args.passphrase or ''
            seed = mnemonic_to_seed(mnemonic, passphrase)
            output_lines.append("")
            output_lines.append(f"Master Seed (64 bytes):")
            output_lines.append(seed.hex())
        
        output = '\n'.join(output_lines)
        
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Seed phrase written to: {args.out}", file=sys.stderr)
        else:
            print(output)
        
        return 0
        
    except Exception as e:
        print(f"Error generating seed: {e}", file=sys.stderr)
        return 1


def cmd_generate(argv: List[str]) -> int:
    """Generate SLIP-39 shares from a secret"""
    parser = argparse.ArgumentParser(
        prog='secreon slip39 generate',
        description='Generate SLIP-39 shares from a secret'
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--bip39',
        help='BIP-39 mnemonic to split (24 words)'
    )
    input_group.add_argument(
        '--bip39-file',
        help='File containing BIP-39 mnemonic'
    )
    input_group.add_argument(
        '--secret',
        help='Secret as hex string (32 bytes = 64 hex chars)'
    )
    input_group.add_argument(
        '--secret-file',
        help='File containing secret (raw bytes)'
    )
    
    # Share generation options
    parser.add_argument(
        '--groups', '-g',
        nargs='+',
        required=True,
        help='Group specifications as "threshold,count" (e.g., "2,3" "3,5" "1,1")'
    )
    parser.add_argument(
        '--group-threshold', '-t',
        type=int,
        help='Number of groups required to recover (default: all groups)'
    )
    parser.add_argument(
        '--passphrase', '-p',
        help='Passphrase for encryption (optional but recommended)'
    )
    parser.add_argument(
        '--iteration-exponent', '-e',
        type=int,
        default=1,
        help='Iteration exponent for PBKDF2 (0-4, default: 1 = 5000 iterations/round)'
    )
    parser.add_argument(
        '--extendable',
        action='store_true',
        default=True,
        help='Create extendable backup (default: true)'
    )
    parser.add_argument(
        '--no-extendable',
        dest='extendable',
        action='store_false',
        help='Create non-extendable backup'
    )
    
    # Output options
    parser.add_argument(
        '--out', '-o',
        help='Output file for shares (JSON format, default: stdout)'
    )
    parser.add_argument(
        '--split-shares',
        action='store_true',
        help='Output each share to a separate file'
    )
    parser.add_argument(
        '--out-dir',
        help='Output directory for split shares (default: current directory)'
    )
    
    args = parser.parse_args(argv)
    
    try:
        # Parse input secret
        if args.bip39:
            mnemonic = args.bip39.strip()
            if not validate_mnemonic(mnemonic):
                print("Error: Invalid BIP-39 mnemonic", file=sys.stderr)
                return 1
            master_secret = mnemonic_to_seed(mnemonic, '')[:32]  # Use first 32 bytes
        elif args.bip39_file:
            with open(args.bip39_file, 'r', encoding='utf-8') as f:
                mnemonic = f.read().strip()
            if not validate_mnemonic(mnemonic):
                print("Error: Invalid BIP-39 mnemonic in file", file=sys.stderr)
                return 1
            master_secret = mnemonic_to_seed(mnemonic, '')[:32]
        elif args.secret:
            try:
                master_secret = bytes.fromhex(args.secret)
                if len(master_secret) != 32:
                    print("Error: Secret must be exactly 32 bytes (64 hex characters)", file=sys.stderr)
                    return 1
            except ValueError:
                print("Error: Invalid hex string for secret", file=sys.stderr)
                return 1
        elif args.secret_file:
            with open(args.secret_file, 'rb') as f:
                master_secret = f.read()
            if len(master_secret) != 32:
                print(f"Error: Secret file must contain exactly 32 bytes (found {len(master_secret)})", file=sys.stderr)
                return 1
        
        # Parse group specifications
        group_specs = []
        for spec in args.groups:
            try:
                parts = spec.split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid group spec: {spec}")
                threshold = int(parts[0])
                count = int(parts[1])
                if threshold < 1 or count < 1 or threshold > count:
                    raise ValueError(f"Invalid group spec: {spec} (threshold must be <= count)")
                group_specs.append((threshold, count))
            except Exception as e:
                print(f"Error parsing group spec '{spec}': {e}", file=sys.stderr)
                return 1
        
        # Determine group threshold
        group_threshold = args.group_threshold
        if group_threshold is None:
            group_threshold = len(group_specs)  # Require all groups by default
        
        if group_threshold < 1 or group_threshold > len(group_specs):
            print(f"Error: Group threshold must be between 1 and {len(group_specs)}", file=sys.stderr)
            return 1
        
        # Generate shares
        passphrase = args.passphrase or ''
        iteration_exponent = args.iteration_exponent
        extendable = args.extendable
        
        print(f"Generating SLIP-39 shares...", file=sys.stderr)
        print(f"  Groups: {len(group_specs)} ({group_threshold} required)", file=sys.stderr)
        for i, (t, n) in enumerate(group_specs, 1):
            print(f"  Group {i}: {t}-of-{n}", file=sys.stderr)
        
        mnemonics = generate_mnemonics(
            group_threshold=group_threshold,
            groups=group_specs,
            master_secret=master_secret,
            passphrase=passphrase.encode('utf-8'),
            iteration_exponent=iteration_exponent,
            extendable=extendable
        )
        
        # Prepare output
        output_data = {
            'version': '1.0',
            'type': 'slip39-shares',
            'group_threshold': group_threshold,
            'groups': []
        }
        
        for group_idx, group_mnemonics in enumerate(mnemonics, 1):
            threshold, count = group_specs[group_idx - 1]
            group_data = {
                'group_index': group_idx,
                'threshold': threshold,
                'count': count,
                'shares': [{'index': i, 'mnemonic': m} for i, m in enumerate(group_mnemonics, 1)]
            }
            output_data['groups'].append(group_data)
        
        # Output shares
        if args.split_shares:
            out_dir = args.out_dir or '.'
            os.makedirs(out_dir, exist_ok=True)
            
            for group_idx, group_data in enumerate(output_data['groups'], 1):
                for share in group_data['shares']:
                    filename = f"slip39-g{group_idx}-s{share['index']}.json"
                    filepath = os.path.join(out_dir, filename)
                    
                    share_data = {
                        'version': output_data['version'],
                        'type': 'slip39-share',
                        'group_threshold': output_data['group_threshold'],
                        'group_index': group_idx,
                        'group_threshold_this': group_data['threshold'],
                        'group_count_this': group_data['count'],
                        'share_index': share['index'],
                        'mnemonic': share['mnemonic']
                    }
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(share_data, f, indent=2)
            
            total_shares = sum(len(g['shares']) for g in output_data['groups'])
            print(f"\nGenerated {total_shares} shares in {len(output_data['groups'])} groups", file=sys.stderr)
            print(f"Output directory: {out_dir}", file=sys.stderr)
        else:
            output_json = json.dumps(output_data, indent=2)
            
            if args.out:
                with open(args.out, 'w', encoding='utf-8') as f:
                    f.write(output_json)
                print(f"\nShares written to: {args.out}", file=sys.stderr)
            else:
                print(output_json)
        
        return 0
        
    except MnemonicError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error generating shares: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_recover(argv: List[str]) -> int:
    """Recover secret from SLIP-39 shares"""
    parser = argparse.ArgumentParser(
        prog='secreon slip39 recover',
        description='Recover secret from SLIP-39 shares'
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--shares',
        nargs='+',
        help='JSON file(s) containing shares'
    )
    input_group.add_argument(
        '--shares-dir',
        help='Directory containing share files'
    )
    input_group.add_argument(
        '--mnemonics', '-m',
        nargs='+',
        help='Share mnemonics directly (space-separated)'
    )
    
    parser.add_argument(
        '--passphrase', '-p',
        help='Passphrase for decryption (if used during generation)'
    )
    parser.add_argument(
        '--out', '-o',
        help='Output file for recovered secret (default: stdout)'
    )
    parser.add_argument(
        '--format',
        choices=['hex', 'bip39'],
        default='hex',
        help='Output format: hex (default) or bip39 mnemonic'
    )
    
    args = parser.parse_args(argv)
    
    try:
        # Collect share mnemonics
        mnemonics = []
        
        if args.mnemonics:
            # Direct mnemonic input
            mnemonics = args.mnemonics
        elif args.shares:
            # Load from JSON file(s)
            for filepath in args.shares:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('type') == 'slip39-share':
                    # Single share file
                    mnemonics.append(data['mnemonic'])
                elif data.get('type') == 'slip39-shares':
                    # Multiple shares file
                    for group in data.get('groups', []):
                        for share in group.get('shares', []):
                            mnemonics.append(share['mnemonic'])
                else:
                    print(f"Warning: Unknown share file format in {filepath}", file=sys.stderr)
        elif args.shares_dir:
            # Load all share files from directory
            share_files = sorted(Path(args.shares_dir).glob('*.json'))
            if not share_files:
                print(f"Error: No JSON files found in {args.shares_dir}", file=sys.stderr)
                return 1
            
            for filepath in share_files:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('type') in ['slip39-share', 'slip39-shares']:
                    if 'mnemonic' in data:
                        mnemonics.append(data['mnemonic'])
                    elif 'groups' in data:
                        for group in data['groups']:
                            for share in group.get('shares', []):
                                mnemonics.append(share['mnemonic'])
        
        if not mnemonics:
            print("Error: No share mnemonics found", file=sys.stderr)
            return 1
        
        print(f"Attempting to recover secret from {len(mnemonics)} shares...", file=sys.stderr)
        
        # Recover the secret
        passphrase = args.passphrase or ''
        master_secret = combine_mnemonics(mnemonics, passphrase.encode('utf-8'))
        
        # Format output
        if args.format == 'hex':
            output = master_secret.hex()
        elif args.format == 'bip39':
            # Convert secret back to BIP-39 (this is a reconstruction, may not match original)
            print("\nWarning: Converting to BIP-39 will generate a new mnemonic", file=sys.stderr)
            print("This may not match the original BIP-39 phrase if one was used.", file=sys.stderr)
            # For proper BIP-39 recovery, we'd need to store entropy, not just the seed
            output = f"Secret (hex): {master_secret.hex()}"
        else:
            output = master_secret.hex()
        
        # Write output
        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\nSecret recovered and written to: {args.out}", file=sys.stderr)
        else:
            print(f"\nRecovered secret:")
            print(output)
        
        print(f"\n✓ Secret recovered successfully!", file=sys.stderr)
        return 0
        
    except MnemonicError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error recovering secret: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def cmd_info(argv: List[str]) -> int:
    """Display information about SLIP-39 shares"""
    parser = argparse.ArgumentParser(
        prog='secreon slip39 info',
        description='Display information about SLIP-39 shares without recovering the secret'
    )
    
    parser.add_argument(
        'mnemonic',
        nargs='?',
        help='SLIP-39 share mnemonic to inspect'
    )
    parser.add_argument(
        '--file', '-f',
        help='JSON file containing share'
    )
    
    args = parser.parse_args(argv)
    
    try:
        from slip39.share import Share
        
        # Get mnemonic
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            mnemonic = data.get('mnemonic')
            if not mnemonic:
                print("Error: No mnemonic found in file", file=sys.stderr)
                return 1
        elif args.mnemonic:
            mnemonic = args.mnemonic
        else:
            print("Error: Provide a mnemonic or --file", file=sys.stderr)
            parser.print_help()
            return 1
        
        # Parse share
        share = Share.from_mnemonic(mnemonic)
        
        # Display information
        print("SLIP-39 Share Information")
        print("=" * 50)
        print(f"Identifier:          {share.identifier}")
        print(f"Iteration Exponent:  {share.iteration_exponent} ({(10000 * 2**share.iteration_exponent) // 4} iterations/round)")
        print(f"Group Index:         {share.group_index}")
        print(f"Group Threshold:     {share.group_threshold}")
        print(f"Group Count:         {share.group_count}")
        print(f"Member Index:        {share.index}")
        print(f"Member Threshold:    {share.member_threshold}")
        print(f"Value Length:        {len(share.value)} bytes")
        print(f"Extendable:          {'Yes' if share.extendable else 'No'}")
        print()
        print(f"Requirements:")
        print(f"  - Need {share.group_threshold} of {share.group_count} groups")
        print(f"  - This group needs {share.member_threshold} shares to reconstruct")
        
        return 0
        
    except MnemonicError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading share: {e}", file=sys.stderr)
        return 1


def cmd_validate(argv: List[str]) -> int:
    """Validate SLIP-39 share mnemonics"""
    parser = argparse.ArgumentParser(
        prog='secreon slip39 validate',
        description='Validate SLIP-39 share mnemonics'
    )
    
    parser.add_argument(
        'mnemonics',
        nargs='*',
        help='SLIP-39 share mnemonics to validate'
    )
    parser.add_argument(
        '--file', '-f',
        nargs='+',
        help='File(s) containing mnemonics or share JSON'
    )
    
    args = parser.parse_args(argv)
    
    try:
        from slip39.share import Share
        
        # Collect mnemonics
        mnemonics = []
        
        if args.file:
            for filepath in args.file:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Try to parse as JSON first
                try:
                    data = json.loads(content)
                    if 'mnemonic' in data:
                        mnemonics.append(data['mnemonic'])
                    elif 'groups' in data:
                        for group in data['groups']:
                            for share in group.get('shares', []):
                                mnemonics.append(share['mnemonic'])
                    else:
                        # Treat as plain text mnemonic
                        mnemonics.append(content)
                except json.JSONDecodeError:
                    # Not JSON, treat as plain text
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            mnemonics.append(line)
        
        if args.mnemonics:
            mnemonics.extend(args.mnemonics)
        
        if not mnemonics:
            print("Error: No mnemonics provided", file=sys.stderr)
            parser.print_help()
            return 1
        
        # Validate each mnemonic
        all_valid = True
        for i, mnemonic in enumerate(mnemonics, 1):
            try:
                share = Share.from_mnemonic(mnemonic)
                print(f"✓ Share {i}: Valid (ID={share.identifier}, Group={share.group_index}, Member={share.index})")
            except MnemonicError as e:
                print(f"✗ Share {i}: Invalid - {e}")
                all_valid = False
            except Exception as e:
                print(f"✗ Share {i}: Error - {e}")
                all_valid = False
        
        if all_valid:
            print(f"\n✓ All {len(mnemonics)} shares are valid")
            return 0
        else:
            print(f"\n✗ Some shares are invalid")
            return 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
