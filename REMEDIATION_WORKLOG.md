# Remediation Worklog — neon_unified

Executes MASTER_REMEDIATION_PROMPT.md (D:\omniroute-monetizer). One gap per entry,
verify → fix → test → log → commit.

### [2026-08-22 04:30] GAP-NU-1 — Suite does not collect from clean checkout — FIXED

- **Repro (pre-fix):** `python -m pytest --collect-only -q` → 1,160 collected, 1 ERROR:
  `tests\baseline\test_baseline.py:8` imports `oiioii_clone_final.src.jobs` →
  `oiioii_clone_final\src\jobs.py:13: from src.models import ...` →
  `ModuleNotFoundError: No module named 'src'`. No conftest.py existed anywhere.
- **Root cause:** generated app uses bare absolute imports (`from src.models import ...`)
  that only resolve with the clone root on sys.path; nothing provided that.
- **Fix:** new root `conftest.py`. It temporarily puts `oiioii_clone_final` on sys.path just
  long enough to bind `sys.modules['src']`, then removes it — because five clones each ship a
  `backend/` package and a permanent per-clone sys.path entry would let one clone's bare
  `backend` import silently bind to another clone's package. Verified no `src/` collision
  (only oiioii_clone_final has one).
- **Test output (verbatim):**
  ```
  1165 tests collected in 1.83s
  1165 passed in 6.39s
  ```
  0 collection errors. The fleet worklog's "1,160/1,160" claim is now reproducible from a
  clean checkout (count grew to 1,165 because the previously-erroring baseline module now
  collects its 5 test cases).
- **Also committed:** pre-existing AGENTS.md rules-block prepend (was dirty in working tree).
- **Commit:** (this entry committed together with the fix)
