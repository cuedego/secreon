"""
SLIP-39 Share data structure

Defines the Share class and related structures for encoding/decoding
SLIP-39 mnemonic shares.
"""

from dataclasses import dataclass
from typing import Iterable, List, NamedTuple

from . import rs1024, wordlist

# Note: We don't import int_to_indices from wordlist because we need
# a version with radix_bits parameter for flexibility

# Constants
RADIX_BITS = 10
"""The length of the radix in bits."""

RADIX = 2 ** RADIX_BITS
"""The number of words in the wordlist (1024)."""

ID_LENGTH_BITS = 15
"""The length of the random identifier in bits."""

EXTENDABLE_FLAG_LENGTH_BITS = 1
"""The length of the extendable backup flag in bits."""

ITERATION_EXP_LENGTH_BITS = 4
"""The length of the iteration exponent in bits."""

ID_EXP_LENGTH_WORDS = 2
"""The length of the identifier + extendable flag + iteration exponent in words (20 bits / 10 = 2)."""

CHECKSUM_LENGTH_WORDS = 3
"""The length of the RS1024 checksum in words."""

METADATA_LENGTH_WORDS = ID_EXP_LENGTH_WORDS + 2 + CHECKSUM_LENGTH_WORDS
"""The length of the mnemonic in words without the share value (2 + 2 + 3 = 7)."""

MIN_STRENGTH_BITS = 128
"""The minimum allowed entropy of the master secret."""

MIN_MNEMONIC_LENGTH_WORDS = METADATA_LENGTH_WORDS + ((MIN_STRENGTH_BITS + RADIX_BITS - 1) // RADIX_BITS)
"""The minimum allowed length of the mnemonic in words."""

CUSTOMIZATION_STRING_ORIG = b"shamir"
"""The customization string for non-extendable backups."""

CUSTOMIZATION_STRING_EXTENDABLE = b"shamir_extendable"
"""The customization string for extendable backups."""

WordIndex = int


class MnemonicError(Exception):
    """Exception raised for errors in mnemonic processing."""
    pass


def _round_bits(n: int, radix_bits: int) -> int:
    """Get the number of radix_bits-sized digits required to store a n-bit value."""
    return (n + radix_bits - 1) // radix_bits


def bits_to_bytes(n: int) -> int:
    """Round up bit count to whole bytes."""
    return _round_bits(n, 8)


def bits_to_words(n: int) -> int:
    """Round up bit count to a multiple of word size."""
    return _round_bits(n, RADIX_BITS)


def int_to_indices(value: int, length: int, radix_bits: int) -> List[int]:
    """
    Convert an integer value to indices in big endian order.
    
    Args:
        value: The integer value to convert
        length: The number of indices to generate
        radix_bits: The number of bits per index
        
    Returns:
        List of indices in big endian order
    """
    mask = (1 << radix_bits) - 1
    return [(value >> (i * radix_bits)) & mask for i in reversed(range(length))]


def _int_to_word_indices(value: int, length: int) -> List[WordIndex]:
    """Converts an integer value to a list of base 1024 indices in big endian order."""
    return list(int_to_indices(value, length, radix_bits=RADIX_BITS))


def _int_from_word_indices(indices: Iterable[WordIndex]) -> int:
    """Converts a list of base 1024 indices in big endian order to an integer value."""
    value = 0
    for index in indices:
        value = value * RADIX + index
    return value


def _customization_string(extendable: bool) -> bytes:
    """Get the customization string for RS1024 checksum."""
    if extendable:
        return CUSTOMIZATION_STRING_EXTENDABLE
    else:
        return CUSTOMIZATION_STRING_ORIG


class ShareCommonParameters(NamedTuple):
    """Parameters that are common to all shares of a master secret."""
    
    identifier: int
    extendable: bool
    iteration_exponent: int
    group_threshold: int
    group_count: int


class ShareGroupParameters(NamedTuple):
    """Parameters that are common to all shares in the same group."""
    
    identifier: int
    extendable: bool
    iteration_exponent: int
    group_index: int
    group_threshold: int
    group_count: int
    member_threshold: int


@dataclass(frozen=True)
class Share:
    """Represents a single mnemonic share and its metadata."""
    
    identifier: int
    extendable: bool
    iteration_exponent: int
    group_index: int
    group_threshold: int
    group_count: int
    index: int
    member_threshold: int
    value: bytes
    
    def common_parameters(self) -> ShareCommonParameters:
        """Return values that uniquely identify a matching set of shares."""
        return ShareCommonParameters(
            self.identifier,
            self.extendable,
            self.iteration_exponent,
            self.group_threshold,
            self.group_count,
        )
    
    def group_parameters(self) -> ShareGroupParameters:
        """Return values that uniquely identify shares belonging to the same group."""
        return ShareGroupParameters(
            self.identifier,
            self.extendable,
            self.iteration_exponent,
            self.group_index,
            self.group_threshold,
            self.group_count,
            self.member_threshold,
        )
    
    def _encode_id_exp(self) -> List[WordIndex]:
        """Encode identifier, extendable flag, and iteration exponent to word indices."""
        id_exp_int = self.identifier << (
            ITERATION_EXP_LENGTH_BITS + EXTENDABLE_FLAG_LENGTH_BITS
        )
        id_exp_int += self.extendable << ITERATION_EXP_LENGTH_BITS
        id_exp_int += self.iteration_exponent
        return _int_to_word_indices(id_exp_int, ID_EXP_LENGTH_WORDS)
    
    def _encode_share_params(self) -> List[WordIndex]:
        """Encode share parameters to word indices."""
        # Each value is 4 bits, for 20 bits total
        val = self.group_index
        val <<= 4
        val += self.group_threshold - 1
        val <<= 4
        val += self.group_count - 1
        val <<= 4
        val += self.index
        val <<= 4
        val += self.member_threshold - 1
        # Group parameters are 2 words (20 bits / 10 = 2)
        return _int_to_word_indices(val, 2)
    
    def words(self) -> List[str]:
        """Convert share data to a list of words."""
        value_word_count = bits_to_words(len(self.value) * 8)
        value_int = int.from_bytes(self.value, 'big')
        value_data = _int_to_word_indices(value_int, value_word_count)
        
        share_data = self._encode_id_exp() + self._encode_share_params() + value_data
        checksum = rs1024.create_checksum(
            share_data, _customization_string(self.extendable)
        )
        
        return wordlist.indices_to_words(share_data + checksum)
    
    def mnemonic(self) -> str:
        """Convert share data to a space-separated mnemonic string."""
        return ' '.join(self.words())
    
    @classmethod
    def from_mnemonic(cls, mnemonic: str) -> 'Share':
        """Convert a share mnemonic to Share data."""
        mnemonic_data = wordlist.mnemonic_to_indices(mnemonic)
        
        if len(mnemonic_data) < MIN_MNEMONIC_LENGTH_WORDS:
            raise MnemonicError(
                f"Invalid mnemonic length. The length of each mnemonic "
                f"must be at least {MIN_MNEMONIC_LENGTH_WORDS} words."
            )
        
        padding_len = (RADIX_BITS * (len(mnemonic_data) - METADATA_LENGTH_WORDS)) % 16
        if padding_len > 8:
            raise MnemonicError("Invalid mnemonic length.")
        
        # Extract identifier, extendable flag, and iteration exponent
        id_exp_data = mnemonic_data[:ID_EXP_LENGTH_WORDS]
        id_exp_int = _int_from_word_indices(id_exp_data)
        
        identifier = id_exp_int >> (
            EXTENDABLE_FLAG_LENGTH_BITS + ITERATION_EXP_LENGTH_BITS
        )
        extendable = bool((id_exp_int >> ITERATION_EXP_LENGTH_BITS) & 1)
        iteration_exponent = id_exp_int & ((1 << ITERATION_EXP_LENGTH_BITS) - 1)
        
        # Verify checksum
        if not rs1024.verify_checksum(mnemonic_data, _customization_string(extendable)):
            raise MnemonicError(
                f'Invalid mnemonic checksum for "{" ".join(mnemonic.split()[:ID_EXP_LENGTH_WORDS + 2])} ...".'
            )
        
        # Extract share parameters
        share_params_data = mnemonic_data[ID_EXP_LENGTH_WORDS:ID_EXP_LENGTH_WORDS + 2]
        share_params_int = _int_from_word_indices(share_params_data)
        share_params = list(int_to_indices(share_params_int, 5, 4))
        
        (
            group_index,
            group_threshold,
            group_count,
            index,
            member_threshold,
        ) = share_params
        
        if group_count < group_threshold:
            raise MnemonicError(
                f'Invalid mnemonic "{" ".join(mnemonic.split()[:ID_EXP_LENGTH_WORDS + 2])} ...". '
                'Group threshold cannot be greater than group count.'
            )
        
        # Extract share value
        value_data = mnemonic_data[
            ID_EXP_LENGTH_WORDS + 2:-CHECKSUM_LENGTH_WORDS
        ]
        value_byte_count = bits_to_bytes(RADIX_BITS * len(value_data) - padding_len)
        value_int = _int_from_word_indices(value_data)
        try:
            value = value_int.to_bytes(value_byte_count, 'big')
        except OverflowError:
            raise MnemonicError(
                f'Invalid mnemonic padding for "{" ".join(mnemonic.split()[:ID_EXP_LENGTH_WORDS + 2])} ...".'
            ) from None
        
        return cls(
            identifier,
            extendable,
            iteration_exponent,
            group_index,
            group_threshold + 1,
            group_count + 1,
            index,
            member_threshold + 1,
            value,
        )
