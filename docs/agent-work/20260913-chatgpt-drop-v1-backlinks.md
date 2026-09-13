# Work Record — 20260913-chatgpt-drop-v1-backlinks

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-drop-v1-backlinks`
- Base: `main@60e1f454de7afb70b8eb9b2b3f7294db76b7b92a`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

Remove historical Go Study v1 backlink compatibility that the owner confirmed is no longer needed, while preserving the current Managed v3 and Freeform v2 formats and the separate optional Legacy JV input path.

This includes both:

- Managed v1 `resource + position + v=1` input compatibility;
- beta.15 Freeform `mode=freeform&path=...&v=1` compatibility.

## Exact writable file scope

Actual writes:

- `src/resource-reference.cjs`
- `src/entry.cjs`
- `tests/resource-reference.test.cjs`
- `tests/resource-reference-runtime.test.cjs`
- `tests/timeline-navigator.test.cjs`
- `tests/reference-fallback.test.cjs`
- `README.md`
- `docs/ROADMAP.md`
- `main.js` (generated through build)
- this work record

Temporary branch-only helper (created and deleted before merge):

- `.github/workflows/rebuild-v1-cleanup.yml`

### Scope deviation

The first CI run after tightening the parser exposed existing v1 assumptions in runtime and Timeline tests. Those tests were added to scope. `tests/reference-fallback.test.cjs` was added because its fixtures described generic Resource-ID recovery as “legacy v1” even though that recovery mechanism remains useful for current Managed links whose Resource state is missing.

A temporary branch-only workflow rebuilt the generated `main.js`; it was deleted immediately after the generated bundle commit and is not part of the final PR diff.

## Changes made

- Managed Go Study parser accepts only current `v=3`.
- Freeform Go Study parser accepts only current `v=2`.
- Removed `path` from allowed Go Study protocol/query keys.
- beta.15 `mode=freeform&path=...&v=1` fails closed.
- Managed `v=1` fails closed.
- Internal Freeform -> matching Managed Resource promotion now uses the current Managed v3 semantic constant instead of constructing a v1 object.
- Removed the internal `reference.path` Freeform fallback.
- Runtime/Timeline fixtures now use current v3 semantics.
- Resource-ID recovery/relink capability remains, but tests no longer describe it as a v1 feature.
- README and Roadmap now describe Managed/Freeform as the useful product families and explicitly note that current v2/v3 are not a chronological old/new sequence.
- Roadmap records a dedicated future protocol-semantic naming cleanup rather than silently changing current wire URLs.

## Do not touch / preserved

- state/schema/migration format
- Preview -> Stable migration
- Legacy `jv://open?...` compatibility behavior
- Bilibili native `?t=` URLs
- Resource-ID recovery/relinking for missing current Managed resources
- architecture-layer structure

## Compatibility / data impact

- Intentional breaking input change: historical Go Study v1 links stop opening.
- Current Managed v3 links remain supported/generated.
- Current Freeform v2 links remain supported/generated.
- beta.15 `path=` input is no longer accepted.
- Legacy JV remains separately supported when explicitly enabled.
- No `data.json` schema or migration change.

Owner confirmed there are no important notes relying on v1 compatibility and explicitly approved dropping it.

## Validation

- [FAIL] First PR CI: 425 tests, 418 pass, 7 fail. All failures were stale v1 assumptions in runtime/Timeline tests; tightened protocol tests themselves passed.
- [PASS] Follow-up CI `34749672367`: full `Run release checks` passed after stale runtime/Timeline/recovery semantics were updated.
- [FAIL] Same run failed only `Verify committed main.js is current`, as expected before generated bundle commit.
- [PASS] Temporary branch build workflow `34749728733` rebuilt and committed `main.js` from source; no hand-editing.
- [PASS] Temporary rebuild workflow was deleted before final integration.
- [PASS] Final CI `34749753534`: `Run release checks` passed and `Verify committed main.js is current` passed. 425 tests passed within the release-check step.
- [MANUAL REQUIRED] Existing Windows/Obsidian final 0.3.0 smoke remains the product release gate; this compatibility cleanup does not replace that acceptance.

## Rollback

Revert this work item/PR to restore v1/beta.15 input parsing. No user state migration is involved.

## Remaining risk

Any unsearched external/Vault note that still contains historical Go Study v1/beta.15 links will no longer open. The owner explicitly searched their important notes and accepted this boundary before public release.

## Handoff

Merge after review. After merge, treat:

- **Managed** = current v3 wire format;
- **Freeform** = current v2 wire format;
- **Legacy JV** = separate optional compatibility adapter.

Do not re-add v1 merely to make an old fixture/test pass. Future protocol naming changes must be a dedicated design/migration task.
