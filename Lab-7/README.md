# Lab 7: Fuzzing for Input Validation Bugs — Cloud Storage Tier

Repo assigned: `SETAPESU26/L6_L7_12_cloud_storage_tier`

| File | Purpose |
|------|---------|
| `processor.py` | Fixed application (the docstring lists every bug Hypothesis found and the fix) |
| `test_processor.py` | Completed Hypothesis fuzz tests for all three functions |
| `Lab7_Fuzz_Testing_Screenshots.pdf` | Screenshots: buggy run, failing tests, fixed run, passing tests |
| `screenshots/` | The same screenshots as images |

```bash
pip install hypothesis pytest
python processor.py
pytest test_processor.py
```
