"""GAP-NU-3 / GAP-NU-4 regression: test isolation modes + all-stack runners.

Docker mode must be hardened (no network, read-only root, cpu/mem caps).
Forced docker with no daemon/CLI must fail closed (ran=False, BLOCKED).
expo-node gets a jest runner; missing toolchains are loud, never silent passes.
"""
import subprocess
import types

import generation_core as gc


class _Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _orch(config):
    return gc.GenerationOrchestratorV5(pool=None, config=config)


def _project_with_tests(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_ok():\n    assert True\n")
    return tmp_path


def test_unknown_isolation_mode_fails_closed(tmp_path):
    res = _orch({"exec_isolation": "warp-drive"})._run_tests(
        _project_with_tests(tmp_path), "fastapi-react")
    assert res.ran is False and "unknown exec_isolation" in res.output


def test_forced_docker_without_cli_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: None)
    res = _orch({"exec_isolation": "docker"})._run_tests(
        _project_with_tests(tmp_path), "fastapi-react")
    assert res.ran is False and "BLOCKED" in res.output


def test_forced_docker_with_dead_daemon_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: "/usr/bin/docker")

    def fake_run(cmd, **kw):
        if cmd[1] == "info":
            return _Proc(returncode=1, stderr="cannot connect")
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({"exec_isolation": "docker"})._run_tests(
        _project_with_tests(tmp_path), "fastapi-react")
    assert res.ran is False and "daemon is not" in res.output


def test_docker_mode_uses_hardened_flags(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: "/usr/bin/docker")
    seen = {}

    def fake_run(cmd, **kw):
        if cmd[1] == "info":
            return _Proc(returncode=0)
        seen["cmd"] = cmd
        return _Proc(returncode=0, stdout="1 passed")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({"exec_isolation": "docker"})._run_tests(
        _project_with_tests(tmp_path), "fastapi-react")
    cmd = seen["cmd"]
    assert res.ran and res.passed
    for flag in ("--network", "--read-only", "--cpus", "--memory", "--tmpfs"):
        assert flag in cmd, f"missing hardening flag {flag}"
    assert cmd[cmd.index("--network") + 1] == "none"
    assert "python:3.11-slim" in cmd


def test_auto_falls_back_to_host_when_daemon_down(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: "/usr/bin/docker")
    seen = {}

    def fake_run(cmd, **kw):
        if cmd[0] == "/usr/bin/docker" and cmd[1] == "info":
            return _Proc(returncode=1)
        seen["cmd"] = cmd
        return _Proc(returncode=0, stdout="1 passed")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({})._run_tests(_project_with_tests(tmp_path), "fastapi-react")
    assert res.ran and res.passed
    assert seen["cmd"][:3] == ["python", "-m", "pytest"]


def test_expo_node_requires_package_json(tmp_path):
    res = _orch({"exec_isolation": "host"})._run_tests(tmp_path, "expo-node")
    assert res.ran is False and "package.json" in res.output


def test_expo_node_runs_jest(tmp_path, monkeypatch):
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    seen = {}

    def fake_run(cmd, **kw):
        seen["cmd"] = cmd
        return _Proc(returncode=0, stdout="no tests, passed")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({"exec_isolation": "host"})._run_tests(tmp_path, "expo-node")
    assert res.ran and res.passed
    assert "jest" in seen["cmd"]


def test_flutter_stack_without_sdk_still_runs_python_half(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: None)

    def fake_run(cmd, **kw):
        return _Proc(returncode=0, stdout="1 passed")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({"exec_isolation": "host"})._run_tests(
        _project_with_tests(tmp_path), "flutter-fastapi")
    assert res.ran and res.passed


def test_flutter_stack_dart_analyze_failure_fails_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(gc.shutil, "which", lambda name: "/usr/bin/dart")

    def fake_run(cmd, **kw):
        if cmd[0] == "/usr/bin/dart":
            return _Proc(returncode=1, stdout="error: undefined name")
        return _Proc(returncode=0, stdout="1 passed")

    monkeypatch.setattr(gc.subprocess, "run", fake_run)
    res = _orch({"exec_isolation": "host"})._run_tests(
        _project_with_tests(tmp_path), "flutter-fastapi")
    assert res.ran and res.passed is False and "dart analyze failed" in res.output


def test_nextjs_postgres_is_loud_blocked(tmp_path):
    res = _orch({})._run_tests(tmp_path, "nextjs-postgres")
    assert res.ran is False and "BLOCKED" in res.output
