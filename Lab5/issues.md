# Issues found in `scheduler_system.py`

Before: Pylint 5.60/10, Bandit 1 High + 1 Low, Flake8 13 findings. After: Pylint 10.00/10, Bandit 0, Flake8 0.
Reports are in `reports/before/` and `reports/after/`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `os.system("cat " + file)` (B605, High) | Security | 43 | Shell command built by string concatenation; a crafted filename means command injection. | Removed the shell call; read the file with `open()` and print it. |
| Bare `except: pass` (B110 / E722 / W0702) | Security / Bug | 23-28 | Swallows every error silently, so cancelling an unknown id (77) looked like it worked. | Explicit `if reservation_id not in reservations` check with a message. |
| Mutable default arg `equipment_list=[]` (W0102) | Bug | 11 | The list is shared across calls, so reservations can alias the same list. | Default `None`, copy into a new list inside the function. |
| Unvalidated slots (`"14-12"`, `1530`) | Logic bug | 30-32, 48-49 | Reversed range gives a negative length; an int slot crashes `.split`. | Added `parse_slot()` that validates format and range; bookings with bad slots are rejected. |
| Equipment can go negative / KeyError | Logic bug | 16-17 | The pool is decremented with no availability check (webcam stock is 1) and an unknown item raises KeyError. | Check availability for all items before allocating anything. |
| Global counter (W0603) | Design | 12 | `global next_reservation`. | Replaced with `itertools.count(1)`. |
| Files opened without `with` / encoding (R1732, W1514) | Resource leak | 35, 40 | `logConflicts` never closed its file handle. | `with open(..., encoding="utf-8")`. |
| `logConflicts` naming, `%` formatting, `.items()`, docstrings (C0103, C0209, C0206, C0114/C0116) | Style | various | Non-snake_case name, old-style formatting, missing docstrings. | Renamed to `log_conflicts`, f-strings, `.values()`, added docstrings. |
| Unused variables `a`, `a_more`, `c` (F841 / W0612) | Cleanliness | 46-49 | Assigned, never used. | Dropped the assignments. |
| E302 / E305 / E501 | Formatting | various | Blank lines, long lines. | Reformatted to PEP 8. |
| `main()` runs on import | Design | 59 | Importing the module runs the demo. | `if __name__ == "__main__":` guard. |
