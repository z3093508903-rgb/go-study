# Go Study — Runtime Architecture Map

Status: descriptive baseline for the current 0.3.0 codebase.

This document describes how the current runtime behaves. It is intentionally neutral: the existence of inheritance/override layers does **not** by itself mean the architecture is defective, and this document is not approval for a rewrite.

The purpose is to make hidden control flow visible before any later maintainability refactor.

## 1. Runtime entry stack

The bundled plugin starts from `src/runtime-entry.cjs`.

```text
Obsidian Plugin
    ↑
src/main.cjs
    ↑ extends
src/entry.cjs
    ↑ extends
src/runtime-entry.cjs   <- build/runtime entry
```

Responsibilities are currently distributed approximately as follows.

### `src/main.cjs`

Base product/workbench implementation:

- state load, normalization and startup data-safety checks;
- Preview -> Stable migration;
- core workbench view and commands;
- Vault reference handling;
- persistence;
- resource launch actions;
- OpenList/Bilibili/Anki/core resource behavior;
- original settings-tab registration;
- most historical UI/workbench implementation.

### `src/entry.cjs`

Stable/runtime hardening layer:

- model resource-locator v2 installation;
- Go Study backlink protocol registration;
- managed/freeform reference open and fallback/relink behavior;
- active media session tracking;
- deferred Vault lifecycle activation;
- resource relink/capture commands;
- newer native-launch hardening.

### `src/runtime-entry.cjs`

Product enhancement layer:

- product settings normalization and settings-tab replacement;
- timeline, note target and Companion registration;
- Bilibili Web Bridge registration;
- immersive hotkeys;
- learning controls and UI fixes;
- project-note entry points;
- project-note-aware resource opening;
- recent-study behavior;
- project-note Vault rename/delete/create extensions;
- recovery-backup retention integration.

## 2. Important property: dynamic dispatch during `super.onload()`

Because the actual plugin instance is `ResourceHubNextRuntimePlugin`, calls made inside a base-class `onload()` through `this.someMethod()` can resolve to an override in a subclass.

This is intentional current behavior and is one of the reasons this map exists.

Two important examples follow.

## 3. Startup / `onload` chain

High-level order:

```text
runtime-entry.onload()
    |
    +--> entry.onload()
            |
            +--> set _vaultLifecycleReady = false
            +--> activeMediaSession = null
            |
            +--> main.onload()
                    |
                    +--> startupSafetySnapshot
                    +--> loadData
                    +--> Preview migration candidate/protection
                    +--> normalizeState
                    +--> catastrophic-drop protection
                    +--> initialize runtime fields
                    +--> register workbench view/commands/events
                    +--> this.addSettingTab(...)
                    |       |
                    |       +--> dynamic dispatch to runtime-entry.addSettingTab()
                    |               -> replaces first base settings tab with GoStudySettingsTab
                    |
                    +--> register Vault rename/delete/create callbacks
                    +--> this.validateVaultRefs()
                            |
                            +--> dynamic dispatch to entry.validateVaultRefs()
                                    -> returns false because lifecycle is not ready
            |
            +--> register resource relink commands
            +--> register learning capture commands
            +--> register `obsidian://go-study`
            +--> schedule activateVaultLifecycle on workspace layout ready
                    -> set _vaultLifecycleReady = true
                    -> call `super.validateVaultRefs()` explicitly
    |
    +--> normalize product settings/project-note state
    +--> persist only if normalization/state initialization changed data
    +--> register timeline/note target/Companion/Bilibili bridge/hotkeys/UI helpers
```

### Why the Vault guard exists

The base `main.onload()` historically validates Vault references immediately. During Stable migration/startup, Obsidian's workspace/Vault lifecycle may not yet be in the desired ready state for that validation.

`entry.cjs` therefore sets `_vaultLifecycleReady = false` **before** calling `super.onload()` and overrides the Vault callbacks so startup-time dynamic dispatch is suppressed. After layout readiness it deliberately calls the base validation implementation.

This is a working compatibility/lifecycle mechanism. A future refactor may make the lifecycle phases explicit, but must preserve the current observable behavior first.

## 4. Settings registration chain

Current chain:

```text
main.onload()
    -> this.addSettingTab(new ResourceHubNextSettingTab(...))

actual instance method resolution
    -> runtime-entry.addSettingTab(tab)
        -> first registration is replaced with GoStudySettingsTab
        -> later registrations delegate to super.addSettingTab(tab)
```

The base `ResourceHubNextSettingTab` remains in `main.cjs`, but the normal current runtime substitutes the product settings tab at registration time.

Implication for maintenance: editing only the original base settings tab may not affect the settings UI users currently see.

## 5. Go Study protocol registration chain

`entry.onload()` registers the `go-study` Obsidian protocol only after `main.onload()` has completed.

```text
registerGoStudyReferenceProtocol()
    -> registerObsidianProtocolHandler('go-study', handler)
    -> handleResourceReference(params)
        -> parseProtocolParams(params)
        -> optional browser-modifier path
        -> openResourceReference(reference)
```

Managed reference resolution then prefers:

```text
current managed Resource
    -> portable fallback carried by newer managed backlink
    -> recovery snapshot
    -> user relink/alias
    -> failure with actionable error
```

Freeform references use `openFreeformReference()` and can be promoted back to a current managed Resource when a matching resource is found.

## 6. Normal resource-open chain

The current `openResourceAction()` behavior is layered.

### Project-note-aware video play

```text
runtime-entry.openResourceAction()
    -> decide whether project-note prompt is needed
    -> chooseStudyNote()
    -> optionally enter/exit Study Mode
    -> super.openResourceAction(...)
         |
         +--> entry.openResourceAction(...)
                  -> super.openResourceAction(...)
                       |
                       +--> main.openResourceAction(...)
                                -> launch web/file/Anki/OpenList/PotPlayer/URI target
                                -> markResourceStarted()
                                     -> mutate()
                                          -> persist()
                                -> render workbench
                  -> on successful video play, update activeMediaSession
    -> recordRecentStudy()
    -> persist()
    -> render workbench
```

The exact number of persistence/render operations can depend on the target path (for example, PotPlayer executable auto-detection can itself persist configuration). A later refactor should measure/collapse redundant work only after tests establish observable behavior.

### Paths that intentionally bypass the project-note prompt

Some continuation/resume code calls `super.openResourceAction(...)` directly from `runtime-entry.cjs` with `skipProjectNotePrompt`, so future work must not assume every resource launch enters through the full prompt path.

## 7. Positioned backlink playback

Managed backlink playback does not simply call the normal zero-position resource action.

`entry.openResourceReference()` resolves a position and calls:

```text
openPositionedPlayTarget(resource, target, playerTime)
    -> OpenList: resolve signed /d/ URL -> PotPlayer(position)
    -> PotPlayer target -> PotPlayer(position)
    -> supported legacy Bilibili URI -> canonical URL -> PotPlayer(position)
    -> markResourceStarted(resource)
```

On successful managed-reference playback it also updates the resource resume position, active media session, persists state and renders.

## 8. Persistence / data-safety chain

The base persistence contract is centralized in `main.cjs`:

```text
persist()
    -> assertSafePersist(this)
    -> reject if readOnlySafety
    -> calculate backup retention
    -> protectBeforePersist(this, retention)
    -> saveData(this.state)
    -> refreshPersistBaseline(this)
```

This ordering is data-safety critical.

Do not refactor persistence callers or state repositories in a way that bypasses this contract unless an equivalent safety contract is proven by tests.

## 9. Vault event chain after startup

Base `main.cjs` registers Vault callbacks during startup:

```text
rename -> this.handleVaultRename(...)
delete -> this.handleVaultDelete(...)
create -> this.handleVaultCreate(...)
```

Because dispatch remains virtual:

```text
runtime-entry.handleVaultRename/Delete/Create
    -> entry guard (ignore while lifecycle not ready)
    -> main Vault-reference behavior
    -> runtime project-note path/folder behavior
```

After project-note-specific changes, runtime may persist/render again.

## 10. Current architecture assessment boundary

This map does **not** conclude that the three-layer structure is "bad" or that Go Study should be rewritten.

What it does show:

- the architecture has evolved by adding behavior around a stable base;
- several important contracts rely on method-override order and dynamic dispatch;
- those relationships are harder to discover than explicit composition/service calls;
- maintenance risk will rise if future features continue adding new override layers without making lifecycle boundaries explicit.

The appropriate response is incremental evidence-driven refactoring, not a rewrite.

## 11. Refactor gate

Before any flattening/composition work is approved:

1. keep the 0.3.0 runtime frozen until owner acceptance is complete;
2. preserve this architecture map as the behavioral baseline;
3. add/maintain characterization tests for override-sensitive contracts;
4. choose one narrow seam at a time (settings or lifecycle are candidates);
5. keep runtime behavior unchanged in each structural PR;
6. require full CI plus Windows/Obsidian manual acceptance when the changed seam touches real integration behavior.

A rewrite-from-scratch is **not** the default plan.

## 12. Candidate later sequence (not yet approved implementation)

Possible order after release acceptance:

```text
A. make settings registration explicit
B. make startup/Vault lifecycle phases explicit
C. isolate persistence/state repository boundary
D. isolate playback adapters/services
E. reduce inheritance once callers are explicit
F. only then consider internal-name cleanup
```

Each step should be independently reversible and should avoid combining structural cleanup with new product features.


## Vault lifecycle coordination update (2026-09-13)

Vault rename/delete/create callbacks still dispatch virtually from the Base registration, but Runtime now owns the complete current-product event boundary. Base exposes `applyVaultRename`, `applyVaultDelete`, and `applyVaultCreate` mutation helpers. Runtime combines those Vault Ref mutations with Project Notes path/folder mutations inside `coordinateVaultLifecycleEvent()` and performs one persist/render after all mutations have completed.

The coordinator applies `_vaultLifecycleReady` to the **entire** event. Before layout readiness, neither Vault Ref nor Project Notes state is changed. If persistence fails after a changed event, both domains have already moved in the same direction in memory; the previous split path where one domain could be new while the other stayed old is removed.

The lower `entry.cjs` readiness overrides remain as defensive behavior for lower-layer/direct use, but the built Runtime path does not rely on `super.handleVaultRename/Delete/Create()` for current-product coordination.
