# Go Study — Current Handoff

Last updated: 2026-08-30 (UTC+8)

## 0. Canonical repository

**Continue all development from:**

`z3093508903-rgb/go-study`

Default branch:

`main`

**Do NOT continue product development from:**

`z3093508903-rgb/learning-resource-hub-vnext`

The old `learning-resource-hub-vnext` repository is now only an **early-development archive / archaeology source**. It can be consulted to understand history, but code must not be copied back blindly and it must not become the release baseline again.

---

## 1. Current stable identity

Permanent public plugin identity:

```json
{
  "id": "go-study",
  "name": "Go Study",
  "version": "0.3.0",
  "minAppVersion": "1.7.2",
  "isDesktopOnly": true
}
```

Public repository:

`https://github.com/z3093508903-rgb/go-study`

License:

MIT

Core product promise:

> Go Study is free and open source.
>
> Core features will not be locked behind a paywall.
>
> Go Study 免费且开源，0.3.0 已有的核心学习功能将永久免费且开源，不会在未来被移到付费墙后。

Future optional paid services are only acceptable for NEW capabilities with recurring operational cost, e.g. AI, cloud sync, hosted/server/API services.

The settings page includes a quiet voluntary **支持 Go Study** entry. No popups, badges, feature gating, or sponsorship nags.

---

## 2. Current repository state

Current `main` HEAD at handoff:

`eaa6f5fccc1296c6ac0c1c6e56f824ad170d814f`

Final legacy-cleanup validator:

- Workflow run: `33267875450`
- Job: `99141063261`
- Build: **38 source modules / 780320 bytes**
- Tests: **419 / 419 PASS**
- Fail: **0**
- **Strict release check passed**

The validator rebuilt and committed the current `main.js`.

Important: several recent ordinary CI runs are red because source changes were pushed before the rebuilt `main.js` was committed. The one-shot strict validator then rebuilt `main.js`, passed all tests, and committed the validated bundle. Do not interpret those earlier red runs as product regressions.

---

## 3. Latest real-machine issue discovered

### Symptom

The first Stable migration test package used the permanent plugin ID `go-study`.

The user reported:

> “我的笔记盒不见了，切回旧版就看得见。”

The underlying project-note data was **not lost**.

### Root cause

Historical workbench view ID remained:

`learning-resource-hub-next-workbench`

while Stable UI injection code derived the selector from the permanent plugin ID:

`go-study-workbench`

Therefore project-page DOM enhancements could not find the workbench after the Stable identity switch.

Affected surfaces potentially included:

- Project Notes / 笔记盒 button
- Continue Learning injection
- workbench learning-control/status UI
- any DOM enhancer scoped through `<plugin-id>-workbench`

### Fix

The stable workbench view type is now:

`go-study-workbench`

Additional stale identity cleanup was also completed:

- stale `learning-resource-hub-next-workbench` selector removed from `styles.css`;
- local deploy example changed to `.obsidian/plugins/go-study`;
- state-safety default plugin path changed from Preview to `go-study`;
- stale “Learning Resource Hub” runtime log text removed;
- intermediate old-plugin state recovery path removed;
- tests updated to enforce Stable identity rather than old class names;
- final strict validation passed 419/419.

A regression test now asserts that registered workbench view type equals:

`<manifest.id>-workbench`

---

## 4. Migration behavior: Preview -> Stable

Preview/test plugin ID:

`go-study-preview`

Stable plugin ID:

`go-study`

Stable 0.3.0 includes one-time safe migration.

Migration occurs only when:

1. Stable `go-study/data.json` does not yet exist / contains no meaningful state; and
2. `go-study-preview/data.json` contains meaningful state.

Migration safety:

- Preview `data.json` is not deleted or modified;
- a `saved-preview-migration-...` recovery snapshot is created;
- state is then persisted into Stable `go-study/data.json`;
- if Stable already has its own `data.json`, Preview will **not** overwrite it.

Do not remove Preview migration support before 0.3.0 ships.

---

## 5. Historical identifiers: what remains and why

A legacy-string audit was performed after the missing Notes Box bug.

### Intentional and must remain for 0.3.0

#### `go-study-preview`

Still appears in:

- Preview -> Stable migration;
- recovery lookup for Preview-era state;
- coexistence/protocol-conflict warning.

This is intentional.

#### `learning-resource-hub-next`

Still appears in `src/entry.cjs` as a **conflicting previous plugin ID** only.

Purpose:

- detect an old plugin still enabled at the same time;
- warn about `obsidian://go-study` protocol contention;
- keep Go Study startup fail-safe.

Do not re-add the old plugin as a general state-recovery source.

#### `jv://open?... `

This is the only historical external link compatibility explicitly promised.

Policy:

- JV is input-only;
- new notes never output JV;
- compatibility switch remains optional / advanced.

### Historical names that are internal only

The code still contains internal identifiers such as:

- `ResourceHubNextPlugin`
- `ResourceHubNextView`
- `ResourceHubNextRuntimePlugin`
- many `rh-next-*` CSS class names

These are implementation names, not public product identity.

**Do not rename them before 0.3.0.**

A mass rename would create a large regression surface for no user benefit. If desired, do it later as a dedicated post-0.3 refactor with tests.

### Removed / should not return

Do not restore:

- `learning-resource-hub-next-workbench`
- `go-study-preview-workbench`
- old `learning-resource-hub-vnext` public URLs in Stable code/docs
- beta/alpha labels as runtime identity
- intermediate beta-era PotPlayer link compatibility
- old Learning Resource Hub state-recovery branches beyond the specifically documented migration/conflict boundary

---

## 6. OpenList incident — do not “fix” it again

During RC acceptance, project-page OpenList launch and OpenList timestamps showed `ERR_CONNECTION_REFUSED`.

A fallback was briefly introduced that tried unsigned `/d/` playback when the API was unreachable.

The user later discovered the real cause:

> the backing network drive had not been mounted.

After mounting it, the existing OpenList/PotPlayer workflow worked normally.

Decision:

- the unsigned fallback was withdrawn;
- OpenList unavailable / storage unmounted should fail visibly;
- do not hide missing external dependencies with speculative playback fallback.

---

## 7. Product scope frozen for 0.3.0

No new features before first public release.

Current core includes:

- Project/resource workbench
- local video / PotPlayer
- OpenList
- Bilibili Freeform
- optional Bilibili Web Bridge
- Companion real Markdown window
- Alt+S HUD
- timestamp / note capture
- Timeline
- Native Markdown drag
- Project Notes Box
- Continue Learning
- backup / named backup / selectable restore
- Preview -> Stable migration
- Legacy JV compatibility

### Explicitly not in 0.3.0

- YouTube dedicated adapter
- AI summary
- cloud sync
- OCR
- learning statistics
- calendar
- cross-device state sync
- browser screenshot capture

Bilibili was intentionally prioritized because the first validated users/workflows are China-centric.

YouTube may be added later only after real overseas user demand/workflow evidence.

---

## 8. Public launch docs already present

Public repository contains:

- `README.md`
- `docs/USER_GUIDE.md`
- `docs/RELEASE_NOTES_0.3.0.md`
- `docs/index.html`
- `docs/PRIVACY.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- Issue templates
- PR template
- MIT `LICENSE`

Landing-page/product message focuses on:

> Don't rebuild yesterday's learning setup.

Old workflow:

`find resource -> open player -> find position -> open Obsidian -> find project -> find note -> manually timestamp -> switch back`

Go Study:

`Project -> resource -> study`

Capture:

`Alt + S -> write`

---

## 9. What the next ChatGPT window should do first

### Step 1 — Read current repo, not memory

Open/read from `z3093508903-rgb/go-study@main`:

1. `AGENTS.md`
2. this file: `docs/HANDOFF_CURRENT.md`
3. `README.md`
4. `docs/USER_GUIDE.md`
5. `docs/RELEASE_NOTES_0.3.0.md`
6. `manifest.json`
7. relevant code for any issue being investigated

Do not start from `learning-resource-hub-vnext`.

### Step 2 — Do not publish yet

The user has not yet confirmed a real-machine test of the **post-cleanup current main**.

The earlier Stable Migration Test V2 fixed the Notes Box workbench-ID bug, but additional cleanup happened after that package was built.

Therefore:

> Generate a fresh **Stable Migration Test V3 / final candidate** from current `go-study/main`, not from the old repo and not from the older V2 artifact.

### Step 3 — Ask for a very short real-machine smoke

The final candidate only needs focused checks:

1. Stable project page opens with correct layout.
2. Notes / 笔记盒 button is visible.
3. Existing linked notes are present.
4. Continue Learning appears/works when applicable.
5. Project-page video/PotPlayer still opens.
6. OpenList works with required storage mounted.
7. One current timestamp opens + seeks correctly.
8. Alt+S / Companion still works.
9. Fully restart Obsidian once and re-check Notes Box + data.
10. Preview remains disabled after Stable is confirmed.

Do not make the user repeat the entire historical RC checklist unless one of these regresses.

### Step 4 — If smoke passes, release

Current release workflow/strict checker expects the tag to equal the manifest version exactly.

Under current rules use:

`0.3.0`

not `v0.3.0`, unless the workflow/checker is deliberately changed first.

Then:

- create tag `0.3.0`;
- let `.github/workflows/release.yml` run strict validation and package:
  - plugin zip
  - `main.js`
  - `manifest.json`
  - `styles.css`
  - Bilibili Bridge zip
- verify GitHub Release assets;
- only then proceed to Obsidian Community Plugins submission and optional GitHub Pages deployment.

---

## 10. Release blocker definition

**HOLD** if the final candidate shows any of:

- missing Notes Box / Continue Learning entry;
- project/resource data missing;
- Stable unexpectedly overwrites its own data from Preview;
- wrong Capture target;
- wrong video/timestamp seek;
- backup restore data loss;
- Companion Markdown caret regression;
- plugin startup crash;
- global overlay residue.

Otherwise publish.

---

## 11. Important release-engineering note

Because `main.js` is committed, ordinary CI can temporarily go red when source is pushed before the rebuilt bundle is committed.

The final one-shot strict validation already passed and committed the current bundle.

Do not “fix product code” based only on those intermediate red CI runs. Read the failing job first.

After 0.3.0, consider simplifying contributor CI so source PRs do not look broken merely because generated `main.js` has not yet been committed. This is a release-engineering cleanup, not a product blocker.

---

## 12. Bottom line

**Canonical repo:** `z3093508903-rgb/go-study`

**Old repo:** archive only.

**Current state:** code complete, feature frozen, historical identity cleanup validated, waiting for one fresh final Stable migration/smoke package and real-machine confirmation before `0.3.0` release.
