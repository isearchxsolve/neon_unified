import re
with open(r"D:\neon_unified\sdlc_wrapper_full.py", "r", encoding="utf-8") as f:
    content = f.read()

old = """def _load_neon():
    \"\"\"Import NeonArchitect from neon_architect_v5.py in the same directory.\"\"\"
    here = Path(__file__).resolve().parent
    candidates = [
        here / "neon_architect_v5.py",
        here / "neon_architect.py",
        Path("/home/workdir/artifacts/neon_v5/neon_architect_v5.py"),
    ]
    import importlib.util
    for path in candidates:
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location("neon_architect_v5", path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
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
    )"""

new = """def _load_neon():
    \"\"\"Import NeonArchitect from neon_architect_v5.py in the same directory.\"\"\"
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
    )"""

content = content.replace(old, new)
with open(r"D:\neon_unified\sdlc_wrapper_full.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
