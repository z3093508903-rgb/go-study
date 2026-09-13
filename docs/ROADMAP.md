# Go Study — Product / Engineering Roadmap

This roadmap records candidate work after the 0.3.0 release freeze. Items here are options, not promises or committed release dates unless explicitly marked `planned`.

## Status vocabulary

- `candidate` — worth considering; no implementation commitment yet.
- `planned` — owner has approved the direction.
- `in_progress` — active work_id exists.
- `deferred` — intentionally postponed.
- `rejected` — do not pursue unless the owner reopens the decision.
- `done` — decision/work has been implemented and validated.

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

- Do not hide bridge startup errors.

---

## 3. Runtime layering cleanup

**Status:** `candidate`

The current implementation has accumulated compatibility/extension layers around `main.cjs`, `entry.cjs`, and `runtime-entry.cjs`.

A future refactor may reduce inheritance/override patching and move toward explicit services/modules such as:

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
- use `docs/ARCHITECTURE_RUNTIME_MAP.md` and characterization tests as the baseline;
- no mass rename mixed into architectural refactors;
- migration/state behavior requires dedicated tests;
- prefer incremental flattening over rewrite-from-scratch.

---

## 4. Release engineering cleanup

**Status:** `done`

### Version-aware release notes

Release workflow selects release notes from the tag/version instead of permanently hard-coding `0.3.0`.

Convention:

`docs/RELEASE_NOTES_<tag>.md`

Examples:

- `docs/RELEASE_NOTES_0.3.0.md`
- `docs/RELEASE_NOTES_0.3.1.md`
- `docs/RELEASE_NOTES_0.4.0.md`

The workflow fails clearly if the matching notes file does not exist.

### Development vs distribution repository

This repository is the owner's engineering/development source repository.

The final public distribution repository may be separate. Its identity must be explicitly recorded before any agent performs publication/mirroring automation.

Do not infer that a release created here is necessarily the final public release channel.

---

## 5. Backlink compatibility policy

**Status:** `in_progress`

Owner decision on 2026-09-13: historical Go Study v1 compatibility is not required because no important notes depend on it.

Target accepted input families:

| Input family | New output generated? | Input accepted? | Product meaning / policy |
| --- | --- | --- | --- |
| Managed Go Study backlink (`v=3`) | yes | yes | current managed-resource backlink with portable fallback metadata |
| Freeform Go Study backlink (`v=2`) | yes | yes | current unregistered/local/portable-media backlink |
| Managed Go Study backlink (`v=1`) | no | **no** | historical development input; compatibility intentionally removed |
| Beta path-style Freeform (`path=...`, `v=1`) | no | **no** | beta.15 development format; compatibility intentionally removed |
| `jv://open?...` | no | optional when Legacy JV Compatibility is enabled | separate explicitly gated legacy input, not part of Go Study v1/v2/v3 family |
| Native Bilibili `?t=` URL | yes for Bilibili web mode | browser-native | not a Go Study protocol |

Rule: old-input compatibility is a product promise, not a default engineering virtue. Keep it only when there is real user data or a deliberate support commitment.

---

## 6. Protocol semantic naming cleanup

**Status:** `planned`

### Problem

The current wire labels can be misread as a single chronological sequence:

- Freeform uses `v=2`;
- Managed portable uses `v=3`.

In reality these are **two current semantic families**, not “old v2 versus new v3”. This creates unnecessary cognitive load for humans and coding agents and makes Freeform v2 look like historical residue even though it is current.

### Direction

Design a future protocol representation where semantic family and format revision are explicit instead of relying on one global-looking version number.

The design phase should answer:

- Should `managed` / `freeform` become an explicit family/kind field?
- Should each family have its own revision number?
- Can existing current links be migrated or regenerated before changing the wire format?
- What is the smallest stable public protocol surface we want to promise long term?
- Can internal constant names be semantic (`MANAGED_REFERENCE_REVISION`, `FREEFORM_REFERENCE_REVISION`) even before the external wire format changes?

Do not silently change current v2/v3 links as part of unrelated work. Treat this as a dedicated protocol-design change with migration/compatibility decisions made up front.
