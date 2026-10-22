#!/usr/bin/env python3
"""Safely stage removal of tracked files outside a committed keep-list.

Default is DRY RUN. Applying requires --apply and an exact repository
confirmation. This utility never commits, pushes, or erases Git history/branches.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_REPO = "manish91082-coder/aists-btcusdt-research-runner"
KEEP_LIST_NAME = "CURRENT_PROJECT_KEEP_PATHS.txt"
REQUIRED_PATHS = {
    "README.md",
    "CRYPTO_10CR_PROJECT_DETAILS.md",
    "CRYPTO_10CR_PROJECT_STATUS.md",
    "CRYPTO_10CR_RESEARCH_LOG_HI.md",
    KEEP_LIST_NAME,
    "scripts/cleanup_current_project.py",
    ".github/workflows/crypto-target-smoke.yml",
    ".github/workflows/repository-cleanup-preview.yml",
    "crypto_target/__init__.py",
    "crypto_target/research_math.py",
    "tests_crypto_target/test_research_math.py",
}


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def load_keep_rules(root: Path) -> tuple[set[str], tuple[str, ...]]:
    keep_file = root / KEEP_LIST_NAME
    if not keep_file.is_file():
        raise ValueError(f"Required allowlist is missing: {KEEP_LIST_NAME}")

    entries = [
        line.strip().replace("\\", "/")
        for line in keep_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if KEEP_LIST_NAME not in entries:
        raise ValueError(f"{KEEP_LIST_NAME} must protect itself in its own allowlist.")

    exact = {entry for entry in entries if not entry.endswith("/")}
    prefixes = tuple(entry for entry in entries if entry.endswith("/"))
    if not exact and not prefixes:
        raise ValueError("The keep-list is empty; refusing to risk deleting the project.")
    return exact, prefixes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview or stage removal of tracked files outside CURRENT_PROJECT_KEEP_PATHS.txt."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Stage tracked-file deletions. Without this flag, the script only previews.",
    )
    parser.add_argument(
        "--confirm-repository",
        default="",
        help=f"Required with --apply; must exactly equal {EXPECTED_REPO!r}.",
    )
    args = parser.parse_args()

    try:
        root = Path(run_git("rev-parse", "--show-toplevel").stdout.strip())
        remote = run_git("remote", "get-url", "origin", check=False)
        remote_url = (remote.stdout or "").strip().lower()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"ERROR: run this inside a Git clone. {exc}", file=sys.stderr)
        return 2

    if "github.com" not in remote_url or EXPECTED_REPO not in remote_url:
        print("ERROR: origin remote does not match the expected repository.", file=sys.stderr)
        print(f"Repository root: {root}", file=sys.stderr)
        print(f"Detected origin: {remote_url or '(missing)'}", file=sys.stderr)
        return 2

    try:
        keep_exact, keep_prefixes = load_keep_rules(root)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: invalid or unavailable keep-list; refusing cleanup. {exc}", file=sys.stderr)
        return 2

    def keep(path: str) -> bool:
        return path in keep_exact or any(path.startswith(prefix) for prefix in keep_prefixes)

    unprotected_required = sorted(path for path in REQUIRED_PATHS if not keep(path))
    if unprotected_required:
        print("ERROR: required current-project paths are not protected; refusing cleanup:", file=sys.stderr)
        for path in unprotected_required:
            print(f"  {path}", file=sys.stderr)
        return 2

    tracked = sorted(path for path in run_git("ls-files", "-z").stdout.split("\0") if path)
    protected = [path for path in tracked if keep(path)]
    removals = [path for path in tracked if not keep(path)]

    print(f"Repository: {EXPECTED_REPO}")
    print(f"Tracked files found: {len(tracked)}")
    print(f"Protected current-project files: {len(protected)}")
    print(f"Tracked files to stage for deletion: {len(removals)}")
    print(f"Allowlist source: {KEEP_LIST_NAME}")
    print("NOTE: untracked/ignored files are not touched; Git history and other branches are not erased.")
    print("\n--- KEEP ---")
    for path in protected:
        print(f"  KEEP  {path}")
    print("\n--- DELETE CANDIDATES ---")
    for path in removals:
        print(f"  DELETE {path}")

    if not args.apply:
        print("\nDRY RUN ONLY. No files changed.")
        print("Review the list before applying. Applying stages deletions; this script does not commit or push.")
        return 0

    if args.confirm_repository != EXPECTED_REPO:
        print("ERROR: --apply requires --confirm-repository with the exact repository name.", file=sys.stderr)
        return 2

    if not removals:
        print("Nothing to delete; no changes made.")
        return 0

    print("\nApplying tracked-file cleanup with git rm (deletions will be STAGED, not committed/pushed)...")
    run_git("rm", "--", *removals)

    log_dir = root / "execution_logs" / "crypto-target"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"cleanup-{stamp}.md"
    body = [
        f"# Repository cleanup log — {stamp}",
        "",
        f"- Repository: {EXPECTED_REPO}",
        f"- Protected tracked files: {len(protected)}",
        f"- Tracked paths staged for deletion: {len(removals)}",
        f"- Allowlist source: `{KEEP_LIST_NAME}`",
        "- Scope: tracked files only; untracked/ignored files untouched.",
        "- Git history and other branches are not erased.",
        "- Deletions are staged for review; this script does not commit or push.",
        "",
        "## Protected tracked files",
        *[f"- `{path}`" for path in protected],
        "",
        "## Paths staged for deletion",
        *[f"- `{path}`" for path in removals],
        "",
        "## Required follow-up",
        "Review `git status --short` and this log. Commit and push only if the staged deletion list is correct.",
    ]
    log_path.write_text("\n".join(body) + "\n", encoding="utf-8")
    run_git("add", "--", str(log_path.relative_to(root)))
    print(f"Cleanup log staged: {log_path.relative_to(root)}")
    print("DONE: deletions and cleanup log are staged. Inspect with: git status --short")
    print("No commit or push was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
