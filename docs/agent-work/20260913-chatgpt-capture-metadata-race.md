# Work Record — 20260913-chatgpt-capture-metadata-race

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-capture-metadata-race`
- Base: `main@23c908ee63e7a16915ac6caf6965201a5267f588`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

Remove the clipboard race introduced by best-effort Bilibili title enrichment. Capture must snapshot PNG bytes immediately after the player capture response, before any optional metadata await. Also bound metadata lookup time so timestamp/capture workflows cannot hang indefinitely on title enrichment.

## Exact writable file scope

- `src/learning-capture.cjs`
- `src/bilibili-metadata.cjs`
- `tests/learning-capture.test.cjs`
- `tests/bilibili-metadata.test.cjs`
- `main.js` (generated only)
- this work record

Temporary branch-only helper files were removed before review.

## Do not touch

- Managed v3 / Freeform v2 protocol format
- state/schema/migration
- project membership
- Timeline navigation semantics
- Bilibili Bridge auth/listener roadmap work

## Implemented behavior

- PNG bytes are read immediately after the player returns a capture, before optional title enrichment awaits.
- Bilibili title lookup has a finite default timeout and remains fail-open.
- Metadata failure/timeout cannot block capture indefinitely.

## Safety / rollback

No persistent-data or protocol change. Revert this PR to roll back.

## Validation

- [PASS] behavior test proves PNG bytes remain the original capture while delayed metadata lookup mutates the simulated clipboard.
- [PASS] metadata helper rejects a hung request after a finite test timeout.
- [PASS] focused `learning-capture` + `bilibili-metadata` tests.
- [PASS] PR CI run `34756618404`: full release checks passed.
- [PASS] committed `main.js` matches rebuilt source.
- [MANUAL REQUIRED] real Windows PotPlayer/Bilibili screenshot + timeline acceptance.

## Data / schema impact

None.
