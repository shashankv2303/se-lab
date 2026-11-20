"""Lab 6 - Branch coverage tests for cloud_storage_tier.py.

Run:
    coverage run --branch -m pytest BranchCoverageTest_cloud_storage_tier.py
    coverage report -m
"""
import pytest
from cloud_storage_tier import process_storage_tenants, monitor_replication_latency


def tenant(tier="hot", buckets=None, active=True, vault=False):
    return {
        "account_active": active,
        "tier": tier,
        "has_backup_vault": vault,
        "buckets": buckets if buckets is not None else [],
    }


def bucket(size=100, corrupted=False, egress=0):
    return {"size_gb": size, "corrupted": corrupted, "egress_gb": egress}


# ---------- input validation: both halves of the `or` and both outcomes ----------

@pytest.mark.parametrize("tenants, fee", [("not a list", 5.0), (None, 5.0), ([], -1.0)])
def test_invalid_input_raises(tenants, fee):
    with pytest.raises(ValueError):
        process_storage_tenants(tenants, fee)


def test_valid_empty_list_is_zero_usage():
    assert process_storage_tenants([], 0.0) == {"total_billed": 0.0, "status": "ZERO_USAGE"}


# ---------- account_active True / False ----------

def test_inactive_tenant_is_skipped():
    result = process_storage_tenants([tenant(active=False, buckets=[bucket()])], 1.0)
    assert result["status"] == "ZERO_USAGE"


def test_missing_account_active_defaults_to_inactive():
    result = process_storage_tenants([{"tier": "hot", "buckets": [bucket()]}], 1.0)
    assert result["status"] == "ZERO_USAGE"


# ---------- tier if / elif / elif / else ----------

@pytest.mark.parametrize("tier, size, expected", [
    ("hot", 100, 2.5),
    ("cool", 200, 3.0),
    ("archive", 400, 2.0),
])
def test_each_tier_rate(tier, size, expected):
    assert process_storage_tenants([tenant(tier, [bucket(size)])], 0.0)["total_billed"] == expected


def test_default_tier_is_hot_when_missing():
    t = {"account_active": True, "buckets": [bucket(100)]}
    assert process_storage_tenants([t], 0.0)["total_billed"] == 2.5


def test_unknown_tier_is_flagged_and_skipped():
    result = process_storage_tenants([tenant("platinum", [bucket()])], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_tenant_with_no_buckets_key_charges_nothing():
    t = {"account_active": True, "tier": "hot"}
    assert process_storage_tenants([t], 0.0)["status"] == "ZERO_USAGE"


# ---------- bucket loop: empty and non-empty ----------

def test_tenant_with_empty_bucket_list():
    assert process_storage_tenants([tenant("hot", [])], 0.0)["status"] == "ZERO_USAGE"


# ---------- size_gb <= 0 / corrupted / > 500 / normal ----------

@pytest.mark.parametrize("size", [0, -5])
def test_non_positive_bucket_size_is_flagged(size):
    result = process_storage_tenants([tenant("hot", [bucket(size), bucket(100)])], 0.0)
    assert result["total_billed"] == 2.5


def test_missing_size_defaults_to_zero_and_is_flagged():
    result = process_storage_tenants([tenant("hot", [{"corrupted": False}])], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_bucket_on_hot_tier_is_not_charged():
    result = process_storage_tenants([tenant("hot", [bucket(100, corrupted=True)])], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_bucket_on_cool_tier_keeps_earlier_charges():
    buckets = [bucket(100), bucket(100, corrupted=True)]
    assert process_storage_tenants([tenant("cool", buckets)], 0.0)["total_billed"] == 1.5


def test_corrupted_bucket_on_archive_zeroes_charge_and_stops():
    buckets = [bucket(100), bucket(100, corrupted=True), bucket(100)]
    result = process_storage_tenants([tenant("archive", buckets, vault=True)], 7.0)
    assert result["total_billed"] == 7.0  # only the vault fee survives


def test_bucket_over_500gb_gets_10_percent_discount():
    assert process_storage_tenants([tenant("hot", [bucket(1000)])], 0.0)["total_billed"] == 22.5


def test_bucket_exactly_500gb_gets_no_discount():
    assert process_storage_tenants([tenant("hot", [bucket(500)])], 0.0)["total_billed"] == 12.5


# ---------- egress > 100 True / False (incl. boundary) ----------

def test_egress_over_100gb_is_surcharged():
    assert process_storage_tenants([tenant("hot", [bucket(100, egress=150)])], 0.0)["total_billed"] == 6.5


def test_egress_exactly_100gb_is_free():
    assert process_storage_tenants([tenant("hot", [bucket(100, egress=100)])], 0.0)["total_billed"] == 2.5


def test_egress_is_charged_on_corrupted_bucket_too():
    result = process_storage_tenants([tenant("hot", [bucket(100, corrupted=True, egress=200)])], 0.0)
    assert result["total_billed"] == 8.0  # 100 * 0.08


# ---------- backup vault True / False ----------

def test_backup_vault_adds_support_fee():
    assert process_storage_tenants([tenant("hot", [bucket(100)], vault=True)], 10.0)["total_billed"] == 12.5


def test_no_backup_vault_no_fee():
    assert process_storage_tenants([tenant("hot", [bucket(100)], vault=False)], 10.0)["total_billed"] == 2.5


# ---------- final status: AUDIT_FLAGGED / ZERO_USAGE / BILLED ----------

def test_audit_flagged_when_more_than_four_flags():
    result = process_storage_tenants([tenant("hot", [bucket(0)] * 5 + [bucket(100)])], 0.0)
    assert result == {"total_billed": 2.5, "status": "AUDIT_FLAGGED"}


def test_exactly_four_flags_is_not_audit_flagged():
    result = process_storage_tenants([tenant("hot", [bucket(0)] * 4 + [bucket(100)])], 0.0)
    assert result["status"] == "BILLED"


def test_billed_status_with_multiple_tenants():
    tenants = [tenant("hot", [bucket(100)]), tenant("cool", [bucket(200)])]
    assert process_storage_tenants(tenants, 0.0) == {"total_billed": 5.5, "status": "BILLED"}


# ---------- monitor_replication_latency ----------

def test_no_data_for_empty_and_none():
    assert monitor_replication_latency([]) == "NO_DATA"
    assert monitor_replication_latency(None) == "NO_DATA"


def test_sync_lag_alert_on_two_consecutive_spikes():
    assert monitor_replication_latency([[10, 250, 300]]) == "SYNC_LAG_ALERT"


def test_alert_found_on_a_later_node():
    assert monitor_replication_latency([[10, 20], [300, 400]]) == "SYNC_LAG_ALERT"


def test_streak_resets_on_a_healthy_reading():
    assert monitor_replication_latency([[250, 20, 250, 20]]) == "SYNCED"


def test_exactly_200ms_is_not_a_spike():
    assert monitor_replication_latency([[200, 200, 200]]) == "SYNCED"


def test_node_with_no_logs_is_synced():
    assert monitor_replication_latency([[]]) == "SYNCED"
