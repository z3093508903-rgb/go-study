# Work Record — 20260913-chatgpt-freeform-bilibili-title

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-freeform-bilibili-title`
- Base: `main@4ed69807691daf98d44428acc6081e4dd01762fb`
- Started: 2026-09-13 (UTC+8)

## Goal

Fix the right-side Timeline title for uncollected / Freeform Bilibili media. Managed resources already use the stored Resource title; Freeform media currently trust the player/bridge title, which can be only a BV identifier. The desired product behavior is to prefer a human-readable video title when a BV identifier can be resolved, without requiring the media to be collected into a learning project.

## Product semantics

- Managed media: keep using `Resource.title` as authoritative display title.
- Freeform media: keep its portable identity, but enrich machine-like Bilibili titles such as `BV...` when the BV ID is identifiable.
- Timeline remains derived UI; it should not become the owner of remote metadata fetching.
- Metadata lookup failure must never block capture or timestamp insertion.

## Exact writable file scope

- `src/bilibili-metadata.cjs` (new)
- `src/learning-capture.cjs`
- `src/timeline-navigator.cjs`
- `tests/bilibili-metadata.test.cjs` (new)
- `tests/learning-capture.test.cjs`
- `tests/timeline-navigator.test.cjs`
- `docs/CODE_PRODUCT_SEMANTICS.md`
- `main.js` (generated only through build)
- `.github/workflows/tmp-freeform-bili-title.yml` (temporary branch-only helper; deleted before merge)
- `scripts/tmp_apply_freeform_bili_title.py` (temporary branch-only helper; deleted before merge)
- this work record

Additional files may enter scope only if CI proves a direct dependency; any scope deviation must be recorded first.

## Do not touch

- Managed v3 / Freeform v2 wire format
- Legacy JV compatibility
- state/schema/migration format
- Preview -> Stable migration
- project membership semantics
- Timeline playback/navigation semantics
- Bilibili Bridge authentication/on-demand-listener roadmap work

## Data / compatibility impact

- No `data.json` schema change.
- No backlink protocol change.
- New Freeform backlinks can carry a better human-readable `title` value.
- Existing Freeform links remain valid. Existing BV-only Timeline entries may improve during a session when Go Study has learned the Bilibili title through the bridge or metadata lookup; no destructive note rewrite is planned.
- External metadata lookup is best-effort and only attempted for Freeform media whose title is missing/machine-like and whose BV ID can be identified.

## Validation plan

- Add pure BV extraction / machine-title detection / metadata-fetch tests.
- Verify human titles never trigger a metadata request.
- Verify BV-only Freeform capture enriches the generated backlink title when metadata resolves.
- Verify lookup failure still inserts a working backlink.
- Verify Timeline can use an already-known cached/live Bilibili title without performing network I/O itself.
- Verify Timeline prefers cached human title over a BV-only Freeform title but keeps normal Freeform titles unchanged.
- Rebuild `main.js` and run full repository CI/release checks.
- Real Windows/Obsidian acceptance remains required for the user’s exact PotPlayer/Bilibili path.

## Rollback

Revert this work item/PR. No migration or user-state rollback is required.

## Test log

- [UNRUN] implementation tests — work just registered.
- [UNRUN] full CI.
- [MANUAL REQUIRED] reproduce with an uncollected Bilibili video and confirm Timeline shows the real title rather than only the BV ID.
