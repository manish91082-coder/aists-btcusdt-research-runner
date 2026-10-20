# Full AI Crypto Trading Bot 21 OCT

This repository is the source of truth for project state, operating rules, safety locks, decisions, and session continuity.

## Current state

- Working branch: `main`
- State: clean-slate bootstrap; no application files or trading implementation currently exist on `main`.
- Previous snapshot: preserved at branch `backup/pre-cleanup-2026-10-21-main-f2fcc6f`.
- Repository rename: not performed; the current GitHub repository name remains `aists-btcusdt-research-runner`.
- No claim is made that a trading bot is implemented, tested, paper-trading, or live-trading.

## Continuity files

- [Project status](PROJECT_STATUS.md): verified current state and next action.
- [Project memory](PROJECT_MEMORY.md): durable decisions and project facts.
- [Continuity protocol](CONTINUITY.md): how to resume work without drift.
- [Rules, locks, and regulations](RULES_AND_LOCKS.md): non-negotiable operating constraints.
- [Session log](SESSION_LOG.md): chronological record of work and verification.
- [Changelog](CHANGELOG.md): repository-level changes.

## Required workflow

At the start of a session or after a chat-thread switch, read these files from GitHub before acting. Verify the live branch head and relevant files rather than trusting chat memory alone. After each substantive project action, update the status, memory, continuity checkpoint, rules/locks if changed, session log, and changelog as applicable, then verify the resulting GitHub state. If a required write or verification fails, report that failure plainly.

All implementation and project-state changes are to be made directly in this GitHub repository unless the user explicitly changes that instruction.