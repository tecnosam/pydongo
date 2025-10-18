#!/usr/bin/env python
from __future__ import annotations
import pathlib, time

try:
    import tomllib as tomli  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli  # type: ignore[no-redef]

P = pathlib.Path("pyproject.toml")
data = tomli.loads(P.read_text(encoding="utf-8"))
base = data.get("project", {}).get("version")
assert base, "project.version missing in pyproject.toml"

ts = time.strftime("%Y%m%d%H%M%S", time.gmtime())
preview = f"{base}.{ts}"
pathlib.Path(".__preview_version__").write_text(preview, encoding="utf-8")
print(preview)
