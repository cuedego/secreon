#!/bin/bash
# SLIP-39 CLI Demo Script
# Demonstrates all SLIP-39 commands in secreon

set -e  # Exit on error

# Find Python - prefer venv if available
if [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

SECREON="$PYTHON secreon.py"
TMPDIR="/tmp/slip39-demo-$$"

echo "=================================="
echo "SLIP-39 CLI Demo"
echo "=================================="
echo ""

# Create temp directory
mkdir -p "$TMPDIR"
echo "Using temporary directory: $TMPDIR"
echo ""

# Clean up on exit
trap "rm -rf $TMPDIR" EXIT

echo "Step 1: Generate a new BIP-39 seed phrase"
echo "==========================================z"
$SECREON slip39 generate-seed --words 24 --out "$TMPDIR/seed.txt"
echo "✓ Seed phrase saved to: $TMPDIR/seed.txt"
echo ""

# Read the seed
BIP39_SEED=$(cat "$TMPDIR/seed.txt" | tail -1)
echo "Generated seed: ${BIP39_SEED:0:50}..."
echo ""

echo "Step 2: Generate SLIP-39 shares from BIP-39 seed"
echo "================================================="
echo "Configuration:"
echo "  - Group 1: 2-of-3 shares"
echo "  - Group 2: 3-of-5 shares"
echo "  - Group threshold: 2 (need both groups)"
echo "  - Passphrase: 'MySecurePassword'"
echo ""

$SECREON slip39 generate \
    --bip39 "$BIP39_SEED" \
    --groups "2,3" "3,5" \
    --group-threshold 2 \
    --passphrase "MySecurePassword" \
    --split-shares \
    --out-dir "$TMPDIR/shares"

echo "✓ Shares generated in: $TMPDIR/shares"
echo ""

echo "Step 3: List generated share files"
echo "==================================="
ls -1 "$TMPDIR/shares/"
echo ""

echo "Step 4: Display info for a single share"
echo "========================================"
SHARE1_FILE="$TMPDIR/shares/slip39-g1-s1.json"
SHARE1_MNEMONIC=$(cat "$SHARE1_FILE" | $PYTHON -c "import json,sys; print(json.load(sys.stdin)['mnemonic'])")
$SECREON slip39 info "$SHARE1_MNEMONIC"
echo ""

echo "Step 5: Validate all shares"
echo "============================"
$SECREON slip39 validate -f "$TMPDIR"/shares/*.json
echo ""

echo "Step 6: Recover secret from minimum shares"
echo "==========================================="
echo "Using 2 shares from Group 1 and 3 shares from Group 2"
$SECREON slip39 recover \
    --passphrase "MySecurePassword" \
    --shares \
        "$TMPDIR/shares/slip39-g1-s1.json" \
        "$TMPDIR/shares/slip39-g1-s2.json" \
        "$TMPDIR/shares/slip39-g2-s1.json" \
        "$TMPDIR/shares/slip39-g2-s2.json" \
        "$TMPDIR/shares/slip39-g2-s3.json" \
    --out "$TMPDIR/recovered.txt"

echo "✓ Secret recovered to: $TMPDIR/recovered.txt"
echo ""

echo "Step 7: Simple single-group example"
echo "===================================="
echo "Generating 3-of-5 shares for a hex secret..."

$SECREON slip39 generate \
    --secret "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" \
    --groups "3,5" \
    --passphrase "simple" \
    --out "$TMPDIR/simple-shares.json"

echo "✓ Simple shares generated"
echo ""

echo "Step 8: Recover from simple shares"
echo "==================================="
# Extract 3 mnemonics from the JSON
$PYTHON -c "
import json
data = json.load(open('$TMPDIR/simple-shares.json'))
mnemonics = [s['mnemonic'] for s in data['groups'][0]['shares'][:3]]
print(' '.join(['\"' + m + '\"' for m in mnemonics]))
" > "$TMPDIR/simple-mnemonics.txt"

MNEMONICS=$(cat "$TMPDIR/simple-mnemonics.txt")
eval "$SECREON slip39 recover --passphrase 'simple' -m $MNEMONICS"
echo ""

echo "=================================="
echo "✓ All SLIP-39 CLI features tested!"
echo "=================================="
echo ""
echo "Summary of commands demonstrated:"
echo "  - generate-seed: Create new BIP-39 seed"
echo "  - generate:      Split secret into SLIP-39 shares"
echo "  - recover:       Reconstruct secret from shares"
echo "  - info:          Display share metadata"
echo "  - validate:      Check share validity"
echo ""
echo "For more information:"
echo "  $SECREON slip39 --help"
echo "  $SECREON slip39 <command> --help"
