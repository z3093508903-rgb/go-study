# Work Record — 20260913-chatgpt-vault-lifecycle-coordination

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-vault-lifecycle-coordination`
- Base: `main@12fd1e1f171d0a82e21b589f0bacf0a9b926cf07`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

Fix Vault lifecycle coordination so layout-readiness gates cover the complete Runtime behavior and each rename/delete/create event mutates `vaultRefs` plus Project Notes before a single persist. Avoid the prior split-persist path where Base and Runtime could leave the two domains out of sync after a failure.

## Exact writable file scope

- `src/main.cjs`
- `src/runtime-entry.cjs`
- `src/vault-lifecycle.cjs` (new)
- `tests/vault-lifecycle.test.cjs` (new)
- `tests/runtime-architecture-characterization.test.cjs`
- `docs/ARCHITECTURE_RUNTIME_MAP.md`
- `main.js` (generated only)
- this work record

Temporary branch-only helper files were removed before review.

## Implemented behavior

- Base exposes `applyVaultRename`, `applyVaultDelete`, and `applyVaultCreate` mutation helpers without persistence.
- Runtime coordinates Vault Ref and Project Notes mutations inside `coordinateVaultLifecycleEvent()`.
- `_vaultLifecycleReady === false` skips the whole current-product event before any state mutation.
- Changed rename/delete/create events persist/render once after all affected domains have moved together.
- Entry-layer readiness overrides remain as defensive lower-layer behavior.

## Do not touch

- Vault data schema
- Project Notes data schema
- migration/backlink/playback behavior
- existing layout-readiness timing itself

## Validation

- [PASS] readiness=false skips the complete event, mutation callback, and persist.
- [PASS] one changed event mutates both domains before exactly one persist.
- [PASS] a simulated persist failure occurs only after both domains have moved together in memory, removing the prior half-updated state.
- [PASS] unchanged events do not persist.
- [PASS] existing Project Notes lifecycle tests and runtime characterization tests pass with the new boundary.
- [PASS] PR CI `34757073461`: full release checks passed.
- [PASS] committed `main.js` matches rebuilt source.
- [MANUAL REQUIRED] real Obsidian rename/delete/create acceptance before final release.

## Data / schema impact

None. This changes event coordination/persistence boundaries only.

## Rollback

Revert this PR. No user-data migration rollback is required.
