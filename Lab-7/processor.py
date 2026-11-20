"""Storage helpers hardened against invalid input (Lab 7 - fuzz testing fixes).

Bugs found by Hypothesis in the original version, and how they were fixed:

parse_storage_quota
  * None / non-str input        -> AttributeError   -> type check
  * '' , 'GB', 'abc', '1.5GB'   -> ValueError       -> validate before int()
  * unknown unit ('10XB', '5')  -> KeyError         -> look the unit up with .get()
  * negative values ('-5GB')    -> silently accepted -> rejected
  * huge digit strings          -> ValueError/OverflowError -> caught

compute_compression_ratio
  * None / non-str input        -> AttributeError   -> type check
  * no ':' or more than one ':' -> ValueError       -> split into exactly two parts
  * non-numeric parts           -> ValueError       -> validated float()
  * compressed size 0           -> ZeroDivisionError -> rejected
  * negative / nan / inf sizes  -> meaningless ratio -> rejected

lookup_bandwidth_tier_rate
  * None / non-str input        -> AttributeError   -> type check
  * short or unknown prefix     -> KeyError         -> .get() with None default

Invalid input now yields a clear message (parse_storage_quota) or None (the
other two) instead of an exception.
"""
import math

MULTIPLIERS = {"MB": 0.001, "GB": 1.0, "TB": 1000.0}
TIER_RATES = {"HOT": 0.08, "COL": 0.05, "ARC": 0.02}
INVALID_QUOTA = "Invalid quota"


def parse_storage_quota(quota_str):
    """Parse '<digits><MB|GB|TB>' into GB. Returns 'Invalid quota' on bad input."""
    if not isinstance(quota_str, str):
        return INVALID_QUOTA
    cleaned = quota_str.strip().upper()
    val_str, unit = cleaned[:-2], cleaned[-2:]
    multiplier = MULTIPLIERS.get(unit)
    if multiplier is None or not (val_str.isascii() and val_str.isdigit()):
        return INVALID_QUOTA
    try:
        gb_total = int(val_str) * multiplier
    except (ValueError, OverflowError):
        return INVALID_QUOTA
    return f"Quota: {gb_total:.2f} GB"


def _parse_size(text):
    """Return a finite, non-negative float or None."""
    try:
        value = float(text)
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def compute_compression_ratio(size_metric_str):
    """Compute raw/compressed from 'raw:compressed'. Returns None on bad input."""
    if not isinstance(size_metric_str, str):
        return None
    parts = size_metric_str.split(":")
    if len(parts) != 2:
        return None
    raw_bytes = _parse_size(parts[0])
    comp_bytes = _parse_size(parts[1])
    if raw_bytes is None or comp_bytes is None or comp_bytes == 0:
        return None
    try:
        return round(raw_bytes / comp_bytes, 2)
    except OverflowError:
        return None


def lookup_bandwidth_tier_rate(tier_descriptor):
    """Look up the egress rate per GB from the first 3 letters. None if unknown."""
    if not isinstance(tier_descriptor, str):
        return None
    return TIER_RATES.get(tier_descriptor.strip().upper()[:3])


def main():
    print("==== Running parse_storage_quota ====")
    q_input = input("Enter quota (e.g. 500MB, 10GB, 2TB): ")
    print(parse_storage_quota(q_input))

    print("\n==== Running compute_compression_ratio ====")
    c_input = input("Enter raw:compressed bytes (e.g. 1024:256): ")
    ratio = compute_compression_ratio(c_input)
    print("Compression Ratio:", "Invalid input" if ratio is None else ratio)

    print("\n==== Running lookup_bandwidth_tier_rate ====")
    t_input = input("Enter tier descriptor (e.g. HOT_TIER, COLD, ARCHIVE): ")
    rate = lookup_bandwidth_tier_rate(t_input)
    print("Rate per GB:", "Unknown tier" if rate is None else f"$ {rate}")


if __name__ == "__main__":
    main()
