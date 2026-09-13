# Work Record — 20260913-chatgpt-runtime-map-characterization

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-runtime-map-characterization`
- Base: `main@12a8d0e2094c2764452253178d55e18238f374ca`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

1. Map the current runtime control flow without changing runtime behavior.
2. Document the `main.cjs -> entry.cjs -> runtime-entry.cjs` inheritance/override structure and the most important lifecycle/call chains.
3. Add characterization tests that lock down selected current architecture-sensitive behavior before any later flattening/refactor is considered.
4. Record observations neutrally; this work does not assume the current architecture is defective or that a rewrite is required.

## Exact writable file scope

Actual writes:

- `docs/ARCHITECTURE_RUNTIME_MAP.md` (new)
- `tests/runtime-architecture-characterization.test.cjs` (new)
- `docs/agent-work/20260913-chatgpt-runtime-map-characterization.md`

No `package.json` change was required because the existing `tests/*.test.cjs` test command discovers the new test automatically.

## Read-only inspection scope

- `src/main.cjs`
- `src/entry.cjs`
- `src/runtime-entry.cjs`
- directly related settings/protocol/runtime helper modules
- existing tests relevant to lifecycle, protocol, settings, persistence, and resource opening

## Do not touch

Preserved:

- `src/**` runtime implementation
- `main.js`
- `manifest.json`
- state/schema/migration behavior
- backlink/PotPlayer compatibility behavior
- current 0.3.0 feature set
- release workflow

## What was documented

`docs/ARCHITECTURE_RUNTIME_MAP.md` records:

- runtime inheritance stack;
- startup / `onload` chain;
- dynamic dispatch during base `onload`;
- settings-tab interception;
- Go Study protocol registration;
- normal resource-open layering;
- positioned backlink playback;
- persistence/data-safety chain;
- Vault event layering;
- a no-rewrite/incremental-refactor boundary.

## Characterization tests added

The new tests lock down selected current contracts:

1. three-layer inheritance relationships;
2. Vault validation stays deferred until layout readiness;
3. base settings registration is intercepted by product settings;
4. product integrations register only after lower-layer startup completes;
5. resource play remains layered runtime -> entry -> base;
6. persistence retains the data-safety ordering around `saveData`;
7. Vault callbacks remain virtual/extendable across the lifecycle and project-note layers.

These tests intentionally characterize current source/control-flow contracts. They are not an architectural target forever; if a later approved refactor changes structure while preserving behavior, that refactor must deliberately update the corresponding characterization test and explain the replacement contract.

## Compatibility / data impact

- Runtime impact: none.
- State/schema impact: none.
- Migration impact: none.
- Backlink compatibility impact: none.
- Generated bundle impact: none.

## Validation

- [PASS] PR #2 GitHub Actions CI run `34748002895` completed successfully.
- [PASS] CI `release-check` job completed successfully, including repository release checks and committed `main.js` currency verification.
- [PASS] New characterization tests are automatically included by the existing `node --test --test-concurrency=1 tests/*.test.cjs` command.
- [PASS] Changed scope is documentation/tests/work-record only; no runtime implementation or generated bundle was edited.
- [MANUAL REQUIRED] Owner's existing final 0.3.0 Windows/Obsidian smoke remains the product release gate; this PR does not replace it.

## Decisions

- Do not rewrite the plugin architecture as part of this work.
- Treat the current layered design as an evolutionary architecture whose hidden override contracts should be made visible first.
- Any later flattening should be narrow, behavior-preserving, reversible, and performed only after 0.3.0 acceptance.

## Rollback

Revert PR #2 / delete the two newly added architecture/test files and this work record. No user data, migration, schema or runtime code is involved.

## Remaining risks

- Static characterization tests intentionally depend on selected source structure; future approved structural refactors will need to update them deliberately rather than treating failures as product regressions automatically.
- Real Windows/Obsidian integration behavior still requires the owner's existing smoke test.

## Handoff

Next step after merge:

1. keep 0.3.0 runtime frozen during final real-machine acceptance;
2. obtain an independent architecture review if desired;
3. compare that review with `docs/ARCHITECTURE_RUNTIME_MAP.md`;
4. after release acceptance, choose at most one narrow structural seam for the first behavior-preserving refactor rather than starting a rewrite.
