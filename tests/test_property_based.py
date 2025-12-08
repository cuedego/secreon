#!/usr/bin/env python3
"""
Property-based tests for SLIP-39 using hypothesis.
"""
import sys
sys.path.insert(0, 'src')

from hypothesis import given, strategies as st
from hypothesis import settings, HealthCheck

from slip39 import generate_mnemonics, combine_mnemonics, MnemonicError

# Reduce health check noise for long-running PBKDF2
settings.register_profile("ci", suppress_health_check=(HealthCheck.too_slow,))
settings.load_profile("ci")

# Helper: generate simple group specs as list of (threshold,count)
@st.composite
def group_specs(draw):
    # choose number of groups 1..3
    g = draw(st.integers(min_value=1, max_value=3))
    specs = []
    for _ in range(g):
        count = draw(st.integers(min_value=1, max_value=4))
        # avoid member_threshold == 1 with count > 1 (not allowed by split_ems)
        if count == 1:
            threshold = 1
        else:
            threshold = draw(st.integers(min_value=2, max_value=count))
        specs.append((threshold, count))
    return specs

@st.composite
def secrets_and_groups(draw):
    # choose secret length 16 or 32 bytes
    secret_len = draw(st.sampled_from([16, 32]))
    secret = draw(st.binary(min_size=secret_len, max_size=secret_len))
    groups = draw(group_specs())
    # For simplicity require all groups be needed (group_threshold == len(groups))
    group_threshold = len(groups)
    # passphrase must be printable ASCII characters (32-126)
    passphrase_text = draw(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=0, max_size=10))
    passphrase = passphrase_text.encode('ascii')
    extendable = draw(st.booleans())
    iteration_exponent = draw(st.integers(min_value=0, max_value=2))
    return secret, groups, group_threshold, passphrase, extendable, iteration_exponent


@given(secrets_and_groups())
@settings(max_examples=200)
def test_generate_and_combine_roundtrip(data):
    secret, groups, group_threshold, passphrase, extendable, iteration_exponent = data

    # generate mnemonics
    mnemonics = generate_mnemonics(
        group_threshold=group_threshold,
        groups=groups,
        master_secret=secret,
        passphrase=passphrase,
        iteration_exponent=iteration_exponent,
        extendable=extendable,
    )

    # For combine, pick exactly the minimal required shares:
    # select `group_threshold` groups and from each take `member_threshold` shares
    flat = []
    for gidx, (threshold, count) in enumerate(groups):
        take = threshold
        # take the first `take` shares from this group
        flat.extend(mnemonics[gidx][:take])

    # combine should recover original secret
    recovered = combine_mnemonics(flat, passphrase)
    assert recovered == secret


@given(secrets_and_groups())
@settings(max_examples=100)
def test_threshold_property(data):
    secret, groups, group_threshold, passphrase, extendable, iteration_exponent = data

    mnemonics = generate_mnemonics(
        group_threshold=group_threshold,
        groups=groups,
        master_secret=secret,
        passphrase=passphrase,
        iteration_exponent=iteration_exponent,
        extendable=extendable,
    )

    # Build an insufficient set by providing fewer than `group_threshold` groups.
    flat = []
    if group_threshold > 1:
        # include only group_threshold-1 groups, each with their required member shares
        for gidx in range(group_threshold - 1):
            threshold, count = groups[gidx]
            flat.extend(mnemonics[gidx][:threshold])
    else:
        # group_threshold == 1: provide zero shares to force failure
        flat = []

    # Combining should fail due to insufficient groups/members
    try:
        _ = combine_mnemonics(flat, passphrase)
    except MnemonicError:
        pass
    except Exception:
        pass
    else:
        # If combine unexpectedly succeeds, that's a test failure — assert False
        assert False, "combine_mnemonics succeeded with insufficient shares"
