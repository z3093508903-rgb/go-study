# AGENTS.md — Go Study

## Canonical repository

All current development and release work must use:

`z3093508903-rgb/go-study`

Default branch:

`main`

Do **not** continue development from `z3093508903-rgb/learning-resource-hub-vnext`.

That repository is an early-development archive only.

## Bootstrap before changing code

Read, in order:

1. `docs/HANDOFF_CURRENT.md`
2. `README.md`
3. `docs/USER_GUIDE.md`
4. `docs/RELEASE_NOTES_0.3.0.md`
5. `manifest.json`
6. the code/tests directly relevant to the task

## Current release rule

Go Study 0.3.0 is feature-frozen.

Before the first public release:

- fix regressions only;
- do not add YouTube, AI, cloud sync, OCR, statistics, calendar, or new platform features;
- preserve Preview -> Stable migration;
- preserve optional Legacy JV compatibility;
- do not restore intermediate beta-era compatibility branches;
- do not reintroduce the withdrawn OpenList unsigned fallback.

## Historical identifiers

Intentional for 0.3.0:

- `go-study-preview`: migration/recovery/coexistence only;
- `learning-resource-hub-next`: coexistence conflict detection only;
- `jv://open?... `: explicitly supported historical external link input.

Internal names such as `ResourceHubNext*` and `rh-next-*` may remain until a later dedicated refactor. Do not mass-rename them before 0.3.0.

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

## Safety

Never commit:

- real `data.json`;
- Vault content;
- credentials/tokens/cookies;
- personal backups;
- real OpenList secrets.

Automated tests do not replace real Windows/Obsidian acceptance for PotPlayer, OpenList, Companion, global hotkeys, backup restore, or Preview -> Stable migration.
