"""
SLIP-39 Shamir's Secret Sharing Implementation

Core SSS functions for splitting and recovering secrets over GF(256).
"""

import hmac
import secrets
from dataclasses import dataclass
from typing import Dict, Iterable, List, NamedTuple, Sequence, Set, Tuple

from . import cipher, gf256
from .share import (
    Share,
    ShareCommonParameters,
    ShareGroupParameters,
    MnemonicError,
    bits_to_bytes,
)

# Constants
DIGEST_LENGTH_BYTES = 4
"""The length of the digest of the shared secret in bytes."""

SECRET_INDEX = 255
"""The index of the share containing the shared secret."""

DIGEST_INDEX = 254
"""The index of the share containing the digest of the shared secret."""

MAX_SHARE_COUNT = 16
"""The maximum number of shares that can be created."""

MIN_STRENGTH_BITS = 128
"""The minimum allowed entropy of the master secret."""

ID_LENGTH_BITS = 15
"""The length of the random identifier in bits."""

GROUP_PREFIX_LENGTH_WORDS = 3
"""The length of the prefix of the mnemonic that is common to a share group."""

RANDOM_BYTES = secrets.token_bytes
"""Source of random bytes. Can be overridden for deterministic testing."""


class RawShare(NamedTuple):
    """A raw share consisting of an x-coordinate and data bytes."""
    x: int
    data: bytes


class ShareGroup:
    """A collection of shares belonging to the same group."""
    
    def __init__(self) -> None:
        self.shares: Set[Share] = set()
    
    def __iter__(self):
        return iter(self.shares)
    
    def __len__(self) -> int:
        return len(self.shares)
    
    def __bool__(self) -> bool:
        return bool(self.shares)
    
    def __contains__(self, obj) -> bool:
        return obj in self.shares
    
    def add(self, share: Share) -> None:
        """Add a share to the group, validating compatibility."""
        if self.shares and self.group_parameters() != share.group_parameters():
            fields = zip(
                ShareGroupParameters._fields,
                self.group_parameters(),
                share.group_parameters(),
            )
            mismatch = next(name for name, x, y in fields if x != y)
            raise MnemonicError(
                f"Invalid set of mnemonics. The {mismatch} parameters don't match."
            )
        
        self.shares.add(share)
    
    def to_raw_shares(self) -> List[RawShare]:
        """Convert to list of RawShare for interpolation."""
        return [RawShare(s.index, s.value) for s in self.shares]
    
    def get_minimal_group(self) -> 'ShareGroup':
        """Return a minimal group containing exactly threshold shares."""
        group = ShareGroup()
        group.shares = set(
            share for _, share in zip(range(self.member_threshold()), self.shares)
        )
        return group
    
    def common_parameters(self) -> ShareCommonParameters:
        """Return parameters common to all shares."""
        return next(iter(self.shares)).common_parameters()
    
    def group_parameters(self) -> ShareGroupParameters:
        """Return parameters common to shares in this group."""
        return next(iter(self.shares)).group_parameters()
    
    def member_threshold(self) -> int:
        """Return the member threshold for this group."""
        return next(iter(self.shares)).member_threshold
    
    def is_complete(self) -> bool:
        """Check if the group has enough shares to recover."""
        if self.shares:
            return len(self.shares) >= self.member_threshold()
        else:
            return False


@dataclass(frozen=True)
class EncryptedMasterSecret:
    """Represents an encrypted master secret with its metadata."""
    
    identifier: int
    extendable: bool
    iteration_exponent: int
    ciphertext: bytes
    
    @classmethod
    def from_master_secret(
        cls,
        master_secret: bytes,
        passphrase: bytes,
        identifier: int,
        extendable: bool,
        iteration_exponent: int,
    ) -> 'EncryptedMasterSecret':
        """Encrypt a master secret with the given parameters."""
        ciphertext = cipher.encrypt(
            master_secret, passphrase, iteration_exponent, identifier, extendable
        )
        return EncryptedMasterSecret(
            identifier, extendable, iteration_exponent, ciphertext
        )
    
    def decrypt(self, passphrase: bytes) -> bytes:
        """Decrypt the encrypted master secret."""
        return cipher.decrypt(
            self.ciphertext,
            passphrase,
            self.iteration_exponent,
            self.identifier,
            self.extendable,
        )


def _interpolate(shares: Sequence[RawShare], x: int) -> bytes:
    """
    Perform Lagrange interpolation over GF(256) to find f(x).
    
    Given shares (x_i, f(x_i)), compute f(x) using Lagrange interpolation.
    
    Args:
        shares: List of (x, y) pairs where y is bytes
        x: The x-coordinate to evaluate at
        
    Returns:
        The interpolated value f(x) as bytes
    """
    x_coordinates = set(share.x for share in shares)
    
    if len(x_coordinates) != len(shares):
        raise MnemonicError("Invalid set of shares. Share indices must be unique.")
    
    share_value_lengths = set(len(share.data) for share in shares)
    if len(share_value_lengths) != 1:
        raise MnemonicError(
            "Invalid set of shares. All share values must have the same length."
        )
    
    # If x is one of the x-coordinates, just return that share's data
    if x in x_coordinates:
        for share in shares:
            if share.x == x:
                return share.data
    
    # Perform Lagrange interpolation byte-by-byte
    share_length = share_value_lengths.pop()
    result = bytes(share_length)
    
    for share in shares:
        # Compute the Lagrange basis polynomial L_i(x)
        # L_i(x) = product of (x - x_j) / (x_i - x_j) for j != i
        basis = 1
        for other in shares:
            if other.x != share.x:
                numerator = x ^ other.x  # x - x_j in GF(256)
                denominator = share.x ^ other.x  # x_i - x_j in GF(256)
                basis = gf256.multiply(basis, gf256.divide(numerator, denominator))
        
        # Add share.data * basis to result
        result = bytes(
            r ^ gf256.multiply(s, basis)
            for r, s in zip(result, share.data)
        )
    
    return result


def _create_digest(random_data: bytes, shared_secret: bytes) -> bytes:
    """Create HMAC digest of the shared secret."""
    return hmac.new(random_data, shared_secret, 'sha256').digest()[:DIGEST_LENGTH_BYTES]


def _split_secret(
    threshold: int, share_count: int, shared_secret: bytes
) -> List[RawShare]:
    """
    Split a secret into shares using Shamir's Secret Sharing over GF(256).
    
    Args:
        threshold: Number of shares needed to recover the secret
        share_count: Total number of shares to generate
        shared_secret: The secret to split
        
    Returns:
        List of RawShare objects
    """
    if threshold < 1:
        raise ValueError("The requested threshold must be a positive integer.")
    
    if threshold > share_count:
        raise ValueError(
            "The requested threshold must not exceed the number of shares."
        )
    
    if share_count > MAX_SHARE_COUNT:
        raise ValueError(
            f"The requested number of shares must not exceed {MAX_SHARE_COUNT}."
        )
    
    # If threshold is 1, just replicate the secret (no SSS needed)
    if threshold == 1:
        return [RawShare(i, shared_secret) for i in range(share_count)]
    
    # For threshold >= 2, we use the digest scheme
    # Generate random shares (threshold - 2 random points)
    random_share_count = threshold - 2
    
    shares = [
        RawShare(i, RANDOM_BYTES(len(shared_secret)))
        for i in range(random_share_count)
    ]
    
    # Create digest
    random_part = RANDOM_BYTES(len(shared_secret) - DIGEST_LENGTH_BYTES)
    digest = _create_digest(random_part, shared_secret)
    
    # Base shares: random shares + digest share + secret share
    base_shares = shares + [
        RawShare(DIGEST_INDEX, digest + random_part),
        RawShare(SECRET_INDEX, shared_secret),
    ]
    
    # Interpolate to generate remaining shares
    for i in range(random_share_count, share_count):
        shares.append(RawShare(i, _interpolate(base_shares, i)))
    
    return shares


def _recover_secret(threshold: int, shares: Sequence[RawShare]) -> bytes:
    """
    Recover a secret from shares using Lagrange interpolation.
    
    Args:
        threshold: The threshold used when splitting
        shares: List of RawShare objects
        
    Returns:
        The recovered secret
    """
    # If threshold is 1, the digest is not used
    if threshold == 1:
        return next(iter(shares)).data
    
    # Interpolate to find the secret and digest
    shared_secret = _interpolate(shares, SECRET_INDEX)
    digest_share = _interpolate(shares, DIGEST_INDEX)
    digest = digest_share[:DIGEST_LENGTH_BYTES]
    random_part = digest_share[DIGEST_LENGTH_BYTES:]
    
    # Verify the digest
    if digest != _create_digest(random_part, shared_secret):
        raise MnemonicError("Invalid digest of the shared secret.")
    
    return shared_secret


def decode_mnemonics(mnemonics: Iterable[str]) -> Dict[int, ShareGroup]:
    """
    Decode a list of mnemonics into groups.
    
    Args:
        mnemonics: Iterable of mnemonic strings
        
    Returns:
        Dictionary mapping group_index to ShareGroup
    """
    common_params: Set[ShareCommonParameters] = set()
    groups: Dict[int, ShareGroup] = {}
    
    for mnemonic in mnemonics:
        share = Share.from_mnemonic(mnemonic)
        common_params.add(share.common_parameters())
        group = groups.setdefault(share.group_index, ShareGroup())
        group.add(share)
    
    if len(common_params) != 1:
        raise MnemonicError(
            "Invalid set of mnemonics. "
            "All mnemonics must begin with the same 3 words, "
            "must have the same group threshold and the same group count."
        )
    
    return groups


def split_ems(
    group_threshold: int,
    groups: Sequence[Tuple[int, int]],
    encrypted_master_secret: EncryptedMasterSecret,
) -> List[List[Share]]:
    """
    Split an Encrypted Master Secret into share groups.
    
    Args:
        group_threshold: Number of groups needed to recover
        groups: List of (member_threshold, member_count) tuples
        encrypted_master_secret: The EMS to split
        
    Returns:
        List of lists of Share objects (one list per group)
    """
    if len(encrypted_master_secret.ciphertext) * 8 < MIN_STRENGTH_BITS:
        raise ValueError(
            f"The length of the master secret must be "
            f"at least {bits_to_bytes(MIN_STRENGTH_BITS)} bytes."
        )
    
    if group_threshold > len(groups):
        raise ValueError(
            "The requested group threshold must not exceed the number of groups."
        )
    
    if any(
        member_threshold == 1 and member_count > 1
        for member_threshold, member_count in groups
    ):
        raise ValueError(
            "Creating multiple member shares with member threshold 1 is not allowed. "
            "Use 1-of-1 member sharing instead."
        )
    
    # Split EMS into group shares
    group_shares = _split_secret(
        group_threshold, len(groups), encrypted_master_secret.ciphertext
    )
    
    # Split each group share into member shares
    return [
        [
            Share(
                encrypted_master_secret.identifier,
                encrypted_master_secret.extendable,
                encrypted_master_secret.iteration_exponent,
                group_index,
                group_threshold,
                len(groups),
                member_index,
                member_threshold,
                value,
            )
            for member_index, value in _split_secret(
                member_threshold, member_count, group_secret
            )
        ]
        for (member_threshold, member_count), (group_index, group_secret) in zip(
            groups, group_shares
        )
    ]


def _random_identifier() -> int:
    """Generate a random identifier."""
    identifier = int.from_bytes(RANDOM_BYTES(bits_to_bytes(ID_LENGTH_BITS)), 'big')
    return identifier & ((1 << ID_LENGTH_BITS) - 1)


def generate_mnemonics(
    group_threshold: int,
    groups: Sequence[Tuple[int, int]],
    master_secret: bytes,
    passphrase: bytes = b"",
    extendable: bool = True,
    iteration_exponent: int = 1,
) -> List[List[str]]:
    """
    Split a master secret into SLIP-39 mnemonic shares.
    
    Args:
        group_threshold: Number of groups required to reconstruct
        groups: List of (member_threshold, member_count) per group
        master_secret: The secret to split
        passphrase: Optional passphrase for encryption
        extendable: Whether this is an extendable backup
        iteration_exponent: PBKDF2 iteration exponent
        
    Returns:
        List of lists of mnemonic strings (one list per group)
    """
    if not all(32 <= c <= 126 for c in passphrase):
        raise ValueError(
            "The passphrase must contain only printable ASCII characters (code points 32-126)."
        )
    
    identifier = _random_identifier()
    encrypted_master_secret = EncryptedMasterSecret.from_master_secret(
        master_secret, passphrase, identifier, extendable, iteration_exponent
    )
    grouped_shares = split_ems(group_threshold, groups, encrypted_master_secret)
    return [[share.mnemonic() for share in group] for group in grouped_shares]


def recover_ems(groups: Dict[int, ShareGroup]) -> EncryptedMasterSecret:
    """
    Recover an Encrypted Master Secret from share groups.
    
    Args:
        groups: Dictionary mapping group_index to ShareGroup
        
    Returns:
        The recovered EncryptedMasterSecret
    """
    if not groups:
        raise MnemonicError("The set of shares is empty.")
    
    params = next(iter(groups.values())).common_parameters()
    
    if len(groups) < params.group_threshold:
        raise MnemonicError(
            f"Insufficient number of mnemonic groups. "
            f"The required number of groups is {params.group_threshold}."
        )
    
    if len(groups) != params.group_threshold:
        raise MnemonicError(
            f"Wrong number of mnemonic groups. "
            f"Expected {params.group_threshold} groups, "
            f"but {len(groups)} were provided."
        )
    
    for group in groups.values():
        if len(group) != group.member_threshold():
            share_words = next(iter(group)).words()
            prefix = " ".join(share_words[:GROUP_PREFIX_LENGTH_WORDS])
            raise MnemonicError(
                f"Wrong number of mnemonics. "
                f'Expected {group.member_threshold()} mnemonics starting with "{prefix} ...", '
                f"but {len(group)} were provided."
            )
    
    # Recover each group's secret
    group_shares = [
        RawShare(
            group_index,
            _recover_secret(group.member_threshold(), group.to_raw_shares()),
        )
        for group_index, group in groups.items()
    ]
    
    # Recover the encrypted master secret
    ciphertext = _recover_secret(params.group_threshold, group_shares)
    return EncryptedMasterSecret(
        params.identifier, params.extendable, params.iteration_exponent, ciphertext
    )


def combine_mnemonics(mnemonics: Iterable[str], passphrase: bytes = b"") -> bytes:
    """
    Combine mnemonic shares to recover the master secret.
    
    Args:
        mnemonics: List of mnemonic strings
        passphrase: The passphrase used to encrypt the master secret
        
    Returns:
        The recovered master secret
    """
    if not mnemonics:
        raise MnemonicError("The list of mnemonics is empty.")
    
    groups = decode_mnemonics(mnemonics)
    encrypted_master_secret = recover_ems(groups)
    return encrypted_master_secret.decrypt(passphrase)
