#!/usr/bin/env python
from __future__ import annotations
import pathlib

try:
    import tomllib as tomli  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli  # type: ignore[no-redef]

P = pathlib.Path("pyproject.toml")
data = tomli.loads(P.read_text(encoding="utf-8"))
version = data.get("project", {}).get("version")
assert version, "project.version missing in pyproject.toml"
print(version, end="")
