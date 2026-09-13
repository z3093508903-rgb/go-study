# Work Record — 20260913-chatgpt-capture-metadata-race

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-capture-metadata-race`
- Base: current `main`
- Started: 2026-09-13 (UTC+8)

## Goal

Remove the clipboard race introduced by best-effort Bilibili title enrichment. Capture must snapshot PNG bytes immediately after the player capture response, before any optional metadata await. Also bound metadata lookup time so timestamp/capture workflows cannot hang indefinitely on title enrichment.

## Exact writable file scope

- `src/learning-capture.cjs`
- `src/bilibili-metadata.cjs`
- `tests/learning-capture.test.cjs`
- `tests/bilibili-metadata.test.cjs`
- `main.js` (generated only)
- this work record

Temporary branch-only helper files may be used and must be deleted before merge.

## Do not touch

- Managed v3 / Freeform v2 protocol format
- state/schema/migration
- project membership
- Timeline navigation semantics
- Bilibili Bridge auth/listener roadmap work

## Safety / rollback

No persistent-data or protocol change. Revert the work item/PR to roll back.

## Validation plan

- [UNRUN] prove PNG bytes are captured before delayed metadata resolution can change the clipboard.
- [UNRUN] prove metadata lookup has a finite fail-open timeout.
- [UNRUN] focused tests.
- [UNRUN] full release checks and bundle drift verification.
- [MANUAL REQUIRED] real Windows PotPlayer/Bilibili screenshot + timeline acceptance.
