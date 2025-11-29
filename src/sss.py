"""
The following Python implementation of Shamir's secret sharing is
released into the Public Domain under the terms of CC0 and OWFa:
https://creativecommons.org/publicdomain/zero/1.0/
http://www.openwebfoundation.org/legal/the-owf-1-0-agreements/owfa-1-0

See the bottom few lines for usage. Tested on Python 2 and 3.
"""

from __future__ import division
from __future__ import print_function

import random
import functools
import json
import os
import sys
import argparse
import hashlib
import base64
from typing import List, Dict, Any, Optional

# Use a large Mersenne Prime suitable for BIP39 24-word mnemonics (~146 bytes = 1168 bits)
# 2^2203 - 1 is a Mersenne prime, provides plenty of headroom
_PRIME = 2 ** 2203 - 1

from typing import List, Dict, Any, Optional
_RINT = functools.partial(random.SystemRandom().randint, 0)

def _eval_at(poly, x, prime):
    """Evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    """
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def make_random_shares(secret, minimum, shares, prime=_PRIME):
    """
    Generates a random shamir pool for a given secret, returns share points.
    """
    if minimum > shares:
        raise ValueError("Pool secret would be irrecoverable.")
    poly = [secret] + [_RINT(prime - 1) for i in range(minimum - 1)]
    points = [(i, _eval_at(poly, i, prime))
              for i in range(1, shares + 1)]
    return points

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1). This can
    be computed via the extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
    # Returns (g, x, y) such that a*x + b*y == g == gcd(a, b)
    last_x, x = 1, 0
    last_y, y = 0, 1
    while b != 0:
        quot = a // b
        a, b = b, a % b
        last_x, x = x, last_x - quot * x
        last_y, y = y, last_y - quot * y
    return a, last_x, last_y

def _divmod(num, den, p):
    """Compute num / den modulo prime p

    To explain this, the result will be such that:
    den * _divmod(num, den, p) % p == num
    """
    g, inv, _ = _extended_gcd(den, p)
    if g != 1:
        raise ValueError("Denominator %s has no inverse modulo %s" % (den, p))
    return (num * inv) % p

def _lagrange_interpolate(x, x_s, y_s, p):
    """
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order.
    """
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum = (accum * (v % p)) % p
        return accum
    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_divmod((nums[i] * den * (y_s[i] % p)) % p, dens[i], p)
               for i in range(k)])
    return (_divmod(num, den, p) + p) % p

def recover_secret(shares, prime=_PRIME):
    """
    Recover the secret from share points
    (points (x,y) on the polynomial).
    """
    if len(shares) < 1:
        raise ValueError("need at least one share")
    x_s, y_s = zip(*shares)
    return _lagrange_interpolate(0, x_s, y_s, prime)


def _serialize_shares_json(shares: List[tuple], meta: Dict[str, Any]) -> str:
    data = {
        'meta': meta,
        'shares': [{'x': int(x), 'y': int(y)} for x, y in shares]
    }
    return json.dumps(data, indent=2)


def _serialize_single_share_json(share: tuple, share_index: int, meta: Dict[str, Any]) -> str:
    """Serialize a single share with metadata for individual file output."""
    x, y = share
    data = {
        'meta': dict(meta, share_index=share_index),
        'share': {'x': int(x), 'y': int(y)}
    }
    return json.dumps(data, indent=2)


def _deserialize_shares_json(s: str):
    obj = json.loads(s)
    meta = obj.get('meta', {})
    
    # Check if it's a single share format
    if 'share' in obj:
        share = obj['share']
        if 'x' not in share or 'y' not in share:
            raise ValueError('invalid share entry, expected {"x":...,"y":...}')
        shares = [(int(share['x']), int(share['y']))]
        return shares, meta
    
    # Legacy format with multiple shares
    raw = obj.get('shares')
    if raw is None:
        raise ValueError('invalid shares JSON: missing "shares" or "share" key')
    shares = []
    for item in raw:
        if 'x' not in item or 'y' not in item:
            raise ValueError('invalid share entry, expected {"x":..,"y":..}')
        shares.append((int(item['x']), int(item['y'])))
    return shares, meta


def _write_output(path: Optional[str], data: str) -> None:
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
    else:
        print(data)


def _read_file_bytes(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()


def _kdf_apply(kdf_spec: Optional[str], secret_input: bytes):
    """Apply KDF if requested. Returns integer secret and metadata dict (or None).
    kdf_spec examples: None, 'sha256', 'pbkdf2:100000'
    """
    if not kdf_spec:
        return int.from_bytes(secret_input, 'big'), None

    if kdf_spec.lower() == 'sha256':
        digest = hashlib.sha256(secret_input).digest()
        return int.from_bytes(digest, 'big'), {'kdf': 'sha256'}

    if kdf_spec.lower().startswith('pbkdf2'):
        parts = kdf_spec.split(':', 1)
        iterations = 100000
        if len(parts) == 2 and parts[1].isdigit():
            iterations = int(parts[1])
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', secret_input, salt, iterations, dklen=32)
        meta = {'kdf': 'pbkdf2', 'iterations': iterations, 'salt': base64.b64encode(salt).decode('ascii')}
        return int.from_bytes(dk, 'big'), meta

    raise ValueError('unsupported kdf spec: %s' % kdf_spec)

def main():
    parser = argparse.ArgumentParser(prog='sss', description='Shamir secret sharing tool')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('generate', help='Generate shares from a secret')
    sub.add_parser('recover', help='Recover secret from shares')
    args, rest = parser.parse_known_args()
    if args.cmd == 'generate':
        return cmd_generate(rest)
    if args.cmd == 'recover':
        return cmd_recover(rest)
    parser.print_help()
    return 2

def cmd_generate(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog='generate', description='Generate Shamir shares from a secret')
    parser.add_argument('--secret', '-s', help='secret string or integer', default=None)
    parser.add_argument('--secret-file', '-f', help='path to file containing secret', default=None)
    parser.add_argument('--minimum', '-m', type=int, help='threshold (minimum shares)', default=None)
    parser.add_argument('--shares', '-n', type=int, help='number of shares to create', default=None)
    parser.add_argument('--prime', help='prime modulus to use', default=None)
    parser.add_argument('--out', '-o', help='output file (JSON) or directory for split shares', default=None)
    parser.add_argument('--format', choices=['json', 'lines'], default='json')
    parser.add_argument('--kdf', help='KDF to apply for passphrases (sha256 or pbkdf2:ITER)', default=None)
    parser.add_argument('--split-shares', action='store_true', help='output each share to a separate file')
    args = parser.parse_args(argv)

    # require secret CLI input
    if args.secret and args.secret_file:
        print('Cannot specify both --secret and --secret-file', file=sys.stderr)
        return 2
    if not args.secret and not args.secret_file:
        print('Missing required secret: provide --secret or --secret-file', file=sys.stderr)
        return 2

    if args.secret is not None:
        secret_bytes = str(args.secret).encode('utf-8')
    else:
        if not os.path.exists(args.secret_file):
            print(f"Secret file not found: {args.secret_file}", file=sys.stderr)
            return 2
        secret_bytes = _read_file_bytes(args.secret_file)

    cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'default.json')
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

    minimum = args.minimum if args.minimum is not None else cfg.get('minimum', 3)
    shares_count = args.shares if args.shares is not None else cfg.get('shares', 6)
    prime_val = args.prime if args.prime is not None else cfg.get('prime', None)
    prime = int(prime_val) if prime_val is not None else _PRIME

    try:
        minimum = int(minimum)
        shares_count = int(shares_count)
    except Exception:
        print('minimum and shares must be integers', file=sys.stderr)
        return 2
    if not (1 <= minimum <= shares_count):
        print('Invalid share parameters: require 1 <= minimum <= shares_count', file=sys.stderr)
        return 2

    secret_int, kdf_meta = _kdf_apply(args.kdf, secret_bytes)
    
    # Check if secret exceeds prime (would cause data loss)
    if secret_int >= prime:
        print(f'Warning: secret ({secret_int.bit_length()} bits) exceeds prime ({prime.bit_length()} bits).', file=sys.stderr)
        print(f'Data will be lost due to modulo reduction. Use a larger --prime or shorter secret.', file=sys.stderr)
        return 2
    
    secret_int = secret_int % prime

    shares = make_random_shares(secret_int, minimum=minimum, shares=shares_count, prime=prime)

    meta = {'minimum': minimum, 'shares': shares_count, 'prime': prime, 'secret_byte_length': len(secret_bytes)}
    if kdf_meta:
        meta['kdf'] = kdf_meta

    if args.format == 'json':
        if args.split_shares:
            # Write each share to a separate file
            if args.out:
                # Ensure output directory exists
                out_dir = os.path.dirname(args.out) if os.path.dirname(args.out) else '.'
                base_name = os.path.basename(args.out)
                if base_name.endswith('.json'):
                    base_name = base_name[:-5]
                os.makedirs(out_dir, exist_ok=True)
            else:
                out_dir = '.'
                base_name = 'share'
            
            for idx, share in enumerate(shares, 1):
                share_json = _serialize_single_share_json(share, idx, meta)
                share_path = os.path.join(out_dir, f"{base_name}-{idx}.json")
                with open(share_path, 'w', encoding='utf-8') as f:
                    f.write(share_json)
            
            if args.out:
                full_prefix = os.path.join(out_dir, base_name)
                print(f"Generated {len(shares)} share files: {full_prefix}-1.json to {full_prefix}-{len(shares)}.json", file=sys.stderr)
            else:
                print(f"Generated {len(shares)} share files in current directory: {base_name}-1.json to {base_name}-{len(shares)}.json", file=sys.stderr)
        else:
            # Original behavior: single file with all shares
            text = _serialize_shares_json(shares, meta)
            _write_output(args.out, text)
    else:
        # lines: each line "x y"
        lines = '\n'.join(f"{x} {y}" for x, y in shares)
        _write_output(args.out, lines)

    return 0

def cmd_recover(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(prog='recover', description='Recover secret from shares')
    parser.add_argument('--shares-file', '-i', help='path to shares JSON file(s), can specify multiple', nargs='+', default=None)
    parser.add_argument('--shares-dir', '-d', help='directory containing share files', default=None)
    parser.add_argument('--format', choices=['json', 'lines'], default='json')
    parser.add_argument('--as-str', action='store_true', help='Attempt to decode the recovered secret as UTF-8')
    parser.add_argument('--out', '-o', help='output file (default stdout)', default=None)
    parser.add_argument('--prime', help='prime modulus to use', default=None)
    args = parser.parse_args(argv)

    shares = []
    meta = {}
    
    # Collect files to read
    files_to_read = []
    
    if args.shares_dir:
        # Read all JSON files from directory
        if not os.path.isdir(args.shares_dir):
            print(f"Shares directory not found: {args.shares_dir}", file=sys.stderr)
            return 2
        for filename in sorted(os.listdir(args.shares_dir)):
            if filename.endswith('.json'):
                files_to_read.append(os.path.join(args.shares_dir, filename))
    elif args.shares_file:
        # Multiple files specified
        files_to_read = args.shares_file
    
    if files_to_read:
        # Read from file(s)
        all_shares = []
        merged_meta = None
        
        for filepath in files_to_read:
            if not os.path.exists(filepath):
                print(f"Shares file not found: {filepath}", file=sys.stderr)
                return 2
            
            with open(filepath, 'r', encoding='utf-8') as f:
                raw = f.read()
            
            if args.format == 'json':
                file_shares, file_meta = _deserialize_shares_json(raw)
                all_shares.extend(file_shares)
                
                # Merge metadata (validate consistency)
                if merged_meta is None:
                    merged_meta = file_meta
                else:
                    # Validate critical metadata matches
                    for key in ['minimum', 'shares', 'prime', 'secret_byte_length']:
                        if key in merged_meta and key in file_meta:
                            if merged_meta[key] != file_meta[key]:
                                print(f"Warning: Inconsistent metadata '{key}' across share files", file=sys.stderr)
                    # Preserve KDF info from first file
                    if 'kdf' in file_meta and 'kdf' not in merged_meta:
                        merged_meta['kdf'] = file_meta['kdf']
            else:
                for line in raw.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) != 2:
                        print('invalid line in shares input: %r' % line, file=sys.stderr)
                        return 2
                    all_shares.append((int(parts[0]), int(parts[1])))
        
        shares = all_shares
        meta = merged_meta if merged_meta else {}
    else:
        # Read from stdin (original behavior)
        raw = sys.stdin.read()
        
        if args.format == 'json':
            shares, meta = _deserialize_shares_json(raw)
        else:
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    print('invalid line in shares input: %r' % line, file=sys.stderr)
                    return 2
                shares.append((int(parts[0]), int(parts[1])))

    if len(shares) < 1:
        print('no shares provided', file=sys.stderr)
        return 2

    cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'default.json')
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, 'r') as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}

    prime_val = args.prime if args.prime is not None else meta.get('prime', cfg.get('prime', None))
    prime = int(prime_val) if prime_val is not None else _PRIME

    # Validate distinct x-values
    xs = [x for x, _ in shares]
    if len(set(xs)) != len(xs):
        print('duplicate x-values in shares', file=sys.stderr)
        return 2

    # If meta provides minimum, check it
    minimum = meta.get('minimum', cfg.get('minimum', None))
    if minimum is not None and len(shares) < int(minimum):
        print('insufficient shares for threshold: need %s' % minimum, file=sys.stderr)
        return 2

    secret_int = recover_secret(shares, prime=prime)

    if args.as_str:
        # attempt to decode as big-endian bytes to UTF-8
        try:
            # Use stored byte length if available, otherwise compute minimal
            blen = meta.get('secret_byte_length')
            if blen is None:
                blen = (secret_int.bit_length() + 7) // 8
            b = secret_int.to_bytes(blen, 'big')
            out = b.decode('utf-8')
        except Exception:
            print('failed to decode recovered secret as UTF-8', file=sys.stderr)
            return 2
    else:
        out = str(secret_int)

    _write_output(args.out, out)
    return 0

if __name__ == '__main__':
    main()