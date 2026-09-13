# Work Record — 20260913-chatgpt-vault-lifecycle-coordination

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-vault-lifecycle-coordination`
- Base: current `main`
- Started: 2026-09-13 (UTC+8)

## Goal

Fix Vault lifecycle coordination so layout-readiness gates cover the complete Runtime behavior and each rename/delete/create event mutates `vaultRefs` plus Project Notes before a single persist. Avoid the current split-persist path where Base and Runtime can leave the two domains out of sync after a failure.

## Exact writable file scope

- `src/main.cjs`
- `src/runtime-entry.cjs`
- `src/vault-lifecycle.cjs` (new)
- `tests/vault-lifecycle.test.cjs` (new)
- `tests/runtime-architecture-characterization.test.cjs`
- `docs/ARCHITECTURE_RUNTIME_MAP.md`
- `main.js` (generated only)
- this work record

Temporary branch-only helper files may be used and must be deleted before merge.

## Do not touch

- Vault data schema
- Project Notes data schema
- migration/backlink/playback behavior
- existing layout-readiness timing itself

## Validation plan

- [UNRUN] readiness=false skips the whole coordinated event and does not persist.
- [UNRUN] one changed event persists exactly once after all domain mutations run.
- [UNRUN] persist failure occurs only after both domain mutations have run, preventing the prior half-updated in-memory state.
- [UNRUN] full release checks and bundle verification.
- [MANUAL REQUIRED] real Obsidian rename/delete/create acceptance before final release.
