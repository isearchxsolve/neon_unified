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

### [2026-08-22 05:35] GAP-NU-3 + GAP-NU-4 — host-native test execution; 2 of 4 stacks had no runner — FIXED

- **Repro (pre-fix):** `_run_tests` ran `subprocess.run(["python","-m","pytest",...],
  cwd=project_dir)` directly on the HOST (no container, no network jail, no resource caps);
  expo-node and flutter-fastapi returned "No automated runner wired for {stack} in v5 core yet".
- **Fix (generation_core.py):**
  1. New `exec_isolation` config: `auto` (default; docker when daemon answers, host
     fallback), `docker` (forced; daemon/CLI missing => ran=False + loud BLOCKED),
     `host` (explicit unsafe opt-in). Unknown mode => ran=False.
  2. `_run_tests_docker`: hardened container run — `--network none --read-only
     --tmpfs /tmp --cpus 1.0 --memory 512m`, project bind-mounted at /project,
     image `python:3.11-slim` (config-overridable), 300s timeout.
  3. expo-node runner: requires package.json, runs `npx --yes jest --ci --passWithNoTests`.
  4. flutter-fastapi: python half via pytest as before; Flutter half gets `dart analyze`
     gate when dart/flutter SDK present (failure => passed=False with analyzer output);
     SDK absent => loud WARNING log, never a silent pass.
  5. nextjs-postgres: explicit loud BLOCKED record (ran=False) instead of the old generic
     "no runner wired" string — honest about the remaining gap.
- **Environment note:** Docker CLI 29.5.3 present but daemon DOWN on this host (Docker
  Desktop not running; launch attempted in background). Therefore docker mode is fully
  implemented + unit-verified via mocked daemon/CLI, but a live container run remains
  BLOCKED on daemon availability — recorded honestly, not faked.
- **New tests:** `tests/test_exec_isolation.py` (10 cases): unknown mode fails closed;
  forced docker w/o CLI => BLOCKED; forced docker w/ dead daemon => BLOCKED; docker mode
  asserts every hardening flag (--network none, --read-only, --cpus, --memory, --tmpfs);
  auto falls back to host when daemon down; expo-node requires package.json; expo-node
  runs jest; flutter w/o SDK still runs python half; dart analyze failure fails the gate;
  nextjs-postgres loud BLOCKED.
- **Test output (verbatim):**
  ```
  tests/test_exec_isolation.py: 10 passed in 0.15s
  full suite: 1183 passed in 5.67s
  ```
- **Commit:** (with this entry)

### [2026-08-22 06:10] GAP-NU-5 — flagship oiioii_clone_final output was a hollow shell — FIXED

- **Repro (pre-fix):** `oiioii_clone_final/backend/main.py` = 1 line
  (`from typing import Optional, List`); `src/api.py` and `src/workflows.py` = 1-line
  comments; `tests/test_api.py` and `tests/test_workflows.py` = 1-line comments;
  the app's own suite had 2 genuine failures (46 passed, 2 failed).
- **Root cause of the 2 failures:** the generated tests were self-contradictory —
  `test_complete_job_fails_for_non_running_job` requires complete_job(PENDING)=False while
  `test_start_job_fails_for_completed_job` / `test_cancel_job_fails_for_completed_job`
  called complete_job directly on a PENDING job and expected it to succeed. The service's
  strict PENDING->RUNNING->COMPLETED state machine is the correct contract; the two tests
  forgot `start_job`. Fixed the TESTS (service untouched), per rule 7 (fix wrong tests AND
  log why).
- **Fix (completed the app instead of renaming — tests/baseline depends on this dir name):**
  1. `src/workflows.py`: full thread-safe WorkflowService (create/get/list/advance/
     attach_job/deactivate) over workflows_store + get_workflow_service singleton.
  2. `src/api.py`: complete FastAPI layer — register/login/logout, project CRUD with
     ownership enforcement (403 for non-owners), workflow create/advance, job
     create/start/complete/cancel, Bearer-token auth dependency (401 without), pydantic
     request models, stage validation (422 on unknown).
  3. `backend/main.py`: real entrypoint (`create_app()` + CORS + /api/health).
  4. `tests/test_api.py`: 9 real TestClient integration tests (no mocks) incl. auth
     enforcement, ownership, workflow lifecycle, job lifecycle, 409 on illegal transitions.
  5. `tests/test_workflows.py`: 7 WorkflowService unit tests.
  6. `frontend/styles.css`: already had full workspace CSS (earlier wc -l 0 was a
     line-counting artifact of a single-line minified file — verified content present).
- **Test output (verbatim):**
  ```
  oiioii_clone_final/tests: 63 passed in 2.10s   (was 46 passed, 2 failed)
  boot check: health {'status': 'ok'}; unauth /api/projects -> 401
  full repo suite: 1183 passed in 5.43s
  ```
- **Commit:** (with this entry)

### [2026-08-22 06:45] GAP-NU-6 — live generation proof — BLOCKED (NIM inference wall, evidence captured)

- **Attempt:** wrote `live_proof_run.py` (real Provider/ProviderPool from neon_architect,
  model meta/llama-3.3-70b-instruct, read_timeout=600s, qa_gate=off because the default
  preview starter serves raw Vite source without bundling — a bundling starter is follow-up
  work). Launched fresh run into `_live_proof_fastapi_react_20260822/`.
- **Observed:** scaffold OK (13 base files), then the architect NIM call never returned;
  the process died silently mid-call (no traceback, no summary file).
- **Isolation evidence (all captured live, 2026-08-22 ~06:35):**
  1. `GET /v1/models` with the same key: **200 OK in 0.3s, 102 models**, llama-3.3-70b present.
  2. Non-streaming chat completion, 60s timeout: APITimeoutError.
  3. Same, 180s timeout: APITimeoutError.
  4. Streaming on llama-3.3-70b (90s): APITimeoutError, zero chunks.
  5. Streaming on nvidia/llama-3.1-nemotron-nano-8b-v1 (90s): ReadTimeout, zero chunks.
- **Diagnosis:** auth + catalog are healthy; INFERENCE never returns a first token on two
  different models including an 8B nano model. This is a provider-side quota/throttle wall
  on this key, not a code defect — consistent with UNIFIED.md limitation #2 ("True 429/RPM —
  quota, not code; use healthy keys / backoff"). Per remediation rule 3 this is logged
  BLOCKED with exact evidence, NOT faked.
- **Artifacts:** `live_proof_run.py` (committed, reusable the moment a healthy key exists),
  `_live_proof_run.log`, partial scaffold in `_live_proof_fastapi_react_20260822/`.
- **Unblock path:** run `python live_proof_run.py` with a key that has live NIM quota;
  acceptance unchanged: success=True, consistency clean, generated tests pass.

### [2026-08-22 06:50] GAP-NU-7 — 641KB monoliths with no growth control — FIXED (freeze + plan)

- **Repro:** `neon_architect.py` 641,222 bytes, `neon_architect_v5.py` 643,861 bytes, single
  files containing 17 tool classes, the agent loop, TUI, FastAPI demo, Flutter template
  strings, and 6 specialized agents.
- **Fix (minimal, per prompt):** no full refactor this sweep.
  1. `docs/MONOLITH_EXTRACTION_PLAN.md`: verified line map of every class in the monolith,
     proposed module layout (neon/config, ui, pacing, providers, tools/*, context, agent,
     tui, templates, specialists), dependency-safe extraction order, known hazards
     (Flutter `{{ }}` template strings, TodoTool isolation fixes).
  2. `tests/test_monolith_freeze.py`: hard 660,000-byte ceiling on both monoliths; fails CI
     if either grows; skips cleanly if a monolith is deleted (extraction complete).
- **Test output (verbatim):**
  ```
  tests/test_monolith_freeze.py: 2 passed in 0.04s
  full suite: 1185 passed in 5.47s
  ```
- **Commit:** (with this entry)
