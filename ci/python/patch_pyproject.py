#!/usr/bin/env python
from __future__ import annotations
import pathlib, sys

try:
    import tomllib as tomli  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli  # type: ignore[no-redef]

try:
    import tomli_w
except Exception:
    print("tomli-w not installed. Add it to [tool.uv].dev-dependencies.", file=sys.stderr)
    sys.exit(1)

pv_path = pathlib.Path(".__preview_version__")
if not pv_path.exists():
    sys.exit(".__preview_version__ missing; run `make preview-version` first")

preview_version = pv_path.read_text(encoding="utf-8").strip()

p = pathlib.Path("pyproject.toml")
data = tomli.loads(p.read_text(encoding="utf-8"))
data.setdefault("project", {})["version"] = preview_version
p.write_text(tomli_w.dumps(data), encoding="utf-8")
print(f"Patched pyproject version -> {preview_version}")
