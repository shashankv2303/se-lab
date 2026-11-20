"""Lab 6 - Code (line) coverage tests for cloud_storage_tier.py.

Run:
    coverage run -m pytest CodeCoverageTest_cloud_storage_tier.py
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


# ---------- process_storage_tenants ----------

def test_single_active_hot_tenant():
    result = process_storage_tenants([tenant("hot", [bucket(100, egress=50)])], 10.0)
    assert result == {"total_billed": 2.5, "status": "BILLED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_storage_tenants("not a list", 5.0)


def test_inactive_tenant_is_skipped():
    result = process_storage_tenants([tenant(active=False, buckets=[bucket()])], 1.0)
    assert result == {"total_billed": 0.0, "status": "ZERO_USAGE"}


def test_cool_tier_rate():
    result = process_storage_tenants([tenant("cool", [bucket(200)])], 0.0)
    assert result["total_billed"] == 3.0


def test_archive_tier_rate_and_large_bucket_discount():
    result = process_storage_tenants([tenant("archive", [bucket(1000)])], 0.0)
    assert result["total_billed"] == 4.5  # 1000 * 0.005 * 0.90


def test_unknown_tier_is_flagged_and_skipped():
    result = process_storage_tenants([tenant("platinum", [bucket()])], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_non_positive_bucket_size_is_flagged():
    result = process_storage_tenants([tenant("hot", [bucket(0), bucket(100)])], 0.0)
    assert result["total_billed"] == 2.5


def test_corrupted_bucket_on_hot_tier_is_not_charged():
    result = process_storage_tenants([tenant("hot", [bucket(100, corrupted=True)])], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_corrupted_bucket_on_archive_zeroes_charge_and_stops():
    buckets = [bucket(100), bucket(100, corrupted=True), bucket(100)]
    result = process_storage_tenants([tenant("archive", buckets)], 0.0)
    assert result["status"] == "ZERO_USAGE"


def test_egress_over_100gb_is_surcharged():
    result = process_storage_tenants([tenant("hot", [bucket(100, egress=150)])], 0.0)
    assert result["total_billed"] == 6.5  # 2.5 + 50 * 0.08


def test_backup_vault_adds_support_fee():
    result = process_storage_tenants([tenant("hot", [bucket(100)], vault=True)], 10.0)
    assert result["total_billed"] == 12.5


def test_audit_flagged_when_more_than_four_flags():
    flagged = [bucket(0)] * 5
    result = process_storage_tenants([tenant("hot", flagged + [bucket(100)])], 0.0)
    assert result["status"] == "AUDIT_FLAGGED"
    assert result["total_billed"] == 2.5


# ---------- monitor_replication_latency ----------

def test_no_data():
    assert monitor_replication_latency([]) == "NO_DATA"


def test_sync_lag_alert_on_two_consecutive_spikes():
    assert monitor_replication_latency([[10, 250, 300]]) == "SYNC_LAG_ALERT"


def test_synced_when_no_consecutive_spikes():
    assert monitor_replication_latency([[10, 250, 20, 250]]) == "SYNCED"
