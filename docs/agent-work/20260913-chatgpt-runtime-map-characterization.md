# Work Record — 20260913-chatgpt-runtime-map-characterization

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-runtime-map-characterization`
- Base: `main@12a8d0e2094c2764452253178d55e18238f374ca`
- Started: 2026-09-13 (UTC+8)

## Goal

1. Map the current runtime control flow without changing runtime behavior.
2. Document the `main.cjs -> entry.cjs -> runtime-entry.cjs` inheritance/override structure and the most important lifecycle/call chains.
3. Add characterization tests that lock down selected current architecture-sensitive behavior before any later flattening/refactor is considered.
4. Record observations neutrally; this work does not assume the current architecture is defective or that a rewrite is required.

## Exact writable file scope

Planned writes:

- `docs/ARCHITECTURE_RUNTIME_MAP.md` (new)
- `tests/runtime-architecture-characterization.test.cjs` (new)
- `docs/agent-work/20260913-chatgpt-runtime-map-characterization.md`

If test discovery requires a script change, `package.json` may be added to scope only after documenting that deviation here first.

## Read-only inspection scope

- `src/main.cjs`
- `src/entry.cjs`
- `src/runtime-entry.cjs`
- directly related settings/protocol/runtime helper modules
- existing tests relevant to lifecycle, protocol, settings, persistence, and resource opening

## Do not touch

- `src/**` runtime implementation
- `main.js`
- `manifest.json`
- state/schema/migration behavior
- backlink/PotPlayer compatibility behavior
- current 0.3.0 feature set
- release workflow

## Compatibility / data impact

- Runtime impact: none intended.
- State/schema impact: none.
- Migration impact: none.
- Backlink compatibility impact: none.
- Generated bundle impact: none.

## Validation plan

- Confirm inheritance and method-override relationships from source.
- Map at least: startup/onload, settings registration, protocol registration, resource opening, Vault lifecycle validation, and persistence/data-safety path.
- Prefer behavior/contract assertions over brittle whole-file snapshots.
- Run repository CI through the PR and report exact status.

## Test log

- [UNRUN] New characterization tests — not written yet.
- [UNRUN] Full CI — branch work not yet complete.

## Rollback

Delete the new architecture document/test file and revert this work record. No runtime or user data change is planned.
