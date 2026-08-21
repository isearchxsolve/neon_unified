"""GAP-NU-7: monolith size freeze.

neon_architect.py / neon_architect_v5.py are 640KB+ single files. They must
not grow further; new code goes into new modules (see
docs/MONOLITH_EXTRACTION_PLAN.md). This test enforces the freeze.
"""
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
MAX_MONOLITH_BYTES = 660_000


@pytest.mark.parametrize("name", ["neon_architect.py", "neon_architect_v5.py"])
def test_monolith_does_not_grow(name):
    path = _ROOT / name
    if not path.exists():
        pytest.skip(f"{name} removed (extraction complete)")
    size = path.stat().st_size
    assert size <= MAX_MONOLITH_BYTES, (
        f"{name} grew to {size} bytes (freeze limit {MAX_MONOLITH_BYTES}). "
        "Put new code in a new module — see docs/MONOLITH_EXTRACTION_PLAN.md."
    )
