# Work Record — 20260913-chatgpt-collaboration-release-roadmap

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-collaboration-release-roadmap`
- Base: `main@43e40ce06994036b3fafacffa6da0823241d9112`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

1. Make release notes selection version-aware instead of hard-coding `0.3.0`.
2. Establish a durable multi-agent collaboration and handoff protocol for this development repository.
3. Record Bilibili Bridge authentication and on-demand listener startup as post-0.3 product options, without changing 0.3.0 runtime behavior.
4. Clarify that this repository is the engineering/development source repository and that public distribution may be performed from a separate distribution repository chosen by the owner.

## Exact file scope

Actual writes:

- `.github/workflows/release.yml`
- `AGENTS.md`
- `docs/AGENT_COLLABORATION.md` (new)
- `docs/ROADMAP.md` (new)
- `docs/agent-work/20260913-chatgpt-collaboration-release-roadmap.md`

No runtime source files, tests, schemas, migration logic, or `main.js` were changed.

### Scope deviation

`docs/HANDOFF_CURRENT.md` was initially listed as a planned write but intentionally left unchanged because the owner is still performing the final 0.3.0 real-machine check and that file contains the detailed frozen release baseline.

Instead, `AGENTS.md` now explicitly states that the development-vs-distribution repository rule supersedes the older publication assumption in the handoff while preserving its smoke/release baseline. `docs/HANDOFF_CURRENT.md` should be refreshed after final acceptance/release-state changes.

## Do not touch

Preserved:

- `src/**`
- `tests/**`
- `main.js`
- `manifest.json`
- current Preview -> Stable migration behavior
- current backlink / PotPlayer / Legacy JV compatibility behavior

## Changes made

### Release workflow

Release notes are now resolved from the pushed tag using:

`docs/RELEASE_NOTES_<tag>.md`

The workflow fails clearly if the version-matched notes file is absent.

Existing `docs/RELEASE_NOTES_0.3.0.md` already matches the convention.

### Multi-agent protocol

Added `docs/AGENT_COLLABORATION.md` with:

- one task / one work_id / one work branch;
- exact file-scope registration before implementation;
- overlap/conflict handling;
- standardized `[PASS]`, `[FAIL]`, `[UNRUN]`, `[MANUAL REQUIRED]` validation markers;
- generated `main.js` ownership rules;
- explicit state/schema/migration/compatibility disclosures;
- rollback requirements;
- criteria for updating the baseline handoff;
- separation between development source repository and an owner-selected distribution repository.

### Product/engineering roadmap

Added `docs/ROADMAP.md` and recorded as post-0.3 candidates:

1. Bilibili Bridge local request authentication/token;
2. on-demand Bilibili Bridge listener startup/shutdown;
3. runtime layering cleanup;
4. compatibility inventory/cleanup.

Release-engineering cleanup for version-aware release notes is marked `planned` and implemented in this branch.

## Compatibility / data impact

- Runtime behavior: none.
- State/schema impact: none.
- Migration impact: none.
- Backlink compatibility impact: none.
- PotPlayer behavior impact: none.
- Public distribution repository: intentionally unnamed; agents must not infer one.

## Validation

- [PASS] Existing `docs/RELEASE_NOTES_0.3.0.md` matches the new `docs/RELEASE_NOTES_<tag>.md` convention for tag `0.3.0`.
- [PASS] Branch diff contains only workflow/docs/work-record changes; no `src/**`, `tests/**`, `main.js`, or `manifest.json` changes.
- [PASS] Collaboration protocol explicitly covers work_id, branch isolation, exact file scope, overlap handling, generated files, testing markers, state/schema/migration impact, rollback, and handoff.
- [UNRUN] Runtime tests — no runtime source or generated bundle changed.
- [UNRUN] GitHub Actions execution — the modified release workflow is only triggered by a release tag and was not invoked as part of this documentation/release-engineering work.
- [MANUAL REQUIRED] Owner final 0.3.0 Windows/Obsidian smoke remains unchanged and is still the release gate.

## Rollback

Revert the commits in this work branch/PR. No user data or runtime migration is involved.

## Remaining risks

- `docs/HANDOFF_CURRENT.md` still contains older wording that treats this repository as the public/release repository. `AGENTS.md` explicitly supersedes only that repository-role assumption until the handoff is refreshed.
- The separate distribution repository is not yet named, so no automation should target it.
- The current parser still accepts some historical Go Study inputs; this branch only documents that fact and does not change compatibility.

## Handoff

Next integration step:

1. review the branch/PR;
2. merge if accepted;
3. continue the owner's final 0.3.0 real-machine smoke;
4. refresh `docs/HANDOFF_CURRENT.md` when the final acceptance/release state changes;
5. only then decide publication/mirroring behavior for the separate distribution repository.
