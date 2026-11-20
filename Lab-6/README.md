# Lab 6: Code and Branch Coverage — Cloud Storage Tier

Repo assigned: `SETAPESU26/L6_L7_12_cloud_storage_tier`

| File | Purpose |
|------|---------|
| `cloud_storage_tier.py` | Application under test (unchanged) |
| `test_cloud_storage.py` | Starter test (1 test) |
| `CodeCoverageTest_cloud_storage_tier.py` | Tests for line coverage: **100%** (57/57 statements) |
| `BranchCoverageTest_cloud_storage_tier.py` | Tests for branch coverage: **100%** (40/40 branches) |
| `screenshots/` | Terminal output of both coverage runs |

```bash
pip install coverage pytest
coverage run -m pytest CodeCoverageTest_cloud_storage_tier.py && coverage report -m
coverage run --branch -m pytest BranchCoverageTest_cloud_storage_tier.py && coverage report -m
```
