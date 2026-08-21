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

### [2026-08-22 05:05] GAP-NU-2 — QA gate fails open, self-heal never wired — FIXED

- **Repro (pre-fix):** `generation_core.py::_run_qa_pass` returned None (="no QA signal",
  treated as non-failure) on EVERY friction path: Playwright missing, no `_preview_starter`,
  server fails, QA run raises. QA was opt-in (`enable_qa_pass`) and `qa_self_heal.py`'s
  closed loop was never invoked by the generation path.
- **Fix (all in generation_core.py unless noted):**
  1. Gate is now DEFAULT-ON for web stacks; only two outcomes return None: non-web stack,
     or explicit `config["qa_gate"]="off"`.
  2. New `_FailedQA` dataclass (ok=False always) is returned for every cannot-run path:
     qa_browser import failure, non-callable starter, starter raising, starter returning no
     URL, Playwright missing, QA run exception, self-heal exception.
  3. Built-in `_default_preview_starter`: serves `frontend/` via ThreadingHTTPServer on a
     free localhost port when the caller wires no starter; registered in `_PREVIEW_SERVERS`
     and always shut down by `_stop_preview_servers()` at gate end.
  4. On QA failure the gate now drives `qa_self_heal.run_self_heal_loop` (max rounds via
     `config["qa_max_heal_rounds"]`, default 5, pool=self.pool) and returns the HealResult.
  5. generate() call site: any result with ok=False appends a HARD error
     (`qa: browser QA gate failed -- <reason>`), which flips result.success to False via the
     existing hard-error filter. Preview servers stopped afterwards.
- **New tests:** `tests/test_qa_gate_fail_closed.py` (8 cases): _FailedQA never ok; explicit
  off → None; non-web stacks → None; qa_browser unavailable → fail closed; starter raises →
  fail closed; starter returns no URL → fail closed; default starter serves real HTTP and
  stops cleanly; no frontend → None URL.
- **Test output (verbatim):**
  ```
  tests/test_qa_gate_fail_closed.py: 8 passed in 1.20s
  full suite: 1173 passed in 5.63s
  ```
- **Commit:** (with this entry)
