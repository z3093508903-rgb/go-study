# Work Record — 20260913-chatgpt-freeform-bilibili-title

- Status: `ready_for_merge`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-freeform-bilibili-title`
- Base: `main@4ed69807691daf98d44428acc6081e4dd01762fb`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

Fix the right-side Timeline title for uncollected / Freeform Bilibili media. Managed resources already use the stored Resource title; Freeform media previously trusted the player/bridge title, which can be only a BV identifier. The desired product behavior is to prefer a human-readable video title when a BV identifier can be resolved, without requiring the media to be collected into a learning project.

## Product semantics

- Managed media: keep using `Resource.title` as authoritative display title.
- Freeform media: keep its portable identity, but enrich machine-like Bilibili titles such as `BV...` when the BV ID is identifiable.
- Timeline remains derived UI; it does not own remote metadata fetching.
- Metadata lookup failure never blocks capture or timestamp insertion.

## Exact writable file scope

Actual accepted branch diff:

- `src/bilibili-metadata.cjs` (new)
- `src/learning-capture.cjs`
- `src/timeline-navigator.cjs`
- `tests/bilibili-metadata.test.cjs` (new)
- `tests/learning-capture.test.cjs`
- `tests/timeline-navigator.test.cjs`
- `docs/CODE_PRODUCT_SEMANTICS.md`
- `main.js` (generated through build)
- this work record

Temporary branch-only helpers were used and deleted before PR merge:

- `.github/workflows/tmp-freeform-bili-title.yml`
- `scripts/tmp_apply_freeform_bili_title.py`

## Do not touch

Preserved:

- Managed v3 / Freeform v2 wire format
- Legacy JV compatibility
- state/schema/migration format
- Preview -> Stable migration
- project membership semantics
- Timeline playback/navigation semantics
- Bilibili Bridge authentication/on-demand-listener roadmap work

## Implementation

- Added a small Bilibili metadata adapter that can extract a BV ID from a Bilibili URL, PotPlayer title, or local filename.
- BV-only / machine-like labels are not treated as final human titles.
- For Freeform capture only, Go Study performs a best-effort request to Bilibili's public `x/web-interface/view?bvid=...` metadata endpoint when a human title is missing.
- Resolved titles are cached in memory for the current plugin session, avoiding repeated requests for the same BV.
- Existing human-readable titles bypass remote lookup entirely.
- Timeline can reuse already-known cached title data or the current matching Bilibili Web Bridge state, but Timeline itself never starts network metadata requests.
- The generated Freeform backlink remains v2; only its existing `title` metadata becomes more useful.

## Data / compatibility impact

- No `data.json` schema change.
- No backlink protocol change.
- No project membership change.
- New Freeform backlinks can carry a better human-readable `title` value.
- Existing Freeform links remain valid and are not rewritten.
- Existing BV-only Timeline entries may improve during a session when Go Study has learned the title through a matching Bilibili bridge state or metadata lookup.
- External metadata lookup is best-effort; failure falls back to the original media identity and never blocks timestamp insertion.

## Validation

- [PASS] BV extraction works from Bilibili URL, PotPlayer-style BV title, and BV-named local file.
- [PASS] BV-only labels are classified as machine labels; normal human titles are preserved.
- [PASS] Metadata lookup resolves a human title and caches it.
- [PASS] Existing human titles cause zero metadata requests.
- [PASS] Metadata failure is fail-open and keeps timestamp insertion usable.
- [PASS] BV-only Freeform PotPlayer capture writes the resolved human title into the Freeform v2 backlink.
- [PASS] Timeline prefers already-known cached/live human Bilibili title over a BV-only label.
- [PASS] Focused tests passed in temporary branch workflow `34754912065`.
- [PASS] `main.js` rebuilt from source in the same workflow.
- [PASS] Full PR CI / release checks passed in run `34754944721`.
- [PASS] committed `main.js` is current.
- [MANUAL REQUIRED] reproduce with the user's exact uncollected Bilibili/PotPlayer path and confirm the right Timeline shows the real title rather than only the BV ID.

## Rollback

Revert this work item/PR. No migration or user-state rollback is required.

## Handoff

Merge after CI remains green. Then test in real Obsidian with one uncollected Bilibili video. If the exact PotPlayer path does not expose a BV identifier anywhere in URL/title/filename, capture will safely fall back to the old label; that specific transport would need an additional identity source rather than guessing.
