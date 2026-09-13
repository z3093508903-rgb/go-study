# Work Record — 20260913-chatgpt-collaboration-release-roadmap

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-collaboration-release-roadmap`
- Base: `main@43e40ce06994036b3fafacffa6da0823241d9112`
- Started: 2026-09-13 (UTC+8)

## Goal

1. Make release notes selection version-aware instead of hard-coding `0.3.0`.
2. Establish a durable multi-agent collaboration and handoff protocol for this development repository.
3. Record Bilibili Bridge authentication and on-demand listener startup as post-0.3 product options, without changing 0.3.0 runtime behavior.
4. Clarify that this repository is the engineering/development source repository and that public distribution may be performed from a separate distribution repository chosen by the owner.

## Exact file scope

Planned writes:

- `.github/workflows/release.yml`
- `AGENTS.md`
- `docs/AGENT_COLLABORATION.md` (new)
- `docs/ROADMAP.md` (new)
- `docs/HANDOFF_CURRENT.md`
- `docs/agent-work/20260913-chatgpt-collaboration-release-roadmap.md`

No runtime source files, tests, schemas, migration logic, or `main.js` are in scope.

## Do not touch

- `src/**`
- `tests/**`
- `main.js`
- `manifest.json`
- current Preview -> Stable migration behavior
- current backlink / PotPlayer / Legacy JV compatibility behavior

## Compatibility / data impact

- Runtime behavior: none intended.
- State/schema impact: none.
- Migration impact: none.
- Public distribution repository: not named here; do not infer one until the owner explicitly records it.

## Validation plan

- Inspect resulting workflow syntax and release-notes path convention.
- Confirm existing `docs/RELEASE_NOTES_0.3.0.md` matches the dynamic path convention.
- Review collaboration rules for file-scope ownership, branch isolation, test reporting, schema/data disclosures, rollback, and handoff.

## Test log

- [UNRUN] Runtime tests — no runtime source change is planned.
- [UNRUN] GitHub Actions execution — workflow change cannot be executed locally through this connector.

## Handoff

Pending changes and review.
