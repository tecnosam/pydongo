#!/usr/bin/env python
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
from typing import List, Tuple

try:
    import tomllib as tomli  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli  # type: ignore[no-redef]


def run(cmd: List[str], capture=True, check=True, text=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, check=check, text=text)


def parse_version(s: str) -> Tuple[int, int, int]:
    # Ignore any preview suffix (e.g., ".20251018123456")
    core = s.split(".", 3)[:3]
    if len(core) != 3:
        raise ValueError(f"Version '{s}' must be MAJOR.MINOR.PATCH")
    return tuple(int(x) for x in core)  # type: ignore[return-value]


def version_level(base: Tuple[int,int,int], cur: Tuple[int,int,int]) -> str | None:
    if cur[0] > base[0]:
        return "major"
    if cur[0] == base[0] and cur[1] > base[1]:
        return "minor"
    if cur > base:
        return "patch"
    return None  # no bump or lower


def read_version_from_text(toml_text: str) -> str:
    data = tomli.loads(toml_text)
    v = data.get("project", {}).get("version")
    if not v:
        raise ValueError("project.version missing in pyproject.toml")
    return v


def read_version_from_file(path: pathlib.Path) -> str:
    return read_version_from_text(path.read_text(encoding="utf-8"))


def any_package_changes(base_ref: str, package_dirs: List[str]) -> bool:
    # List changed files vs base
    diff = run(["git", "diff", "--name-only", f"{base_ref}...HEAD"]).stdout.splitlines()
    if not diff:
        return False
    # If pyproject changed, we’ll always check
    if "pyproject.toml" in diff:
        return True
    for f in diff:
        for d in package_dirs:
            if f.startswith(d.rstrip("/") + "/"):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-ref", required=True, help="git ref to compare (e.g., origin/main)")
    ap.add_argument("--require-level", default="patch", choices=["patch", "minor", "major"])
    ap.add_argument("--package-dirs", default="src", help='space-separated dirs (default: "src")')
    args = ap.parse_args()

    # Ensure we have the base ref
    try:
        run(["git", "fetch", "--no-tags", "--depth=1", "origin", args.base_ref.split("/", 1)[-1]], check=False)
    except Exception:
        pass

    package_dirs = args.package_dirs.split()

    # Skip if package code didn’t change
    if not any_package_changes(args.base_ref, package_dirs):
        print("No package changes detected; version bump not required.")
        return 0

    # Read current version (working tree)
    cur_ver_str = read_version_from_file(pathlib.Path("pyproject.toml"))

    # Read base version from that ref
    try:
        base_pyproject = run(["git", "show", f"{args.base_ref}:pyproject.toml"]).stdout
    except subprocess.CalledProcessError:
        print(f"::warning::Couldn't read pyproject.toml at {args.base_ref}; assuming bump required.")
        base_pyproject = ""

    if not base_pyproject:
        print("::warning::No base pyproject found; skipping strict compare.")
        return 0

    base_ver_str = read_version_from_text(base_pyproject)

    base = parse_version(base_ver_str)
    cur = parse_version(cur_ver_str)

    lvl = version_level(base, cur)
    if lvl is None:
        print(f"::error::project.version {cur_ver_str} is not greater than base {base_ver_str}")
        print("Please bump the version in pyproject.toml.")
        return 2

    required = args.require_level
    ok = (
        (required == "patch" and lvl in {"patch", "minor", "major"}) or
        (required == "minor" and lvl in {"minor", "major"}) or
        (required == "major" and lvl == "major")
    )

    if not ok:
        print(f"::error::Required level: {required} bump; found: {lvl} (base {base_ver_str} -> current {cur_ver_str})")
        return 3

    print(f"Version bump OK: {base_ver_str} -> {cur_ver_str} ({lvl})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
