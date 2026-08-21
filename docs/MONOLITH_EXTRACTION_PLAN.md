# Monolith Extraction Plan — neon_architect.py (GAP-NU-7)

`neon_architect.py` is a 641KB single file (~13,000+ lines) containing the
entire agent runtime. `neon_architect_v5.py` is a 643KB near-duplicate. Any
merge conflict or partial edit in these files is catastrophic. This plan
freezes their size NOW (enforced by `tests/test_monolith_freeze.py`) and
maps the extraction into modules for a future sweep.

## Freeze rule

`neon_architect.py` and `neon_architect_v5.py` must not grow past
**660,000 bytes** (current: 641,222 / 643,861). New functionality goes into
new modules, not into the monoliths. The freeze test fails CI if violated.

## Current structure (verified line map, 2026-08-22)

| Lines (approx) | Content | Proposed module |
|---|---|---|
| 1–788 | imports, constants, `verify_nim`, config defaults | `neon/config.py` |
| 789–1234 | `UI` (rich console rendering) | `neon/ui.py` |
| 1235–1346 | `TokenBucket`, `TokenMeter` | `neon/pacing.py` |
| 1347–1586 | `Provider`, `ProviderPool`, pool builder | `neon/providers.py` |
| 1587–1761 | `ToolResult`, `Tool` base | `neon/tools/base.py` |
| 1762–2343 | `ReadTool`, `WriteTool` | `neon/tools/files.py` |
| 2344–2877 | `EditTool`, `SearchTool`, `GlobTool`, `LsTool` | `neon/tools/edit_search.py` |
| 2878–4292 | `RunTool`, `ProductionValidatorTool` | `neon/tools/exec.py` |
| 4293–5034 | `TaskTool`, `ModulesTool`, `TodoTool`, `WebSearchTool`, `BrowsePageTool` | `neon/tools/task_web.py` |
| 5035–5814 | `ContextManager`, `EnvironmentCapabilities` | `neon/context.py` |
| 5815–9656 | `NeonArchitect` main agent loop | `neon/agent.py` |
| 9657–10360 | `_TuiLogSink`, TUI plumbing | `neon/tui.py` |
| 10361–11505 | FastAPI demo models + embedded Flutter template strings | `neon/templates/` (move strings to files) |
| 11506–end | `SpecializedAgent` + Planner/Architect/Designer/Frontend/Backend/Database agents | `neon/specialists.py` |

## Extraction order (dependency-safe)

1. `neon/pacing.py` (no deps) → 2. `neon/providers.py` → 3. `neon/tools/*`
(base first) → 4. `neon/context.py` → 5. `neon/specialists.py` →
6. `neon/templates/` → 7. `neon/agent.py` (last, imports everything).

Each step: move code, leave a re-export shim in the monolith
(`from neon.pacing import TokenBucket  # noqa`), keep the freeze test green,
run the full suite. Delete `neon_architect_v5.py` once `neon_architect.py`
is fully extracted (it is a maintained alias, per FLEET_WORKLOG step 5).

## Known hazards

- The Flutter template strings (~lines 10990–11179) contain `{{ }}` format
  placeholders — move them as raw files, never through f-string refactors.
- `TodoTool` instance-isolation fixes (FLEET_WORKLOG steps 6–7) and the
  `EditTool` ambiguous-match warning must survive extraction unchanged;
  their regression tests in `tests/` are the safety net.
