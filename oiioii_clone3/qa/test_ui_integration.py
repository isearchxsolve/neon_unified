"""QA integration tests — Playwright.

Run:
  pip install -r qa/requirements-qa.txt
  playwright install chromium
  # start the app on base_url first
  pytest qa/test_ui_integration.py -v
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))  # allow importing package qa_browser if present

try:
    from qa_browser import UISpec, Flow, Step, VisualPage, run_qa_suite, HAS_PLAYWRIGHT
except ImportError:
    # inline minimal skip
    HAS_PLAYWRIGHT = False
    run_qa_suite = None

SPEC_PATH = Path(__file__).parent / "ui_spec.json"


def load_spec() -> "UISpec":
    raw = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    flows = []
    for f in raw.get("flows", []):
        steps = [Step(**s) for s in f.get("steps", [])]
        flows.append(Flow(id=f["id"], description=f.get("description", ""), steps=steps))
    visuals = [VisualPage(**v) for v in raw.get("visual_pages", [])]
    vp = raw.get("viewport", [1280, 720])
    return UISpec(
        base_url=raw.get("base_url", "http://127.0.0.1:5173"),
        flows=flows,
        visual_pages=visuals,
        must_have_selectors=raw.get("must_have_selectors", ["body"]),
        must_have_text=raw.get("must_have_text", []),
        viewport=(vp[0], vp[1]),
    )


@pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="playwright not installed")
def test_ui_integration_suite(tmp_path):
    spec = load_spec()
    out = ROOT / "qa_out"
    result = run_qa_suite(spec, out_dir=out, baseline_dir=out / "baselines", headless=True)
    assert result.report_path
    # Soft: suite may fail if app not running — expose report
    if not result.ok:
        pytest.fail(f"QA suite failed — see {result.report_path}\n errors={result.errors}")
