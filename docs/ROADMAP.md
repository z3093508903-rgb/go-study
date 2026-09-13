# Go Study — Product / Engineering Roadmap

This roadmap records candidate work after the 0.3.0 release freeze. Items here are options, not promises or committed release dates.

## Status vocabulary

- `candidate` — worth considering; no implementation commitment yet.
- `planned` — owner has approved the direction.
- `in_progress` — active work_id exists.
- `deferred` — intentionally postponed.
- `rejected` — do not pursue unless the owner reopens the decision.

---

## 1. Bilibili Bridge request authentication

**Status:** `candidate`

### Problem

The local Bilibili Bridge listener binds to `127.0.0.1`, but the current state endpoint accepts local POST requests without an application-level authentication token.

This is not treated as a remote-code-execution issue. The main risk is local/web-origin state spoofing: another process or page could try to submit a fake Bilibili URL/title/time and make Go Study believe it is the current learning source.

### Candidate design

Use a short-lived or installation-local random bridge token shared between the Go Study plugin and the browser bridge.

Possible transport:

- request header such as `X-Go-Study-Token`;
- plugin rejects missing/invalid tokens;
- token is generated locally and is never committed to the repository;
- avoid exposing the token in user notes or logs.

### Acceptance questions before implementation

- How will the unpacked browser extension learn the token with minimal setup friction?
- Should the token survive Obsidian restarts or rotate?
- Is origin restriction useful in addition to token authentication?
- How will upgrade/migration work for existing bridge users?

### Non-goals

- Do not add cloud authentication.
- Do not turn the bridge into a general remote-control API.
- Do not grant additional browser host permissions solely for authentication.

---

## 2. On-demand Bilibili Bridge listener

**Status:** `candidate`

### Problem

The browser bridge is optional product functionality, but the current runtime starts the local listener during plugin startup even when the user is not using Bilibili web enhancement.

### Candidate design

Add an explicit product setting, for example:

`bilibiliBridgeEnabled`

Behavior candidate:

- disabled: no `127.0.0.1:27124` listener;
- enabled: start listener and expose status;
- turning it off: close the listener cleanly;
- port conflict / startup errors remain visible rather than silently falling back.

### Questions before implementation

- Should enabling `videoEnhancementEnabled` automatically enable the bridge, or remain separate?
- Should the UI distinguish “bridge feature enabled”, “listener started”, and “browser connected”?
- Should PotPlayer-only users ever start the bridge implicitly? Preferred answer: no, unless a concrete workflow requires it.

### Non-goals

- Do not change 0.3.0 runtime behavior during release freeze.
- Do not hide bridge startup errors.

---

## 3. Runtime layering cleanup

**Status:** `candidate`

The current implementation has accumulated compatibility/extension layers around `main.cjs`, `entry.cjs`, and `runtime-entry.cjs`.

A post-release refactor may reduce inheritance/override patching and move toward explicit services/modules such as:

- Workbench controller;
- Project/resource services;
- Vault lifecycle service;
- PotPlayer adapter;
- OpenList adapter;
- Bilibili adapter;
- state repository / migration layer;
- settings service.

This is an engineering-maintainability project, not a user-facing feature.

Constraints:

- preserve current behavior first;
- no mass rename mixed into the architectural refactor;
- migration/state behavior requires dedicated tests;
- do not remove old-input compatibility merely because the code looks cleaner.

---

## 4. Release engineering cleanup

**Status:** `planned`

### Version-aware release notes

Release workflow should select release notes from the tag/version instead of permanently hard-coding `0.3.0`.

Convention:

`docs/RELEASE_NOTES_<tag>.md`

Examples:

- `docs/RELEASE_NOTES_0.3.0.md`
- `docs/RELEASE_NOTES_0.3.1.md`
- `docs/RELEASE_NOTES_0.4.0.md`

The workflow should fail clearly if the matching notes file does not exist.

### Development vs distribution repository

This repository is the owner's engineering/development source repository.

The final public distribution repository may be separate. Its identity must be explicitly recorded before any agent performs publication/mirroring automation.

Do not infer that a release created here is necessarily the final public release channel.

---

## 5. Compatibility inventory / cleanup

**Status:** `candidate`

Before deleting compatibility branches, maintain a table of historical inputs:

| Input family | New output generated? | Old input accepted? | Policy |
| --- | --- | --- | --- |
| Current managed Go Study backlink (v3) | yes | yes | stable current format |
| Current freeform Go Study backlink (v2) | yes | yes | stable current format |
| Managed Go Study backlink v1 | no for new managed notes | yes | existing old-input compatibility |
| Beta path-style freeform Go Study link | no | currently accepted by parser | review/document policy before removal |
| `jv://open?...` | no | optional when Legacy JV compatibility is enabled | explicitly supported historical input |
| Native Bilibili `?t=` URL | yes for Bilibili web mode | browser-native | not a Go Study protocol |

Rule: distinguish **output compatibility** from **input compatibility**. A format may stop being generated while remaining readable for old notes.
