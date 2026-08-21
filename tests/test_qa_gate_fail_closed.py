"""GAP-NU-2 regression: the browser QA gate must fail CLOSED.

A QA gate that cannot run (missing Playwright, dead preview server, QA
exception) is a failure, never a silent skip. Only two outcomes yield
None (= gate does not apply): non-web stack, or explicit qa_gate='off'.
"""
import builtins
import urllib.request

import generation_core as gc


def test_failed_qa_placeholder_is_never_ok():
    assert gc._FailedQA("anything").ok is False


def test_qa_gate_explicit_off_returns_none():
    orch = gc.GenerationOrchestratorV5(pool=None, config={"qa_gate": "off"})
    assert orch._run_qa_pass({}, None, "fastapi-react", None) is None


def test_qa_gate_not_applicable_for_non_web_stacks():
    orch = gc.GenerationOrchestratorV5(pool=None, config={})
    assert orch._run_qa_pass({}, None, "expo-node", None) is None
    assert orch._run_qa_pass({}, None, "flutter-fastapi", None) is None


def test_qa_gate_fails_closed_when_qa_browser_unavailable(monkeypatch):
    orch = gc.GenerationOrchestratorV5(pool=None, config={})
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "qa_browser":
            raise ImportError("playwright not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    res = orch._run_qa_pass({}, None, "fastapi-react", None)
    assert res is not None and res.ok is False
    assert "qa_gate_unavailable" in res.reason


def test_qa_gate_fails_closed_when_preview_starter_raises():
    def boom(project_dir, stack):
        raise RuntimeError("port in use")

    orch = gc.GenerationOrchestratorV5(
        pool=None, config={"_preview_starter": boom})
    res = orch._run_qa_pass({}, None, "fastapi-react", None)
    assert res is not None and res.ok is False
    assert "preview_server_failed" in res.reason


def test_qa_gate_fails_closed_when_preview_starter_returns_no_url():
    orch = gc.GenerationOrchestratorV5(
        pool=None, config={"_preview_starter": lambda pd, st: None})
    res = orch._run_qa_pass({}, None, "fastapi-react", None)
    assert res is not None and res.ok is False
    assert "preview_server_failed" in res.reason


def test_default_preview_starter_serves_frontend_and_stops(tmp_path):
    fe = tmp_path / "frontend"
    fe.mkdir()
    (fe / "index.html").write_text(
        "<html><body>neon-qa-ok</body></html>", encoding="utf-8")
    url = gc._default_preview_starter(tmp_path, "fastapi-react")
    assert url and url.startswith("http://127.0.0.1:")
    body = urllib.request.urlopen(url, timeout=5).read().decode()
    assert "neon-qa-ok" in body
    gc._stop_preview_servers()
    assert gc._PREVIEW_SERVERS == []


def test_default_preview_starter_none_without_frontend(tmp_path):
    assert gc._default_preview_starter(tmp_path, "fastapi-react") is None
