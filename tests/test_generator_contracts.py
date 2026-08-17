"""Offline production contracts for Neon Architect's deterministic core.

The large parameter matrix is intentionally behavior-based: it verifies every
documented detection keyword across natural prefixes/suffixes and casing, rather
than padding the suite with empty assertions.  It provides broad regression
coverage without using an NIM key or making network requests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import generation_core as gc
from neon_architect import TodoTool


PREFIXES = (
    "Build a ", "Create a secure ", "Ship an accessible ", "Design a useful ",
    "Implement a production-ready ", "Generate a clean ", "Make a small ",
    "I need a reliable ", "Please create a ", "Develop a polished ",
    "Prototype a maintainable ", "Launch a multilingual ", "Write a tested ",
    "Construct a privacy-aware ", "Deliver a responsive ", "Build an offline-first ",
    "Create an internationalized ", "Implement a collaborative ", "Make a fast ",
    "Produce a documented ",
)
SUFFIXES = (
    " for a habit tracker", " with authentication", " with a searchable dashboard",
    " that handles Unicode names", " for teams", " with audit history",
    " and clear validation", " with a resilient API", " for a small business",
    " with empty states", " that is deterministic", " with integration tests",
)
STACK_KEYWORDS = {
    "flutter-fastapi": "flutter mobile application",
    "expo-node": "expo react native mobile application",
    "nextjs-postgres": "next.js app router application",
    "fastapi-react": "web SaaS dashboard",
}


def _stack_cases() -> list[Any]:
    cases: list[Any] = []
    for expected, keyword in STACK_KEYWORDS.items():
        for index, (prefix, suffix) in enumerate(
            (pair for pair in ((p, s) for p in PREFIXES for s in SUFFIXES))
        ):
            description = f"{prefix}{keyword}{suffix}"
            marks = (pytest.mark.smoke,) if index < 12 else ()
            cases.append(pytest.param(description, expected, id=f"{expected}-{index:03d}", marks=marks))
    return cases


@pytest.mark.parametrize(("description", "expected"), _stack_cases())
def test_stack_detection_matrix(description: str, expected: str) -> None:
    """All supported-stack prompts resolve to their explicit contract."""
    assert gc.detect_stack(description) == expected


ENTITY_CASES = {
    "habit": ("habit", "Habit"), "task": ("task", "Task"),
    "note": ("note", "Note"), "recipe": ("recipe", "Recipe"),
    "expense": ("expense", "Expense"), "workout": ("workout", "Workout"),
    "book": ("book", "Book"), "event": ("event", "Event"),
    "product": ("product", "Product"), "order": ("order", "Order"),
    "ticket": ("ticket", "Ticket"), "article": ("post", "Post"),
    "project": ("project", "Project"),
}
ENTITY_CONTEXTS = (
    "tracker", "manager", "dashboard", "platform", "with auth", "with analytics",
    "for teams", "for Unicode users", "with empty states", "with exports",
)


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        pytest.param(f"{keyword} {context}", expected, id=f"{keyword}-{n}")
        for keyword, expected in ENTITY_CASES.items()
        for n, context in enumerate(ENTITY_CONTEXTS)
    ],
)
def test_primary_entity_matrix(description: str, expected: tuple[str, str]) -> None:
    assert gc.derive_primary_entity(description) == expected


@pytest.mark.parametrize("stack", gc.SUPPORTED_STACKS)
@pytest.mark.smoke
def test_stack_surface_contract_has_domain_and_entity_endpoint(stack: str) -> None:
    surface = gc.stack_surface(stack, "Build a habit tracker with Unicode names")
    assert surface["entity_slug"] == "habit"
    assert surface["entity_pascal"] == "Habit"
    assert "habit" in surface["endpoints"]
    assert surface["domain"][-1] == "habit"
    assert surface["frontend_entities"][0] == "Habit"


@pytest.mark.parametrize("stack", gc.SUPPORTED_STACKS)
@pytest.mark.smoke
def test_scaffold_manifest_contracts_and_required_files(tmp_path: Path, stack: str) -> None:
    project = tmp_path / f"{stack}-unicode-\u043f\u0440\u043e\u0435\u043a\u0442"
    created = gc.scaffold(stack, project, {"project_name": project.name})
    assert created and (project / "README.md").is_file()
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in project.rglob("*") if p.is_file())
    assert "TODO:" not in all_text and "FIXME:" not in all_text
    if stack == "flutter-fastapi":
        pubspec = (project / "pubspec.yaml").read_text(encoding="utf-8")
        assert "name:" in pubspec and "sdk:" in pubspec and (project / "backend/main.py").is_file()
    elif stack == "fastapi-react":
        package = json.loads((project / "frontend/package.json").read_text(encoding="utf-8"))
        assert package["private"] is True and "dev" in package["scripts"]
        assert (project / "backend/requirements.txt").read_text(encoding="utf-8").strip()
    elif stack == "nextjs-postgres":
        package = json.loads((project / "package.json").read_text(encoding="utf-8"))
        assert package["dependencies"]["next"] and (project / "app/page.tsx").is_file()
    else:
        package = json.loads((project / "package.json").read_text(encoding="utf-8"))
        assert package["main"] == "expo-router/entry" and (project / "server/index.js").is_file()


@pytest.mark.parametrize("stack", gc.SUPPORTED_STACKS)
@pytest.mark.smoke
def test_scaffold_is_idempotent_for_same_input(tmp_path: Path, stack: str) -> None:
    project = tmp_path / stack
    context = {"project_name": "repeatable app"}
    gc.scaffold(stack, project, context)
    first = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest() for p in project.rglob("*") if p.is_file()}
    gc.scaffold(stack, project, context)
    second = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest() for p in project.rglob("*") if p.is_file()}
    assert first == second


@pytest.mark.parametrize(
    ("rel", "content", "expected"),
    [
        ("safe/file.txt", "hello", True), ("../escape.txt", "no", False),
        ("nested/../../escape.txt", "no", False), ("/absolute.txt", "no", False),
        ("C:/escape.txt", "no", False), ("bad.py", "def broken(:", False),
        (None, "no", False), ("valid.txt", None, False),
    ],
)
def test_safe_write_rejects_traversal_and_partial_invalid_writes(
    tmp_path: Path, rel: Any, content: Any, expected: bool
) -> None:
    errors: list[str] = []
    assert gc._safe_write(tmp_path, rel, content, errors) is expected
    if not expected:
        assert errors
        assert not (tmp_path.parent / "escape.txt").exists()


@pytest.mark.parametrize("bad_stack", ["", "unknown", "FastAPI-React", "../flutter-fastapi"])
def test_scaffold_rejects_unknown_stack(tmp_path: Path, bad_stack: str) -> None:
    with pytest.raises(gc.GenerationInputError):
        gc.scaffold(bad_stack, tmp_path, {"project_name": "app"})


@pytest.mark.parametrize("description", [None, "", "  ", "x" * (gc.MAX_DESCRIPTION_CHARS + 1)])
def test_generation_rejects_bad_descriptions_before_any_write(tmp_path: Path, description: Any) -> None:
    orchestrator = gc.GenerationOrchestratorV5(pool=None, config={})
    with pytest.raises(gc.GenerationInputError):
        orchestrator.generate(description, tmp_path / "project")
    assert not (tmp_path / "project").exists()


def test_orchestrator_rejects_invalid_config_type() -> None:
    with pytest.raises(gc.GenerationInputError):
        gc.GenerationOrchestratorV5(pool=None, config="not-a-dict")


@pytest.mark.smoke
def test_todo_instances_are_isolated_and_counters_start_independently(tmp_path: Path) -> None:
    first, second = TodoTool(tmp_path / "one"), TodoTool(tmp_path / "two")
    assert first.execute(action="add", content="first board").text().startswith("Added todo T001")
    assert second.execute(action="list").text() == "No todos"
    assert second.execute(action="add", content="second board").text().startswith("Added todo T001")
    first.execute(action="clear")
    assert second.execute(action="list").text() != "No todos"


@pytest.mark.parametrize("status", ["pending", "in_progress", "done"])
def test_todo_accepts_only_documented_statuses(tmp_path: Path, status: str) -> None:
    todo = TodoTool(tmp_path)
    todo.execute(action="add", content="validate status")
    assert not todo.execute(action="update", id="T001", status=status).is_error


@pytest.mark.parametrize("status", ["", "queued", "DONE", "null", "in progress"])
def test_todo_rejects_invalid_statuses(tmp_path: Path, status: str) -> None:
    todo = TodoTool(tmp_path)
    todo.execute(action="add", content="validate status")
    result = todo.execute(action="update", id="T001", status=status)
    assert result.is_error
    assert todo.todos["T001"]["status"] == "pending"


@pytest.mark.smoke
def test_todo_restore_is_instance_local_and_defensive(tmp_path: Path) -> None:
    original, restored, unrelated = TodoTool(tmp_path / "a"), TodoTool(tmp_path / "b"), TodoTool(tmp_path / "c")
    original.execute(action="add", content="persist me")
    restored.restore(dict(original.todos), original.counter)
    assert "persist me" in restored.execute(action="list").text()
    assert not restored.execute(action="update", id="T001", status="done").is_error
    assert original.todos["T001"]["status"] == "pending"
    assert unrelated.execute(action="list").text() == "No todos"


@pytest.mark.parametrize(
    ("todos", "counter"),
    [
        (None, 0),
        ({"": {"content": "x", "status": "pending"}}, 1),
        ({"T001": None}, 1),
        ({"T001": {"content": "", "status": "pending"}}, 1),
        ({"T001": {"content": "x", "status": "queued"}}, 1),
        ({"T001": {"content": "x", "status": "pending"}}, True),
        ({"T001": {"content": "x", "status": "pending"}}, "not-a-number"),
    ],
)
def test_todo_restore_rejects_malformed_persisted_state(tmp_path: Path, todos: Any, counter: Any) -> None:
    todo = TodoTool(tmp_path)
    todo.execute(action="add", content="existing item")
    with pytest.raises(ValueError):
        todo.restore(todos, counter)
    assert todo.todos == {"T001": {"content": "existing item", "status": "pending"}}


@pytest.mark.parametrize("invalid", [0, [], {}, b"flutter", object()])
def test_stack_contract_public_functions_reject_non_text_input(invalid: Any) -> None:
    with pytest.raises(gc.GenerationInputError):
        gc.detect_stack(invalid)
    with pytest.raises(gc.GenerationInputError):
        gc.derive_primary_entity(invalid)


@pytest.mark.parametrize("invalid_stack", [None, "", "unknown", "../flutter-fastapi", 1])
def test_stack_surface_rejects_unknown_or_unsafe_stack(invalid_stack: Any) -> None:
    with pytest.raises(gc.GenerationInputError):
        gc.stack_surface(invalid_stack, "Build a habit tracker")


def test_stack_surface_returns_independent_contract_collections() -> None:
    first = gc.stack_surface("flutter-fastapi", "Build a habit tracker")
    first["domain"].append("unexpected")
    first["frontend_entities"].append("Unexpected")
    second = gc.stack_surface("flutter-fastapi", "Build a habit tracker")
    assert second["domain"] == ["health", "auth", "habit"]
    assert second["frontend_entities"] == ["Habit", "User"]


@pytest.mark.parametrize("project_name", ["", "   ", "a\nnewline", "x" * (gc.MAX_PROJECT_NAME_CHARS + 1), None])
def test_scaffold_rejects_invalid_or_control_character_project_names(tmp_path: Path, project_name: Any) -> None:
    with pytest.raises(gc.GenerationInputError):
        gc.scaffold("flutter-fastapi", tmp_path / "project", {"project_name": project_name})


@pytest.mark.parametrize("stack", ["fastapi-react", "flutter-fastapi", "nextjs-postgres"])
def test_scaffold_serializes_adversarial_project_name_without_corrupting_sources(
    tmp_path: Path, stack: str
) -> None:
    project = tmp_path / stack
    name = 'Unicode <App> "quoted" проект'
    gc.scaffold(stack, project, {"project_name": name})
    if stack in {"fastapi-react", "flutter-fastapi"}:
        ast_source = (project / "backend/main.py").read_text(encoding="utf-8")
        compile(ast_source, "backend/main.py", "exec")
        assert f"title={json.dumps(name, ensure_ascii=False)}" in ast_source
    if stack == "fastapi-react":
        html = (project / "frontend/index.html").read_text(encoding="utf-8")
        assert "&lt;App&gt;" in html and "&quot;quoted&quot;" in html
    elif stack == "flutter-fastapi":
        description = next(
            line for line in (project / "pubspec.yaml").read_text(encoding="utf-8").splitlines()
            if line.startswith("description: ")
        )
        assert json.loads(description.removeprefix("description: ")) == name
    else:
        layout = (project / "app/layout.tsx").read_text(encoding="utf-8")
        assert f"title: {json.dumps(name, ensure_ascii=False)}" in layout


def test_safe_write_preserves_destination_and_cleans_temporary_file_when_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "safe.txt"
    target.write_text("known-good", encoding="utf-8")

    def fail_replace(self: Path, target_path: Path) -> Path:
        raise OSError("simulated replace failure")

    monkeypatch.setattr(Path, "replace", fail_replace)
    errors: list[str] = []
    assert not gc._safe_write(tmp_path, "safe.txt", "new content", errors)
    assert errors == ["write failed safe.txt: simulated replace failure"]
    assert target.read_text(encoding="utf-8") == "known-good"
    assert not list(tmp_path.glob(".safe.txt.*.tmp"))


def test_generate_rejects_existing_file_as_project_directory(tmp_path: Path) -> None:
    blocked_path = tmp_path / "not-a-directory"
    blocked_path.write_text("not a project", encoding="utf-8")
    orchestrator = gc.GenerationOrchestratorV5(pool=None, config={})
    with pytest.raises(gc.GenerationInputError, match="directory"):
        orchestrator.generate("Build a habit tracker", blocked_path)


def test_import_consistency_finds_and_repair_scaffolds_package_inits(tmp_path: Path) -> None:
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "main.py").write_text("from backend.services.billing import BillingService\n", encoding="utf-8")
    orchestrator = gc.GenerationOrchestratorV5(pool=None, config={})
    problems = orchestrator._import_consistency(tmp_path, ["backend/main.py"])
    assert problems == ["backend/main.py: imports 'backend.services.billing' but module not generated"]
    result = gc.GenerationResult(False, tmp_path, "fastapi-react")
    assert orchestrator._repair_imports({}, tmp_path, [], result) == 1
    assert (backend / "__init__.py").is_file()
