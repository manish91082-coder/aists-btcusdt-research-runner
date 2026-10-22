#!/usr/bin/env python3
"""Safely stage deletion of tracked files outside the current crypto-target project.

Default is DRY RUN. Nothing is removed unless --apply AND the exact repository
confirmation are supplied. This does not erase Git history or other branches.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXPECTED_REPO = "manish91082-coder/aists-btcusdt-research-runner"

KEEP_EXACT = {
    "README.md",
    "CRYPTO_10CR_RESEARCH_LOG_HI.md",
    "CRYPTO_10CR_PROJECT_STATUS.md",
    "crypto_target/__init__.py",
    "crypto_target/research_math.py",
    "tests_crypto_target/test_research_math.py",
    ".github/workflows/crypto-target-smoke.yml",
    ".github/workflows/repository-cleanup-preview.yml",
    "scripts/cleanup_current_project.py",
    "scripts/EXECUTE_CLEANUP_NOW",
    "CURRENT_PROJECT_KEEP_PATHS.txt",
    "execution_logs/2026-10-22-repo-discovery.md",
    "execution_logs/2026-10-22-research-harness-bootstrap.md",
    "execution_logs/2026-10-22-cleanup-script-push.md",
}

KEEP_PREFIXES = (
    "crypto_target/",
    "tests_crypto_target/",
    "execution_logs/crypto-target/",
)


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run or stage removal of tracked files outside the current project allowlist."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually stage deletion of tracked files not on the keep list. Without this, only preview.",
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

    tracked = run_git("ls-files", "-z").stdout.split("\0")
    tracked = sorted(p for p in tracked if p)

    def keep(path: str) -> bool:
        return path in KEEP_EXACT or any(path.startswith(prefix) for prefix in KEEP_PREFIXES)

    removals = [p for p in tracked if not keep(p)]
    protected = [p for p in tracked if keep(p)]

    print(f"Repository: {EXPECTED_REPO}")
    print(f"Tracked files found: {len(tracked)}")
    print(f"Protected current-project files: {len(protected)}")
    print(f"Tracked files to stage for deletion: {len(removals)}")
    print("NOTE: untracked/ignored files are not touched; Git history and other branches are not erased.")
    print("\n--- KEEP ---")
    for path in protected:
        print(f"  KEEP  {path}")
    print("\n--- DELETE CANDIDATES ---")
    for path in removals:
        print(f"  DELETE {path}")

    if not args.apply:
        print("\nDRY RUN ONLY. No files changed.")
        print("Review the list, then rerun with --apply --confirm-repository "
              f"{EXPECTED_REPO!r} to stage the listed deletions.")
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
        f"- Protected files: {len(protected)}",
        f"- Tracked paths staged for deletion: {len(removals)}",
        "- Scope: tracked files only; untracked/ignored files untouched.",
        "- Git history and other branches are not erased.",
        "- Deletions are staged for review; this script does not commit or push.",
        "",
        "## Protected files",
        *[f"- `{p}`" for p in protected],
        "",
        "## Paths staged for deletion",
        *[f"- `{p}`" for p in removals],
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
