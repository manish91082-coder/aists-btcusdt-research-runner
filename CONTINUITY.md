# Session and Chat Continuity Protocol

Use this document whenever resuming after a pause, context loss, or chat-thread change.

## Mandatory resume sequence

1. Fetch the live `main` branch ref from GitHub.
2. Read `README.md`, `PROJECT_STATUS.md`, `PROJECT_MEMORY.md`, `CONTINUITY.md`, `RULES_AND_LOCKS.md`, `SESSION_LOG.md`, and `CHANGELOG.md`.
3. Confirm the latest commit SHA and check whether the repository has changed since the last checkpoint.
4. Inspect relevant code, tests, issue/PR state, and evidence from GitHub before continuing the specific task.
5. Identify the last verified completed step, unresolved blockers, and the next safe action.
6. If Git state contradicts the chat transcript, trust the verified Git state and explain the discrepancy. Never silently overwrite or discard unexpected changes.

## End-of-work checkpoint

After each substantive project action:
1. Update `PROJECT_STATUS.md` with what changed, what is verified, blockers, and the next action.
2. Update `PROJECT_MEMORY.md` for durable decisions or new confirmed facts.
3. Update this file with the latest resume point and any continuity risks.
4. Update `RULES_AND_LOCKS.md` whenever a rule, constraint, or lock changes; otherwise preserve its rules.
5. Append a concise dated entry to `SESSION_LOG.md`.
6. Update `CHANGELOG.md` with repository changes.
7. Commit changes directly to GitHub, then re-fetch and verify the resulting commit and file contents.
8. In the user response, provide the commit link/SHA and state exactly what was verified. If any write or verification fails, say so and leave the status unambiguous.

For purely conversational turns with no project-state change, do not manufacture a repository change. If the user explicitly requires a checkpoint for that turn, record it.

## Current resume point

As of 2026-10-21, the clean-slate reset has been verified. The current work is to establish the governance and continuity files. No trading implementation has been started on the clean-slate `main`.

## Context priority

1. Live GitHub state and verified repository evidence.
2. The governance and continuity files in this repository.
3. Current conversation instructions.
4. Older conversation memory, only when consistent with the above.

## Safety against drift

- Never infer a feature exists because it was planned.
- Never call a test passed unless its output was observed.
- Never claim an exchange order was placed without direct verified execution evidence.
- Preserve unresolved questions as unresolved.
- Keep secrets out of Git.