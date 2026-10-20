# Project Status

Last updated: 2026-10-21
Status type: initial verified checkpoint

## Verified repository state

- Repository currently named: `manish91082-coder/aists-btcusdt-research-runner`.
- Default branch: `main`.
- The `main` branch was verified empty immediately before this bootstrap.
- The empty-tree commit that began the clean slate: `f52bac573c9509c71143158a7f609bd55a6a76bb`.
- Previous snapshot commit: `f2fcc6f2e74dcd08e59cdcb811cd680d35fb1733`.
- Backup branch: `backup/pre-cleanup-2026-10-21-main-f2fcc6f`, intended to preserve the previous snapshot.
- Desired display/project name: **Full AI Crypto Trading Bot 21 OCT**.
- GitHub repository rename is pending; it has not been performed.

## Work completed

1. Confirmed the prior main snapshot and its tracked-file count before clean-slate reset.
2. Created the backup branch at the prior snapshot.
3. Moved `main` to a new commit with the canonical empty Git tree.
4. Re-verified `main` points to the clean-slate commit and the GitHub contents API returned an empty list.
5. Began rebuilding repository governance and continuity files directly on `main`.

## Not yet done / do not imply completion

- No trading engine or strategy has been implemented on the new `main`.
- No backtest, paper-trading, exchange integration, security audit, or live-trading test has been run as part of this clean-slate work.
- No credentials or API keys have been configured.
- Repository rename has not been completed.
- The old snapshot has not been independently exported as a ZIP; preservation is via GitHub Git history and backup branch.

## Next action

Complete and verify the initial governance/continuity file set. Then define the bot's requirements and architecture with the user before implementing trading logic.

## Verification policy

Before changing files, fetch the current `main` ref and read relevant GitHub content. After changes, verify the new commit and each updated file. Never report a task as complete without evidence from the repository.