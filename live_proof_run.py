"""GAP-NU-6 live proof driver: one clean fastapi-react generation via NIM.

Uses the real Provider/ProviderPool from neon_architect with the NIM key
from the environment (never printed). QA gate is explicitly OFF for this
run: the default preview starter serves the Vite source tree raw (no
bundling), so raw-TSX script errors would fail the gate on tooling, not on
substance. A bundling preview starter is tracked as follow-up work.
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from neon_architect import Provider, ProviderPool  # noqa: E402
from generation_core import GenerationOrchestratorV5  # noqa: E402

API_KEY = os.environ.get("NIM_API_KEY") or os.environ.get("NVIDIA_API_KEY") or ""
if not API_KEY:
    print("BLOCKED: no NIM_API_KEY / NVIDIA_API_KEY in environment")
    sys.exit(2)

MODEL_CFG = {
    "id": "meta/llama-3.3-70b-instruct",
    "name": "llama-3.3-70b",
    "rpm": 40,
    "max_tokens": 8192,
    "ctx_window": 131072,
    "thinking": False,
    "extra_body": None,
    "temperature": 0.3,
    "top_p": 0.95,
}

provider = Provider(
    "nim-live-proof",
    "https://integrate.api.nvidia.com/v1",
    API_KEY,
    MODEL_CFG,
    connect_timeout=30.0,
    read_timeout=600.0,
)
pool = ProviderPool([provider])

out_dir = Path(__file__).resolve().parent / "_live_proof_fastapi_react_20260822"
orch = GenerationOrchestratorV5(pool, {
    "qa_gate": "off",
    "exec_isolation": "host",
})

t0 = time.monotonic()


def prog(phase, msg):
    print(f"[{time.monotonic() - t0:7.1f}s] {phase}: {msg}", flush=True)


result = orch.generate(
    description=(
        "Build a task tracker web app: users create tasks with title and "
        "priority, list them on a dashboard, and mark them done. FastAPI "
        "backend with a React frontend."
    ),
    project_dir=out_dir,
    stack="fastapi-react",
    on_progress=prog,
)

summary = {
    "success": result.success,
    "run_id": result.run_id,
    "stack": result.stack,
    "files_created": len(result.files_created),
    "files_generated": len(result.files_generated),
    "errors": result.errors,
    "warnings": result.warnings,
    "repair_rounds": result.repair_rounds,
    "test_ran": result.test_output.ran if result.test_output else None,
    "test_passed": result.test_output.passed if result.test_output else None,
    "test_output_tail": (result.test_output.output[-1500:]
                         if result.test_output else None),
    "duration_sec": round(time.monotonic() - t0, 1),
}
(out_dir / "LIVE_PROOF_SUMMARY.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2), flush=True)
sys.exit(0 if result.success else 1)
