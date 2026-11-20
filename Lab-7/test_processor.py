"""Lab 7 - Hypothesis fuzz tests for processor.py.

Each property says: whatever string (or None) we feed the function, it must
not crash.  Hypothesis generates hundreds of inputs and shrinks any failure to
the smallest reproducing example.
"""
from hypothesis import given, strategies as st
from processor import (
    parse_storage_quota,
    compute_compression_ratio,
    lookup_bandwidth_tier_rate,
)


@given(st.text() | st.none())
def test_parse_storage_quota_no_crash(s):
    try:
        parse_storage_quota(s)
    except Exception as e:
        assert False, f"parse_storage_quota crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_compute_compression_ratio_safe(s):
    try:
        compute_compression_ratio(s)
    except Exception as e:
        assert False, f"compute_compression_ratio crashed with: {type(e).__name__}: {e}"


@given(st.text() | st.none())
def test_lookup_bandwidth_tier_rate_safe(s):
    try:
        lookup_bandwidth_tier_rate(s)
    except Exception as e:
        assert False, f"lookup_bandwidth_tier_rate crashed with: {type(e).__name__}: {e}"
