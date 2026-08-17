#!/usr/bin/env python3
"""
SDLC Wrapper (Full Neon Agent)
==============================

Outer iteration loop that drives the **full Neon Architect agent**
(not only GenerationOrchestratorV5).

Each outer round:
  1. Evaluate acceptance criteria on the project
  2. If all hard criteria pass -> success
  3. Else set/update goal with open failures, enable autopilot, run agent turns
  4. Repeat until success or max outer rounds

This gets closer to complex products (e.g. oiioii-style platforms) because the
full agent can read/edit code, run tests, use tools, and continue SDLC phases.

Usage:
    export NIM_API_KEY=...
    python sdlc_wrapper_full.py --project ./oiioii_clone --preset oiioii --max-outer 5 --max-inner 40

Library:
    from sdlc_wrapper_full import FullAgentSDLCWrapper, goal_oiioii_shell
    w = FullAgentSDLCWrapper(project_dir=Path("./app"), api_key="...")
    result = w.run(goal_oiioii_shell(), max_outer_rounds=5, max_inner_turns=40)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

# == Reuse criterion model from lightweight wrapper when available ============

try:
    from sdlc_wrapper import (
        Criterion,
        Goal,
        CriterionResult,
        Evaluator,
        CycleMemory,
        goal_oiioii_shell,
    )
except ImportError:
    try:
        import importlib.util
        _sw = Path(__file__).resolve().parent / "sdlc_wrapper.py"
        _spec = importlib.util.spec_from_file_location("sdlc_wrapper", _sw)
        _mod = importlib.util.module_from_spec(_spec)
        assert _spec.loader is not None
        _spec.loader.exec_module(_mod)
        Criterion = _mod.Criterion
        Goal = _mod.Goal
        CriterionResult = _mod.CriterionResult
        Evaluator = _mod.Evaluator
        CycleMemory = _mod.CycleMemory
        goal_oiioii_shell = _mod.goal_oiioii_shell
    except Exception as e:
        raise SystemExit(f"Need sdlc_wrapper.py next to this file: {e}")


# == Load full Neon Architect =================================================

def _load_neon():
    """Import NeonArchitect from neon_architect_v5.py in the same directory."""
    here = Path(__file__).resolve().parent
    candidates = [
        (here / "neon_architect_v5.py", "neon_architect_v5"),
        (here / "neon_architect.py", "neon_architect"),
        (Path("/home/workdir/artifacts/neon_v5/neon_architect_v5.py"), "neon_architect_v5"),
    ]
    import importlib.util
    for path, modname in candidates:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[modname] = mod
        # Ensure sibling generation_core is importable
        sys.path.insert(0, str(path.parent))
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"Warning: failed loading {path.name}: {e}")
            continue
        if hasattr(mod, "NeonArchitect"):
            return mod
    raise ImportError(
        "Could not load NeonArchitect. Place neon_architect_v5.py next to this file."
    )


# =============================================================================
# Result types
# =============================================================================

@dataclass
class OuterRoundResult:
    round_num: int
    action: str
    success: bool
    criteria: List[CriterionResult] = field(default_factory=list)
    agent_turns: int = 0
    notes: str = ""
    duration_sec: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class FullWrapperResult:
    success: bool
    goal: Goal
    project_dir: Path
    rounds: List[OuterRoundResult] = field(default_factory=list)
    final_criteria: List[CriterionResult] = field(default_factory=list)
    stop_reason: str = ""
    total_duration_sec: float = 0.0


ProgressCb = Optional[Callable[[str, str], None]]


# =============================================================================
# Full-agent SDLC wrapper
# =============================================================================

class FullAgentSDLCWrapper:
    """
    Drives the full NeonArchitect agent in outer evaluation/repair cycles.

    Strategy:
    - Outer loop owns acceptance criteria and stop conditions
    - Inner loop runs the real agent (goal + autopilot + run_turn)
    - Between outer rounds, failures are injected into the goal/prompt
      so the agent focuses on what is still broken
    """

    def __init__(
        self,
        project_dir: Path,
        api_key: Optional[str] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
        on_progress: ProgressCb = None,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = (
            api_key
            or os.getenv("NIM_API_KEY")
            or os.getenv("NVIDIA_API_KEY")
            or os.getenv("NGC_API_KEY")
            or ""
        )
        self.config_overrides = config_overrides or {}
        self.on_progress = on_progress
        self.evaluator = Evaluator(self.project_dir)
        self.memory_path = self.project_dir / ".neon_full_sdlc_memory.json"
        self.history_path = self.project_dir / ".neon_full_sdlc_history.jsonl"
        self._neon_mod = None
        self.agent = None

    def _log(self, phase: str, msg: str) -> None:
        if self.on_progress:
            self.on_progress(phase, msg)
        else:
            print(f"[{phase}] {msg}")

    def _append_history(self, payload: Dict[str, Any]) -> None:
        try:
            with open(self.history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, default=str) + "\n")
        except Exception:
            pass

    def _build_agent(self):
        if self.agent is not None:
            return self.agent

        mod = _load_neon()
        self._neon_mod = mod

        # Start from DEFAULT_CONFIG when available
        cfg = {}
        if hasattr(mod, "DEFAULT_CONFIG"):
            cfg = dict(mod.DEFAULT_CONFIG)
        cfg["project_dir"] = str(self.project_dir)
        if self.api_key:
            cfg["api_key"] = self.api_key
        # Outer wrapper controls length; keep inner autopilot bounded per outer round
        cfg["max_autopilot_rounds"] = int(
            self.config_overrides.get("max_autopilot_rounds", cfg.get("max_autopilot_rounds") or 30)
        )
        cfg["max_rounds"] = int(self.config_overrides.get("max_rounds", cfg.get("max_rounds") or 0) or 0)
        cfg.update(self.config_overrides)

        # Persist API key into project key file if the agent supports it
        try:
            if hasattr(mod, "save_project_api_key") and self.api_key:
                mod.save_project_api_key(self.project_dir, self.api_key)
        except Exception:
            pass

        agent = mod.NeonArchitect(cfg)
        # Ensure project_dir is correct even if constructor copied config
        try:
            agent.project_dir = self.project_dir
        except Exception:
            pass
        self.agent = agent
        return agent

    def _compose_goal_text(self, goal: Goal, memory: CycleMemory, failures: List[CriterionResult]) -> str:
        parts = [goal.description.strip()]
        if goal.notes:
            parts.append(goal.notes.strip())
        parts.append("Acceptance criteria (must eventually all pass):")
        for c in goal.criteria:
            parts.append(f"- [{c.id}] {c.description}")
        if failures:
            parts.append("CURRENT HARD FAILURES -- prioritize fixing these:")
            for f in failures:
                parts.append(f"- [{f.id}] {f.detail}")
        if memory.open_failures and not failures:
            parts.append("Previously open failures:")
            for x in memory.open_failures[:8]:
                parts.append(f"- {x}")
        parts.append(
            "Work in the project directory. Prefer editing existing code over rewriting everything. "
            "Use tools. Run tests. Do not claim completion until criteria are actually satisfied."
        )
        return "\n".join(parts)

    def _run_agent_inner(
        self,
        goal_text: str,
        max_inner_turns: int,
        restart_autopilot: bool,
    ) -> Dict[str, Any]:
        """
        Set goal, start autopilot, run up to max_inner_turns agent turns.
        Returns stats dict.
        """
        agent = self._build_agent()
        errors: List[str] = []
        turns = 0

        try:
            # Set goal through public API when possible
            if hasattr(agent, "cmd_goal"):
                agent.cmd_goal(goal_text)
            else:
                agent.goal = goal_text

            # Raise inner autopilot budget for this outer round
            try:
                agent.max_autopilot_rounds = max(max_inner_turns, int(getattr(agent, "max_autopilot_rounds", 0) or 0))
                agent.config["max_autopilot_rounds"] = agent.max_autopilot_rounds
            except Exception:
                pass

            started = False
            if hasattr(agent, "cmd_autopilot"):
                try:
                    agent.cmd_autopilot(restart=restart_autopilot)
                    started = True
                except TypeError:
                    # Some versions may not take restart kw
                    agent.cmd_autopilot()
                    started = True
            elif hasattr(agent, "_start_autopilot"):
                agent._start_autopilot(restart=restart_autopilot)
                started = True
            else:
                agent.autopilot = True
                started = True

            if not started:
                errors.append("could not start autopilot")

            # Drive turns. Empty input continues autopilot.
            for i in range(max_inner_turns):
                turns += 1
                self._log("agent", f"inner turn {i + 1}/{max_inner_turns}")
                try:
                    # If autopilot stopped, nudge with a continuation prompt
                    if not getattr(agent, "autopilot", False):
                        agent.run_turn(
                            "Continue toward the goal. Fix remaining gaps, run tests, "
                            "and implement missing acceptance criteria. Use tools."
                        )
                        # try re-enable
                        if hasattr(agent, "_start_autopilot"):
                            try:
                                agent._start_autopilot(restart=False)
                            except Exception:
                                agent.autopilot = True
                    else:
                        agent.run_turn("")  # continue autopilot
                except KeyboardInterrupt:
                    errors.append("interrupted by user")
                    break
                except Exception as e:
                    errors.append(f"turn error: {e}")
                    self._log("agent", f"turn error: {e}")
                    # brief backoff then continue
                    time.sleep(1.0)

                # Early exit if agent thinks SDLC is complete and we can re-evaluate outside
                try:
                    phases = getattr(self._neon_mod, "SDLC_PHASES", []) if self._neon_mod else []
                    idx = int(getattr(agent, "sdlc_phase_idx", 0))
                    if phases and idx >= len(phases) and not getattr(agent, "autopilot", False):
                        self._log("agent", "agent reported SDLC complete")
                        break
                except Exception:
                    pass

            # Stop autopilot cleanly
            try:
                if hasattr(agent, "_stop_autopilot"):
                    agent._stop_autopilot()
                else:
                    agent.autopilot = False
            except Exception:
                pass

            try:
                if hasattr(agent, "persist"):
                    agent.persist(force=True)
            except Exception:
                pass

        except Exception as e:
            errors.append(f"agent session error: {e}")
            errors.append(traceback.format_exc()[-600:])

        return {"turns": turns, "errors": errors}

    def run(
        self,
        goal: Goal,
        max_outer_rounds: int = 5,
        max_inner_turns: int = 40,
        force_restart_first: bool = True,
    ) -> FullWrapperResult:
        t0 = time.monotonic()
        goal.ensure_minimum_criteria()
        memory = CycleMemory.load(self.memory_path, goal.description)
        memory.goal_description = goal.description

        result = FullWrapperResult(
            success=False,
            goal=goal,
            project_dir=self.project_dir,
        )

        self._log("wrapper", f"FULL Neon agent SDLC wrapper")
        self._log("wrapper", f"Goal: {goal.description[:140]}")
        self._log("wrapper", f"Project: {self.project_dir}")
        self._log("wrapper", f"Outer rounds={max_outer_rounds} | Inner turns/round={max_inner_turns}")

        for outer in range(1, max_outer_rounds + 1):
            rt0 = time.monotonic()
            self._log("wrapper", f"======== OUTER ROUND {outer}/{max_outer_rounds} ========")

            # 1) Evaluate
            criteria_results = self.evaluator.evaluate(goal.criteria)
            hard_fails = Evaluator.hard_failures(criteria_results)
            self._log("evaluate", f"hard failures: {len(hard_fails)}")
            self._log("evaluate", Evaluator.summary(criteria_results))

            if not hard_fails:
                # Confirm project is not empty
                if any(self.project_dir.rglob("*.py")) or any(self.project_dir.rglob("*.tsx")):
                    rr = OuterRoundResult(
                        round_num=outer,
                        action="evaluate_only",
                        success=True,
                        criteria=criteria_results,
                        notes="All hard criteria satisfied",
                        duration_sec=time.monotonic() - rt0,
                    )
                    result.rounds.append(rr)
                    result.final_criteria = criteria_results
                    result.success = True
                    result.stop_reason = "all_hard_criteria_passed"
                    memory.completed_criteria = [r.id for r in criteria_results if r.passed]
                    memory.open_failures = []
                    memory.rounds_completed = outer
                    memory.save(self.memory_path)
                    break

            # 2) Drive full agent
            goal_text = self._compose_goal_text(goal, memory, hard_fails)
            restart = force_restart_first and outer == 1
            self._log("agent", "Starting full Neon agent inner loop…")
            inner = self._run_agent_inner(
                goal_text=goal_text,
                max_inner_turns=max_inner_turns,
                restart_autopilot=restart,
            )

            # 3) Re-evaluate
            criteria_results = self.evaluator.evaluate(goal.criteria)
            hard_fails = Evaluator.hard_failures(criteria_results)

            rr = OuterRoundResult(
                round_num=outer,
                action="full_agent",
                success=len(hard_fails) == 0,
                criteria=criteria_results,
                agent_turns=int(inner.get("turns") or 0),
                notes="full NeonArchitect session",
                duration_sec=time.monotonic() - rt0,
                errors=list(inner.get("errors") or []),
            )
            result.rounds.append(rr)
            result.final_criteria = criteria_results

            memory.rounds_completed = outer
            memory.completed_criteria = [r.id for r in criteria_results if r.passed]
            memory.open_failures = [f"[{r.id}] {r.detail}" for r in hard_fails]
            memory.last_errors = (inner.get("errors") or [])[:8]
            if hard_fails:
                memory.decisions.append(
                    f"Outer {outer}: next focus " + ", ".join(r.id for r in hard_fails[:6])
                )
            memory.save(self.memory_path)
            self._append_history({
                "outer_round": outer,
                "hard_failures": [r.id for r in hard_fails],
                "turns": rr.agent_turns,
                "errors": rr.errors[:5],
            })

            if not hard_fails:
                result.success = True
                result.stop_reason = "all_hard_criteria_passed"
                self._log("wrapper", "[OK] All hard criteria passed")
                break

            self._log("wrapper", f"Outer {outer} done -- {len(hard_fails)} hard failure(s) remain")
        else:
            result.stop_reason = "max_outer_rounds_reached"
            self._log("wrapper", "Max outer rounds reached")

        result.total_duration_sec = time.monotonic() - t0
        result.final_criteria = self.evaluator.evaluate(goal.criteria)
        self._write_report(result)
        return result

    def _write_report(self, result: FullWrapperResult) -> None:
        path = self.project_dir / "FULL_SDLC_WRAPPER_REPORT.md"
        lines = [
            "# Full Neon Agent SDLC Wrapper Report",
            "",
            f"- Success: **{result.success}**",
            f"- Stop reason: `{result.stop_reason}`",
            f"- Outer rounds: {len(result.rounds)}",
            f"- Duration: {result.total_duration_sec:.1f}s",
            f"- Project: `{result.project_dir}`",
            "",
            "## Goal",
            "",
            result.goal.description,
            "",
            "## Final criteria",
            "",
            Evaluator.summary(result.final_criteria),
            "",
            "## Outer rounds",
            "",
        ]
        for r in result.rounds:
            lines.append(
                f"### Outer {r.round_num} -- {r.action} -- "
                f"{'ok' if r.success else 'fail'} -- turns={r.agent_turns}"
            )
            lines.append(f"- Duration: {r.duration_sec:.1f}s")
            if r.errors:
                lines.append(f"- Errors: {r.errors[:3]}")
            lines.append("")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
        except Exception:
            pass


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Full Neon Agent SDLC Iteration Wrapper")
    parser.add_argument("--project", type=str, default="./sdlc_full_out")
    parser.add_argument("--goal", type=str, default="")
    parser.add_argument("--preset", type=str, default="", choices=["", "oiioii"])
    parser.add_argument("--stack", type=str, default="fastapi-react")
    parser.add_argument("--max-outer", type=int, default=5)
    parser.add_argument("--max-inner", type=int, default=40)
    parser.add_argument("--api-key", type=str, default="")
    args = parser.parse_args()

    if args.preset == "oiioii":
        # Engineering-complete oiioii goal (media quality via external APIs)
        try:
            from oiioii_engineering import goal_oiioii_engineering, bootstrap_project
            goal = goal_oiioii_engineering(stack=args.stack)
            boot = bootstrap_project(Path(args.project))
            print(f"Engineering scaffold written: {len(boot.get('created', []))} files")
        except Exception as e:
            print(f"Warning: oiioii_engineering bootstrap failed ({e}); using shell goal")
            goal = goal_oiioii_shell(stack=args.stack)
    elif args.goal:
        goal = Goal(description=args.goal, stack=args.stack)
        goal.ensure_minimum_criteria()
    else:
        print("Provide --goal or --preset oiioii")
        raise SystemExit(2)

    def prog(phase: str, msg: str) -> None:
        print(f"  [{phase}] {msg}")

    wrapper = FullAgentSDLCWrapper(
        project_dir=Path(args.project),
        api_key=args.api_key or None,
        on_progress=prog,
    )
    result = wrapper.run(
        goal,
        max_outer_rounds=args.max_outer,
        max_inner_turns=args.max_inner,
    )

    print("\n======== RESULT ========")
    print(f"Success: {result.success}")
    print(f"Stop:    {result.stop_reason}")
    print(f"Rounds:  {len(result.rounds)}")
    print(f"Report:  {Path(args.project).resolve() / 'FULL_SDLC_WRAPPER_REPORT.md'}")
    print(Evaluator.summary(result.final_criteria))
    raise SystemExit(0 if result.success else 1)


if __name__ == "__main__":
    main()
