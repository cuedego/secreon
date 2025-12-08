#!/usr/bin/env python3
"""
Secreon - Shamir's Secret Sharing tool for secure secret management

Usage:
    # Classic SSS
    secreon generate --secret "my secret" --out shares.json
    secreon recover --shares-file shares.json --as-str
    
    # SLIP-39 (BIP-39 compatible)
    secreon slip39 generate-seed --words 24
    secreon slip39 generate --bip39 "word1 ... word24" --groups "2,3" "3,5"
    secreon slip39 recover --shares shares.json
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def main():
    """Main entry point - route to appropriate subcommand"""
    argv = sys.argv[1:]
    
    # Check if user wants slip39 commands
    if argv and argv[0] == 'slip39':
        from slip39_cli import main as slip39_main
        # Remove 'slip39' from argv for slip39_cli processing
        sys.argv = [sys.argv[0]] + argv[1:]
        return slip39_main()
    
    # Check for help at top level
    if not argv or argv[0] in ['-h', '--help']:
        print_main_help()
        return 0
    
    # Route to classic SSS
    if argv[0] in ['generate', 'recover']:
        from sss import main as sss_main
        return sss_main()
    
    # Unknown command
    print(f"Unknown command: {argv[0]}", file=sys.stderr)
    print_main_help()
    return 2


def print_main_help():
    """Print top-level help"""
    prog_name = 'secreon'
    help_text = f"""usage: {prog_name} [-h] command

Secreon - Shamir's Secret Sharing tool for secure secret management

positional arguments:
  generate              Generate shares from a secret (classic SSS)
  recover               Recover secret from shares (classic SSS)
  slip39                SLIP-39 commands for cryptocurrency wallets

options:
  -h, --help            show this help message and exit

Examples:
  # Classic Shamir's Secret Sharing
  {prog_name} generate --secret "my secret" --minimum 3 --shares 5
  {prog_name} recover --shares-file shares.json --as-str
  
  # SLIP-39 for cryptocurrency wallets
  {prog_name} slip39 generate-seed --words 24
  {prog_name} slip39 generate --bip39 "word1 ... word24" --groups "2,3" "3,5"
  {prog_name} slip39 recover --shares shares.json

For more information on a specific command:
  {prog_name} generate --help
  {prog_name} slip39 --help
"""
    print(help_text)


if __name__ == '__main__':
    sys.exit(main())
