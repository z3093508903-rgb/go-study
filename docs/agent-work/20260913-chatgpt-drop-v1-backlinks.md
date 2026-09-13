# Work Record — 20260913-chatgpt-drop-v1-backlinks

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-drop-v1-backlinks`
- Base: `main@60e1f454de7afb70b8eb9b2b3f7294db76b7b92a`
- Started: 2026-09-13 (UTC+8)

## Goal

Remove historical Go Study v1 backlink compatibility that the owner confirmed is no longer needed, while preserving the current Managed v3 and Freeform v2 formats and the separate optional Legacy JV input path.

This includes both:

- Managed v1 `resource + position + v=1` input compatibility;
- beta.15 Freeform `mode=freeform&path=...&v=1` compatibility.

## Exact writable file scope

- `src/resource-reference.cjs`
- `src/entry.cjs`
- `tests/resource-reference.test.cjs`
- `tests/resource-reference-runtime.test.cjs`
- `tests/timeline-navigator.test.cjs`
- `tests/reference-fallback.test.cjs`
- `README.md`
- `docs/ROADMAP.md`
- `main.js` (generated only, through build)
- this work record

### Scope deviation

The first CI run after tightening the parser exposed existing v1 assumptions in runtime and Timeline tests. Those tests are now explicitly in scope. `tests/reference-fallback.test.cjs` is also in scope because its test names/fixtures describe generic Resource-ID recovery as “legacy v1” even though that recovery mechanism remains useful for current Managed links whose Resource state is missing.

## Do not touch

- state/schema/migration format
- Preview -> Stable migration
- Legacy `jv://open?...` compatibility behavior
- Bilibili native `?t=` URLs
- product features unrelated to backlink parsing
- architecture-layer refactor

## Compatibility / data impact

- Intentional breaking input change: historical Go Study v1 links stop opening.
- Current Managed v3 links remain supported/generated.
- Current Freeform v2 links remain supported/generated.
- beta.15 `path=` input stops being accepted.
- Legacy JV remains separately supported when explicitly enabled.
- Resource-ID recovery / relinking for current Managed links remains supported.
- No `data.json` schema or migration change.

Owner confirmed there are no important notes relying on v1 compatibility and explicitly approved dropping it.

## Validation plan

- Make Managed parser accept only v3.
- Make Freeform parser accept only v2 and `locator`, not historical `path`.
- Ensure v1 and beta.15 examples fail closed in tests.
- Update internal managed-reference construction so runtime code does not create semantic v1 objects.
- Move runtime/Timeline fixtures to current v3 semantics.
- Keep Resource-ID recovery tests while removing misleading “legacy v1” semantics from them.
- Rebuild `main.js`.
- Run full repository CI/release checks.

## Rollback

Revert this work item/PR to restore v1/beta.15 input parsing. No user state migration is involved.

## Test log

- [FAIL] First PR CI run: 425 tests, 418 pass, 7 fail. Failures were all stale v1 assumptions in `resource-reference-runtime` and `timeline-navigator`; the tightened protocol parser itself passed its new current-format/rejection tests.
- [UNRUN] Follow-up full CI — pending cleanup of discovered dependencies and regenerated `main.js`.
