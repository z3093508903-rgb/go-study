# Work Record — 20260913-chatgpt-state-safety-protection-result

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-state-safety-protection-result`
- Base: current `main`
- Started: 2026-09-13 (UTC+8)

## Goal

Make backup/protection failure explicit and retryable. A failed pre-save protection must not advance `lastProtectedRaw`. Ordinary saves may continue in a clearly degraded protection state, while high-risk Preview migration and state restore must not replace current state unless a protective snapshot succeeds first.

## Exact writable file scope

- `src/state-safety.cjs`
- `src/main.cjs`
- `tests/state-safety.test.cjs`
- additional existing state/restore tests only if directly required
- `main.js` (generated only)
- this work record

Temporary branch-only helper files may be used and must be deleted before merge.

## Do not touch

- state schema/model semantics
- backup JSON format
- Preview source data
- protocol/playback/capture behavior

## Validation plan

- [UNRUN] failed pre-save snapshot does not advance `lastProtectedRaw` and a later call retries.
- [UNRUN] ordinary persist records degraded protection without claiming success.
- [UNRUN] Preview migration refuses to proceed when its safety snapshot cannot be created.
- [UNRUN] restore refuses to replace current state when the pre-restore safety snapshot cannot be created.
- [UNRUN] full release checks and bundle verification.
- [MANUAL REQUIRED] real Vault backup/restore acceptance remains required.
