# AGENTS.md — Go Study

## Repository role

Engineering/development source repository:

`z3093508903-rgb/go-study`

Default branch:

`main`

This repository is the owner's development source of truth for current code, tests, migration policy, architecture decisions, and agent handoff records.

Public distribution may be performed from a separate repository chosen by the owner. Until that repository is explicitly recorded, do **not** infer one and do not publish/mirror/sync to another repository without an explicit owner instruction.

This repository-role statement supersedes older wording in `docs/HANDOFF_CURRENT.md` that may describe this repository as the final public distribution repository. The current 0.3.0 smoke/release baseline in that handoff remains useful; only the repository-role/publication assumption is superseded until the handoff is refreshed after final acceptance.

Do **not** continue development from `z3093508903-rgb/learning-resource-hub-vnext`.

That repository is an early-development archive / archaeology source only.

## Bootstrap before changing anything

Read, in order:

1. `docs/AGENT_COLLABORATION.md`
2. `docs/HANDOFF_CURRENT.md`
3. active `docs/agent-work/*.md` records that overlap the task
4. `README.md`
5. `docs/USER_GUIDE.md`
6. the current release notes relevant to the target version
7. `manifest.json`
8. the code/tests directly relevant to the task

Repository state is authoritative over old chat memory.

## Multi-agent work rule

Normal changes must follow `docs/AGENT_COLLABORATION.md`.

Minimum contract:

- one task = one `work_id` = one `work/<work_id>` branch;
- create `docs/agent-work/<work_id>.md` before implementation changes;
- register exact writable file scope and do-not-touch scope;
- do not silently overlap another active work item's file/behavior scope;
- do not write directly to `main` for normal feature/fix/refactor/release-engineering work;
- completion records must use `[PASS]`, `[FAIL]`, `[UNRUN]`, and `[MANUAL REQUIRED]` test markers;
- every state/schema/migration/compatibility change must declare impact and rollback behavior.

`docs/HANDOFF_CURRENT.md` is a baseline summary, not a scratchpad. Routine task details belong in the work record.

## Current release rule

Go Study 0.3.0 is feature-frozen.

Before the first public release candidate is accepted:

- fix regressions only;
- do not add YouTube, AI, cloud sync, OCR, statistics, calendar, or new platform features;
- preserve Preview -> Stable migration;
- preserve optional Legacy JV compatibility;
- do not casually add or remove beta-era compatibility behavior without first documenting the actual parser/runtime behavior;
- do not reintroduce the withdrawn OpenList unsigned fallback.

Post-0.3 candidate work is recorded in `docs/ROADMAP.md` and is not automatically approved for the frozen release.

## Historical identifiers

Intentional for 0.3.0:

- `go-study-preview`: migration/recovery/coexistence only;
- `learning-resource-hub-next`: coexistence conflict detection only;
- `jv://open?...`: explicitly supported historical external link input when Legacy JV compatibility is enabled.

Internal names such as `ResourceHubNext*` and `rh-next-*` may remain until a later dedicated refactor. This engineering repository may contain historical/internal names that do not affect Stable product identity. Do not mass-rename them before 0.3.0.

Important compatibility distinction:

- new output format and old-input readability are separate questions;
- do not claim an old format is unsupported until parser/runtime/tests confirm it;
- do not claim compatibility merely because an old identifier still exists internally.

See `docs/ROADMAP.md` for the current compatibility inventory.

## Release validation

Current Stable identity:

- id: `go-study`
- name: `Go Study`
- version: `0.3.0`
- workbench view type: `go-study-workbench`

Before release, generate a fresh final migration/smoke package from current `main` and get real-machine confirmation.

Current strict release rules expect tag:

`0.3.0`

not `v0.3.0`.

Release-note file convention:

`docs/RELEASE_NOTES_<tag>.md`

The development-repository release workflow is packaging/validation infrastructure; it must not be treated as proof of the final public distribution state when a separate distribution repository is used.

## Safety

Never commit:

- real `data.json`;
- Vault content;
- credentials/tokens/cookies;
- bridge authentication tokens;
- personal backups;
- real OpenList secrets.

Automated tests do not replace real Windows/Obsidian acceptance for PotPlayer, OpenList, Companion, global hotkeys, browser bridge, backup restore, or Preview -> Stable migration.
