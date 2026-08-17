#!/usr/bin/env python3
"""Run one observable, fresh flutter-fastapi generation against NIM.

Usage:
    python scripts/run_live_flutter_verification.py --project ./neon_flutter_release

This intentionally runs one job only. It emits a redacted JSON evidence record
and never prints API-key material.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generation_core import GenerationOrchestratorV5
from neon_architect import DEFAULT_CONFIG, build_pool


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="fresh output directory")
    args = parser.parse_args()
    key = (
        os.environ.get("NIM_API_KEY")
        or os.environ.get("NVIDIA_API_KEY")
        or os.environ.get("NGC_API_KEY")
        or ""
    ).strip()
    if not key:
        print(json.dumps({"success": False, "error": "NIM_API_KEY is not set"}))
        return 2

    project = Path(args.project).resolve()
    if project.exists() and any(project.iterdir()):
        print(json.dumps({"success": False, "error": f"project is not fresh: {project}"}))
        return 2
    project.mkdir(parents=True, exist_ok=True)

    config = dict(DEFAULT_CONFIG)
    config["api_key"] = key
    config["project_dir"] = str(project)
    observed: list[str] = []

    def progress(phase: str, message: str) -> None:
        line = f"{phase}: {message}"
        observed.append(line)
        print(line, flush=True)

    result = GenerationOrchestratorV5(build_pool(config), config).generate(
        "Build a notes app with auth and note list",
        project,
        stack="flutter-fastapi",
        on_progress=progress,
    )
    payload = {
        "run_id": result.run_id,
        "success": result.success,
        "stack": result.stack,
        "files_created": len(result.files_created),
        "files_generated": len(result.files_generated),
        "repair_rounds": result.repair_rounds,
        "errors": result.errors,
        "warnings": result.warnings,
        "test_ran": bool(result.test_output and result.test_output.ran),
        "test_passed": bool(result.test_output and result.test_output.passed),
        "consistency_lines": [line for line in observed if "consistency" in line or "repair" in line],
    }
    print("VERIFICATION_RESULT=" + json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
