"""Preflight the source-owned authorization artifacts before packaging.

The check is deliberately offline and read-only.  It confirms that the
validation policy and its delivery note are present, and prevents the named
v2.3.7 installer samples from being copied into a release tree.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Iterable


REQUIRED_FILES = (
    Path("portable") / "authorization_policy.py",
    Path("docs") / "AUTHORIZATION_DELIVERY.md",
)
REQUIRED_DOC_MARKERS = (
    "source-owned validation",
    "offline comparison only",
)
V237_SAMPLE_NAMES = frozenset(
    {
        "QQFarmCVHelper_v2.3.7_x64_setup.exe",
        "QQFarmCVHelper_v2.3.7_x64_green.exe",
    }
)
V237_SAMPLE_DIR = "v2.3.7-standalone"


def _iter_files(root: Path) -> Iterable[Path]:
    try:
        return (path for path in root.rglob("*") if path.is_file())
    except OSError:
        return ()


def check_delivery_tree(
    root: str | Path,
    *,
    allow_analysis: bool = False,
) -> list[str]:
    """Return actionable delivery issues; return an empty list when clean."""

    base = Path(root)
    issues: list[str] = []
    if not base.is_dir():
        return [f"delivery root missing: {base}"]

    for relative in REQUIRED_FILES:
        path = base / relative
        if not path.is_file():
            issues.append(f"required delivery file missing: {relative.as_posix()}")

    policy_path = base / REQUIRED_FILES[0]
    if policy_path.is_file():
        try:
            ast.parse(policy_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, SyntaxError) as error:
            issues.append(f"authorization policy is not parseable: {error}")

    note_path = base / REQUIRED_FILES[1]
    if note_path.is_file():
        try:
            note = note_path.read_text(encoding="utf-8").lower()
            for marker in REQUIRED_DOC_MARKERS:
                if marker.lower() not in note:
                    issues.append(f"authorization delivery note missing marker: {marker}")
        except (OSError, UnicodeError) as error:
            issues.append(f"authorization delivery note is unreadable: {error}")

    flagged_v237_dir = False
    for path in _iter_files(base):
        relative_parts = tuple(part.lower() for part in path.relative_to(base).parts)
        if allow_analysis and any(
            part in {".analysis", V237_SAMPLE_DIR}
            for part in relative_parts
        ):
            continue
        if V237_SAMPLE_DIR in relative_parts:
            if not flagged_v237_dir:
                issues.append(
                    "v2.3.7 standalone comparison tree must remain outside the release tree"
                )
                flagged_v237_dir = True
            continue
        if path.name in V237_SAMPLE_NAMES:
            issues.append(
                "v2.3.7 installer sample must remain outside the release tree: "
                + path.relative_to(base).as_posix()
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="release or source tree")
    parser.add_argument(
        "--source-tree",
        action="store_true",
        help="ignore preserved local analysis directories in a source checkout",
    )
    args = parser.parse_args(argv)
    issues = check_delivery_tree(args.root, allow_analysis=args.source_tree)
    if issues:
        for issue in issues:
            print("ERROR: " + issue)
        return 1
    print("OK: authorization delivery preflight passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
