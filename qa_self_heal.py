#!/usr/bin/env python3
"""
QA Self-Healing Loop
====================

Not just testing — a closed loop:

  run browser QA → if fail → build repair brief → drive agent/fix → re-QA → repeat

Integrates:
  - qa_browser.run_qa_suite (Playwright + visual diff)
  - Full Neon agent (optional) or generation repair prompts
  - Acceptance criteria from oiioii / custom UISpec

Usage:
  python qa_self_heal.py --base-url http://127.0.0.1:5173 --project ./app --max-rounds 5

  # with full agent repair
  python qa_self_heal.py --base-url http://127.0.0.1:5173 --project ./app --use-full-agent
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from qa_browser import (
    UISpec,
    QAResult,
    run_qa_suite,
    oiioii_workspace_spec,
    default_web_app_spec,
    HAS_PLAYWRIGHT,
)


@dataclass
class HealRound:
    round_num: int
    qa_ok: bool
    repair_attempted: bool
    detail: str = ""
    report_path: str = ""
    duration_sec: float = 0.0


@dataclass
class HealResult:
    success: bool
    rounds: List[HealRound] = field(default_factory=list)
    final_qa: Optional[QAResult] = None
    stop_reason: str = ""
    repair_brief_path: str = ""


def build_repair_brief(qa: QAResult, project_dir: Path) -> str:
    """Turn QA failures into an actionable agent repair prompt."""
    lines = [
        "UI QA FAILED. Fix the application so these checks pass.",
        "Do not rewrite everything — surgically fix failing flows, selectors, and visual regressions.",
        "",
        "## Failed structural checks",
    ]
    for s in qa.structural:
        if not s.ok:
            lines.append(f"- {s.step}: {s.detail}")
    lines.append("")
    lines.append("## Failed flows")
    for f in qa.flows:
        if not f.ok:
            lines.append(f"- Flow `{f.flow_id}`: {f.error or 'step failure'}")
            for st in f.steps:
                if not st.ok:
                    lines.append(f"    - step {st.step}: {st.detail}")
    lines.append("")
    lines.append("## Visual / pixel failures")
    for v in qa.visual:
        if not v.ok:
            lines.append(f"- {v.name}: {v.detail} (screenshot={v.screenshot_path})")
    if qa.errors:
        lines.append("")
        lines.append("## Runner errors")
        for e in qa.errors:
            lines.append(f"- {e}")
    lines.append("")
    lines.append("## Required actions")
    lines.append("1. Ensure routes exist for pages under test (/, /login, /dashboard as applicable).")
    lines.append("2. Match selectors used in qa/ui_spec.json (or update the spec only if the product requirement changed).")
    lines.append("3. Fix layout/CSS so screenshots stay within pixel diff threshold vs baselines.")
    lines.append("4. Keep loading/empty/error states; do not remove accessibility attributes.")
    lines.append("5. Re-run is external — just fix the code.")
    brief = "\n".join(lines)
    path = Path(project_dir) / "QA_REPAIR_BRIEF.md"
    path.write_text(brief, encoding="utf-8")
    return brief


def _repair_with_full_agent(project_dir: Path, brief: str, api_key: str, max_turns: int = 25) -> str:
    """Drive full Neon agent to apply QA repair brief."""
    try:
        from sdlc_wrapper_full import FullAgentSDLCWrapper
        from sdlc_wrapper import Goal, Criterion
    except Exception as e:
        return f"full agent unavailable: {e}"

    goal = Goal(
        description=(
            "Fix UI so browser QA passes. Follow QA_REPAIR_BRIEF.md strictly. "
            + brief[:3000]
        ),
        notes="Surgical UI/UX and route fixes only. Preserve working backend.",
        criteria=[
            Criterion("repair_brief", "Repair brief exists", require_path="QA_REPAIR_BRIEF.md", soft=True),
        ],
    )
    wrapper = FullAgentSDLCWrapper(
        project_dir=Path(project_dir),
        api_key=api_key or None,
    )
    # Single outer round focused on repair
    result = wrapper.run(goal, max_outer_rounds=1, max_inner_turns=max_turns, force_restart_first=False)
    return f"full_agent repair success={result.success} stop={result.stop_reason}"


def _repair_with_generation_core(project_dir: Path, brief: str, pool: Any, config: Dict) -> str:
    try:
        from generation_core import GenerationOrchestratorV5
    except Exception as e:
        return f"generation core unavailable: {e}"
    orch = GenerationOrchestratorV5(pool, config)
    result = orch.generate(
        description=(
            "REPAIR existing project. " + brief[:4000]
        ),
        project_dir=Path(project_dir),
        stack=None,
    )
    return f"generation repair success={result.success} errors={result.errors[:3]}"


def run_self_heal_loop(
    spec: UISpec,
    project_dir: Path,
    out_dir: Path,
    max_rounds: int = 5,
    use_full_agent: bool = False,
    api_key: str = "",
    pool: Any = None,
    config: Optional[Dict] = None,
    headless: bool = True,
    update_baselines_on_first_pass: bool = True,
) -> HealResult:
    """
    Closed loop:
      QA → (fail) repair brief → agent fix → QA → ...
    """
    project_dir = Path(project_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    baseline_dir = out_dir / "baselines"

    result = HealResult(success=False)
    if not HAS_PLAYWRIGHT:
        result.stop_reason = "playwright_not_installed"
        return result

    for rnd in range(1, max_rounds + 1):
        t0 = time.monotonic()
        print(f"[heal] round {rnd}/{max_rounds} — running QA…")
        qa = run_qa_suite(
            spec,
            out_dir=out_dir / f"round_{rnd}",
            baseline_dir=baseline_dir,
            headless=headless,
            update_baselines=(update_baselines_on_first_pass and rnd == 1 and not any(baseline_dir.glob("*.png"))),
        )
        hr = HealRound(
            round_num=rnd,
            qa_ok=qa.ok,
            repair_attempted=False,
            detail="pass" if qa.ok else "fail",
            report_path=qa.report_path,
            duration_sec=time.monotonic() - t0,
        )

        if qa.ok:
            hr.detail = "QA pass"
            result.rounds.append(hr)
            result.success = True
            result.final_qa = qa
            result.stop_reason = "qa_passed"
            print("[heal] QA passed")
            break

        # Build repair brief
        brief = build_repair_brief(qa, project_dir)
        result.repair_brief_path = str(project_dir / "QA_REPAIR_BRIEF.md")
        print(f"[heal] QA failed — repair brief → {result.repair_brief_path}")

        # Repair
        hr.repair_attempted = True
        if use_full_agent:
            detail = _repair_with_full_agent(project_dir, brief, api_key=api_key)
        elif pool is not None:
            detail = _repair_with_generation_core(project_dir, brief, pool, config or {})
        else:
            detail = (
                "No repair engine configured. Wrote QA_REPAIR_BRIEF.md — "
                "run full agent with this brief as /goal, then re-run heal loop."
            )
            hr.detail = detail
            result.rounds.append(hr)
            result.final_qa = qa
            result.stop_reason = "repair_engine_missing"
            break

        hr.detail = detail
        result.rounds.append(hr)
        result.final_qa = qa
        print(f"[heal] repair: {detail[:200]}")
        # brief pause for servers to reload if HMR
        time.sleep(2.0)
    else:
        result.stop_reason = "max_rounds_reached"

    # Report
    report = out_dir / "SELF_HEAL_REPORT.md"
    lines = [
        "# QA Self-Heal Report",
        "",
        f"- Success: **{result.success}**",
        f"- Stop: `{result.stop_reason}`",
        f"- Rounds: {len(result.rounds)}",
        f"- Repair brief: `{result.repair_brief_path}`",
        "",
        "## Rounds",
        "",
    ]
    for r in result.rounds:
        lines.append(
            f"### Round {r.round_num} — QA {'PASS' if r.qa_ok else 'FAIL'} — "
            f"repair={r.repair_attempted}"
        )
        lines.append(f"- {r.detail}")
        lines.append(f"- report: {r.report_path}")
        lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"[heal] report → {report}")
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="QA self-healing loop")
    parser.add_argument("--base-url", default="http://127.0.0.1:5173")
    parser.add_argument("--project", default=".")
    parser.add_argument("--out", default="./qa_heal_out")
    parser.add_argument("--max-rounds", type=int, default=5)
    parser.add_argument("--use-full-agent", action="store_true")
    parser.add_argument("--api-key", default=os.getenv("NIM_API_KEY") or "")
    parser.add_argument("--preset", choices=["default", "oiioii"], default="oiioii")
    parser.add_argument("--spec", default="", help="Path to ui_spec.json")
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    if args.spec:
        raw = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        from qa_browser import Flow, Step, VisualPage
        flows = [
            Flow(id=f["id"], description=f.get("description", ""), steps=[Step(**s) for s in f.get("steps", [])])
            for f in raw.get("flows", [])
        ]
        visuals = [VisualPage(**v) for v in raw.get("visual_pages", [])]
        vp = raw.get("viewport", [1280, 720])
        spec = UISpec(
            base_url=raw.get("base_url", args.base_url),
            flows=flows,
            visual_pages=visuals,
            must_have_selectors=raw.get("must_have_selectors", ["body"]),
            must_have_text=raw.get("must_have_text", []),
            viewport=(vp[0], vp[1]),
        )
    elif args.preset == "oiioii":
        spec = oiioii_workspace_spec(args.base_url)
    else:
        spec = default_web_app_spec(args.base_url)

    result = run_self_heal_loop(
        spec=spec,
        project_dir=Path(args.project),
        out_dir=Path(args.out),
        max_rounds=args.max_rounds,
        use_full_agent=args.use_full_agent,
        api_key=args.api_key,
        headless=not args.headed,
    )
    raise SystemExit(0 if result.success else 1)


if __name__ == "__main__":
    main()
