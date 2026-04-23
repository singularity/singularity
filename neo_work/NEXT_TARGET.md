# Neo's Next Target — Singularity Issue #343

## The Issue
**#343 Crash bug** — Segmentation fault in pygame parachute during new game start

## Root Cause (mechanism identified)
1. User clicks "New Game" → `new_game()` called → dialog handlers fire
2. `map.py` `show()` method at line ~580 calls `log_error()` from `safety.py`
3. `log_error()` calls Python's `logging.getLogger().error()` which opens a log file
4. This file I/O while pygame is in a parachute state → segfault

**The crash surface:** `safety.py` line 48-52 - the logging call happens inside `log_error()` and is NOT wrapped in exception handling.

```python
# safety.py lines 43-52
def log_error(error_message, *args):
    if len(args):
        sys.stderr.write((error_message % args) + "\n")
    else:
        sys.stderr.write(error_message + "\n")
    if len(logging.getLogger().handlers) > 0:
        try:
            logging.getLogger().error(error_message, *args)
        except IOError:  # Probably access denied with --singledir. That's ok
            pass
```

The `try/except` only catches `IOError`. On pygame parachute crash, the logging module itself can segfault — not raise an exception. The fix should use a broad `except Exception` to catch any failure in the logging call, or avoid calling Python logging entirely during crash states.

## Suggested Fix
Wrap the entire logging block in a broad exception handler. Example pattern:

```python
try:
    logging.getLogger().error(error_message, *args)
except Exception:
    pass  # Logging failure is non-fatal
```

## Context
- Fork: `/home/openclaw/neo_forks/singularity/`
- Branch: `neo/safety-crash-fix` (already created from master)
- Tests: `PYTHONPATH=. python3 -m pytest tests/` (31 tests exist)
- No pygame window needed for the fix — static code fix + existing tests validate

## Instructions
1. Implement the fix in `safety.py`
2. Run full test suite to verify no regressions
3. Commit to `neo/safety-crash-fix` branch
4. Push to `Dstoob/singularity` fork
5. Open PR against `singularity/singularity`
6. Update `neo_work/WORK_ITEMS.md`
