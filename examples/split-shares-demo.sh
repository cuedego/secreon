#!/usr/bin/env bash
set -euo pipefail

# Demo: generate split-share files from the sample seed and recover
TMPDIR="/tmp/secreon-demo-$$"
mkdir -p "$TMPDIR"

echo "Generating split shares from examples/sample-seed.txt into $TMPDIR..."
python3 secreon.py generate --secret-file examples/sample-seed.txt --minimum 3 --shares 5 --out "$TMPDIR/seed.json" --split-shares

echo
echo "List generated files:"
ls -lh "$TMPDIR"

echo
echo "Recovering from 3 specific share files (1,3,5):"
python3 secreon.py recover --shares-file "$TMPDIR/seed-1.json" "$TMPDIR/seed-3.json" "$TMPDIR/seed-5.json" --as-str

echo
echo "Recovering using directory scan (all files):"
python3 secreon.py recover --shares-dir "$TMPDIR" --as-str

echo
echo "Demo complete. Temporary files in: $TMPDIR"
