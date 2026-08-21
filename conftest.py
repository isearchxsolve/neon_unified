"""Repo-root pytest path fixup.

The generated app under ``oiioii_clone_final`` uses bare absolute imports
(``from src.models import ...``), which only resolve when that clone's own
root is on ``sys.path``. We must NOT add per-clone roots permanently: five
clones each contain a ``backend/`` package, and a bare ``backend`` import
from one clone would silently bind to another clone's package.

Fix: temporarily put ``oiioii_clone_final`` on ``sys.path`` just long enough
to bind ``sys.modules['src']``, then remove it. Submodule imports then
resolve through the package's own ``__path__``.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_FINAL = _ROOT / "oiioii_clone_final"

if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

if "src" not in sys.modules and (_FINAL / "src" / "__init__.py").exists():
    _already = str(_FINAL) in sys.path
    sys.path.insert(0, str(_FINAL))
    try:
        import src  # noqa: F401
    finally:
        if not _already:
            sys.path.remove(str(_FINAL))
