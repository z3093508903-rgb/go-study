# Go Study — Code ↔ Product Semantics Map

Status: human/agent collaboration reference.

Purpose: translate between **what the user/product means** and **where the behavior lives in code**. This is not a replacement for `docs/ARCHITECTURE_RUNTIME_MAP.md`; the runtime map explains call order and inheritance, while this document explains product meaning, ownership and modification boundaries.

When repository state conflicts with this document, repository state wins and this document should be updated in the same accepted work item.

---

## 1. Product vocabulary → domain/state/code

| Product term | Product meaning | Primary state / identity | Primary code | Important note |
| --- | --- | --- | --- | --- |
| **Project / 学习项目** | A learning goal/workspace that groups modules, notes, files, tasks and resources | `state.projects` | `src/model.cjs`, `src/main.cjs` | Project is the top-level learning context, not a filesystem folder. |
| **Module / 学习模块** | A project-local section that organizes resources on the project board | `state.modules`, resource membership | `src/model.cjs`, `src/main.cjs` | Do not confuse Module with external content provider/source. |
| **Resource / 学习资源** | A reusable learning object such as video, PDF, file, web page or Anki deck | `state.resources` | `src/model.cjs`, `src/main.cjs`, `src/resource-locator.cjs` | A Resource has stable managed identity inside Go Study. |
| **Source / 来源连接** | Configuration for an external provider/service, e.g. OpenList or Anki | `state.sources` | `src/model.cjs`, `src/main.cjs` | A Source is a provider/configuration, not an individual Resource. |
| **Vault Ref / 项目文件关联** | A reference from a project to an Obsidian Vault file/folder | `state.vaultRefs` | `src/model.cjs`, `src/main.cjs` | Go Study tracks references; it should not silently delete user files. |
| **Project Note / 笔记盒中的笔记** | Markdown note explicitly associated with a project and usable for study/capture | `state.projectNotes`, project `noteFolder` | `src/project-notes.cjs`, `src/project-notes-ui.cjs` | “笔记盒” is association/navigation over real Markdown, not a private note database. |
| **Managed media** | Media already represented by a Go Study Resource | Resource ID + resource locator/action | `src/resource-reference.cjs`, `src/resource-resolver.cjs`, `src/entry.cjs` | Current managed backlink wire format is presently `v=3`; this is a protocol label, not a product generation number. |
| **Freeform media** | Local/portable/web media currently being studied without requiring a stored Resource | media locator + name/web/title | `src/media-session.cjs`, `src/freeform-playback.cjs`, `src/resource-reference.cjs`, `src/bilibili-metadata.cjs` | Current Freeform backlink wire format is presently `v=2`; it is **current**, not “old v2”. Bilibili BV-only machine labels may be enriched to a human title without changing Resource/project membership. |
| **Resume / 继续位置** | Last known learning/playback position for a managed Resource | resource `resume.position` | `src/resource-resolver.cjs`, `src/learning-capture.cjs`, `src/entry.cjs` | Resume state is product state; opening a positioned link may update it. |
| **Active Media Session** | Runtime knowledge of the media currently being learned | runtime `plugin.activeMediaSession` | `src/entry.cjs`, `src/media-session.cjs`, `src/learning-capture.cjs` | Ephemeral runtime context; not the same as persisted Resource identity. |
| **Continue Learning / 继续学习** | Reopen the most recent project resource/note and resume when possible | `uiState.recentStudyByProject` + Resource resume | `src/project-notes.cjs`, `src/runtime-entry.cjs`, `src/learning-controls-ui.cjs` | Crosses project notes, resource playback and persisted recent-study state. |
| **Companion** | Lightweight separate Markdown window using real Obsidian Markdown | Companion UI/runtime state + real Vault file | `src/companion-note-window.cjs`, `src/companion-events.cjs` | Companion is a window/surface, not a separate note format. |
| **Study Mode / 学习模式** | Locks a chosen note/context for focused learning and capture | `uiState.studyMode` + Companion state | `src/study-mode.cjs`, `src/runtime-entry.cjs` | Can represent managed, Freeform or note-only study context. |
| **Capture Target / 记录目标** | Markdown editor/file that Alt+S and capture actions should write into | runtime remembered/Companion target | `src/note-target.cjs` | Resolution priority includes locked Companion, active editor and remembered editor. |
| **Capture / 快捷记录** | Insert timestamp, note, screenshot or combinations into Markdown | Markdown content + optional Resource resume | `src/learning-capture.cjs`, `src/resource-note.cjs`, `src/capture-actions.cjs` | Capture is a workflow spanning player state, note target, output template and persistence. |
| **HUD / 动作盘** | Alt+S interaction for choosing capture actions | product settings + runtime UI | `src/action-hud.cjs`, `src/immersive-hotkeys.cjs`, `src/capture-actions.cjs` | Shortcut handling and action definitions are separate concerns. |
| **Timeline** | Lightweight visualization/navigation of timestamps already present in notes | derived from Markdown/current UI | `src/timeline-navigator.cjs` | Timeline is not authoritative playback state and not a second video player. |
| **Bilibili Web Bridge** | Optional browser-extension → localhost bridge exposing current Bilibili playback state | transient bridge state | `src/bilibili-web-bridge.cjs`, `browser-extension/bilibili-bridge/**` | Browser transport integration; native Bilibili `?t=` links are not Go Study protocol links. |
| **PotPlayer integration** | Launch/query/control Windows PotPlayer for local/OpenList/video learning | executable config + runtime media state | `src/native-potplayer.cjs`, `src/potplayer-bridge.cjs`, `src/main.cjs`, `src/entry.cjs` | Native launch, older bridge query path and product playback orchestration are separate layers. |
| **OpenList** | User-configured remote file source whose playable URLs may be signed and opened in PotPlayer | `state.sources` + Resource locator metadata | `src/main.cjs`, `src/resource-locator.cjs`, `src/resource-relink.cjs` | Missing/unmounted backing storage must fail visibly; no speculative unsigned fallback. |
| **Legacy JV Compatibility** | Optional input-only support for historical `jv://open?...` links | `uiState.legacyJvCompatibilityEnabled` | `src/legacy-jv.cjs`, `src/main.cjs`, `src/product-settings.cjs` | Separate from Go Study v2/v3 protocol. New notes never output JV. |
| **Settings / 设置** | User-facing control of product behavior, templates, PotPlayer path, capture, compatibility, etc. | mostly `state.uiState` | `src/product-settings.cjs`, `src/product-settings-tab.cjs`, `src/runtime-entry.cjs` | Runtime currently intercepts the older base settings-tab registration; see runtime architecture map. |
| **State safety / 数据保护** | Prevent accidental destructive save; preserve recovery copies | plugin `data.json` + `.obsidian/go-study-recovery` | `src/state-safety.cjs`, `src/main.cjs` | `persist()` safety ordering is a critical contract. |
| **Backup / Restore** | User-visible manual/named/automatic recovery of plugin state | recovery JSON files | `src/state-safety.cjs`, `src/main.cjs`, product settings | Backup retention and restore safety are product behavior, not only developer tooling. |
| **Preview → Stable migration** | One-time safe import from `go-study-preview` when Stable has no meaningful data | Preview `data.json` → Stable state + recovery snapshot | `src/state-safety.cjs`, `src/main.cjs` | Preview data stays untouched; do not treat old plugin identity as general recovery source. |

---

## 2. Source module → product responsibility

| File / area | Product responsibility | Role type | Must co-review with |
| --- | --- | --- | --- |
| `src/main.cjs` | Base workbench, project/resource UI, state load/persist, Vault refs, core launch actions, OpenList/Bilibili/Anki base behavior | **base/orchestration + legacy core** | `src/entry.cjs`, `src/runtime-entry.cjs`, `src/model.cjs`, data-safety tests |
| `src/entry.cjs` | Go Study protocol registration, backlink opening/fallback/relink, positioned playback, active media session, deferred Vault lifecycle | **runtime hardening/orchestration** | `resource-reference`, `resource-resolver`, `reference-*`, `freeform-playback`, runtime map |
| `src/runtime-entry.cjs` | Product settings substitution, Project Notes-aware launch, Continue Learning, Study Mode, Companion/Timeline/HUD registrations | **product enhancement/orchestration** | `entry.cjs`, project-note modules, settings, study mode, runtime map |
| `src/model.cjs` | Domain state model and most pure project/module/resource/layout operations | **domain model** | schema/state tests, `main.cjs` callers |
| `src/resource-locator.cjs` | Stable/canonical resource location metadata and OpenList/resource identity helpers | **domain adapter** | `model.cjs`, Resource import/relink code |
| `src/resource-reference.cjs` | Go Study backlink wire parsing/building and input validation | **protocol boundary** | `resource-note`, `entry`, compatibility tests, README compatibility policy |
| `src/resource-note.cjs` | Convert learning context into Markdown timestamps/notes/captures using templates | **output formatting** | `learning-capture`, product settings, protocol builder |
| `src/resource-resolver.cjs` | Resolve managed Resource + position into playback target/time and update resume | **playback domain logic** | `entry`, Resource actions/model |
| `src/reference-fallback.cjs` | Managed-link current Resource lookup, portable fallback, recovery snapshot lookup/browser source | **compat/recovery** | `entry`, state-safety/recovery semantics |
| `src/reference-relink-ui.cjs` | UI for reconnecting a broken managed backlink to a current Resource | **recovery UI** | `entry`, reference fallback |
| `src/resource-relink.cjs` / `src/resource-relink-ui.cjs` | Relink moved OpenList/resource paths and safe folder remap | **resource recovery** | OpenList/resource locator/model |
| `src/media-session.cjs` | Resolve player/browser media into managed vs Freeform learning context | **media identity** | `learning-capture`, Bilibili/PotPlayer inputs |
| `src/freeform-playback.cjs` | Open unregistered/portable media and apply position when supported | **playback adapter** | `entry`, native PotPlayer, protocol Freeform semantics |
| `src/native-potplayer.cjs` | Windows-native PotPlayer discovery/launch/query boundary | **OS/player adapter** | `main`, `learning-capture`, security tests |
| `src/potplayer-bridge.cjs` | PotPlayer bridge request compatibility/query path | **player integration adapter** | `learning-capture` |
| `src/bilibili-web-bridge.cjs` | Localhost bridge listener, Bilibili state normalization and timestamp helpers | **browser integration adapter** | browser extension, `learning-capture`, bridge tests |
| `src/bilibili-metadata.cjs` | Detect BV-only machine labels, best-effort resolve/cache human Bilibili titles for Freeform media | **metadata adapter** | `learning-capture`, Timeline, Bilibili bridge state |
| `browser-extension/bilibili-bridge/**` | Read current Bilibili `<video>` state and POST to local Go Study Bridge | **browser-side adapter** | `bilibili-web-bridge.cjs`, privacy/security docs |
| `src/learning-capture.cjs` | End-to-end capture workflow: resolve player/context/target, generate Markdown, screenshots, persist resume | **workflow orchestration** | media session, note target, resource-note, player bridges, settings |
| `src/capture-actions.cjs` | Capture action definitions/default HUD slots/normalization | **action model** | HUD/hotkeys/settings |
| `src/action-hud.cjs` | Visual action chooser/HUD behavior | **interaction UI** | immersive hotkeys, capture actions |
| `src/immersive-hotkeys.cjs` | Global/foreground shortcut handling and routing into capture actions | **input integration** | HUD, learning capture, product settings |
| `src/note-target.cjs` | Remember and resolve the Markdown editor/file that receives capture output | **editor-target service** | Companion, learning capture |
| `src/companion-note-window.cjs` | Open/manage actual Companion Markdown window, top-most/lock/layout/editor behavior | **window/UI integration** | study mode, note target, companion events |
| `src/companion-events.cjs` | Companion-related event/focus/window coordination | **window event integration** | Companion implementation |
| `src/study-mode.cjs` | Persist/enter/exit focused study context and coordinate locked Companion | **workflow state** | runtime entry, Companion, project notes |
| `src/project-notes.cjs` | Project-note associations, note folders, recent note/study state, Vault path lifecycle | **domain state** | project-notes UI, runtime Vault event overrides |
| `src/project-notes-ui.cjs` | Choose/open/manage project notes and Project Notes entry points | **product UI** | project-notes state, runtime entry |
| `src/learning-controls-ui.cjs` | Project/workbench learning controls such as Continue Learning | **product UI enhancement** | project notes, runtime entry |
| `src/timeline-navigator.cjs` | Build lightweight timestamp navigation over Markdown | **derived UI** | resource link format/Markdown parsing |
| `src/product-settings.cjs` | Defaults/normalization/persistence rules for product settings and output templates | **settings model** | settings tab, capture, runtime entry |
| `src/product-settings-tab.cjs` | User-facing settings interface | **settings UI** | product-settings, runtime settings interception |
| `src/state-safety.cjs` | Recovery snapshots, catastrophic-drop guard, Preview migration candidate/protection | **data-safety boundary** | `main.persist/onload`, backup/restore tests |
| `src/legacy-jv.cjs` | Parse optional historical `jv://open` input into current Freeform runtime shape | **explicit legacy adapter** | product setting, main URI launch path |
| `src/anki-launch.cjs` / `src/release-hardening.cjs` | Anki/native integration and release-era runtime hardening helpers | **integration/hardening** | main/entry and integration tests |
| `src/ui-fixes.cjs` / `src/usage-polish.cjs` | Scoped UI corrections and interaction polish | **UI support** | affected UI surface tests |
| `styles.css` | Product visual layout/classes, including historical `rh-next-*` internal selectors | **presentation** | corresponding DOM rendering code/tests |
| `build.mjs` | Bundle source modules from runtime entry into committed `main.js` | **build infrastructure** | generated `main.js`, bundle tests |
| `scripts/check-release.mjs` | Validate release identity/files/secrets/version consistency | **release gate** | manifest/package/workflows |
| `.github/workflows/ci.yml` | Build/test/release-check and committed bundle drift detection | **CI gate** | package scripts |
| `.github/workflows/release.yml` | Tag-driven package/release assembly | **release packaging** | release notes + distribution policy |

---

## 3. Human request → first files an Agent should inspect

| Human/product request | First inspection targets | Why |
| --- | --- | --- |
| “改项目页 / 学习模块 / 资源卡片” | `src/main.cjs`, `src/model.cjs`, `styles.css` | Base workbench DOM/layout and domain model live here. |
| “笔记盒不见了 / 项目笔记有问题” | `src/project-notes.cjs`, `src/project-notes-ui.cjs`, `src/runtime-entry.cjs` | Data association, UI entry and runtime injection are split. |
| “继续学习不对” | `src/project-notes.cjs`, `src/runtime-entry.cjs`, `src/learning-controls-ui.cjs`, `src/resource-resolver.cjs` | Recent project context and playback resume cross several modules. |
| “时间戳生成/点击不对” | `src/resource-reference.cjs`, `src/resource-note.cjs`, `src/entry.cjs`, `src/resource-resolver.cjs` | Wire format, Markdown generation, protocol handler and playback resolution are distinct. |
| “本地临时视频笔记不工作” | `src/media-session.cjs`, `src/freeform-playback.cjs`, `src/learning-capture.cjs`, `src/resource-reference.cjs` | This is the Freeform workflow, not ordinary managed Resource playback. |
| “PotPlayer 打不开/跳转时间不对” | `src/native-potplayer.cjs`, `src/main.cjs`, `src/entry.cjs`, `src/resource-resolver.cjs` | OS launch and product playback orchestration are separate. |
| “OpenList 视频打不开” | `src/main.cjs`, `src/resource-locator.cjs`, `src/resource-relink.cjs`, `src/entry.cjs` | Source auth/path/signing and positioned playback cross layers. |
| “B站网页 Alt+S 不工作” | `browser-extension/bilibili-bridge/**`, `src/bilibili-web-bridge.cjs`, `src/learning-capture.cjs`, `src/immersive-hotkeys.cjs` | Browser state transport and capture are separate systems. |
| “Companion 小窗/置顶/焦点有问题” | `src/companion-note-window.cjs`, `src/companion-events.cjs`, `src/note-target.cjs`, `src/study-mode.cjs` | Window lifecycle, target editor and Study Mode interact. |
| “Alt+S / 动作盘有问题” | `src/immersive-hotkeys.cjs`, `src/action-hud.cjs`, `src/capture-actions.cjs`, `src/learning-capture.cjs` | Input, UI, action model and execution are intentionally split. |
| “设置页改了没效果” | `src/product-settings.cjs`, `src/product-settings-tab.cjs`, `src/runtime-entry.cjs`, `docs/ARCHITECTURE_RUNTIME_MAP.md` | Base settings registration is intercepted at runtime. |
| “Vault 重命名/删除后关联错了” | `src/main.cjs`, `src/entry.cjs`, `src/runtime-entry.cjs`, `src/project-notes.cjs` | Vault event handling uses layered dynamic dispatch. |
| “data.json 丢了/恢复/迁移” | `src/state-safety.cjs`, `src/main.cjs` | Treat as data-safety work; do not patch UI first. |
| “要改旧链接兼容” | `src/resource-reference.cjs`, `src/legacy-jv.cjs`, `README.md`, compatibility tests | Compatibility is a product policy, not just parser cleanup. |
| “想重构架构” | `docs/ARCHITECTURE_RUNTIME_MAP.md`, runtime characterization tests, `main/entry/runtime-entry` | Preserve behavior before changing structure. |

---

## 4. Protocol semantics: do not read v2/v3 as old/new

Current product meaning is family-based:

```text
Managed Resource backlink  -> current wire label v3
Freeform media backlink    -> current wire label v2
Legacy JV input            -> separate gated adapter
```

Therefore:

- **v3 does not supersede Freeform v2**;
- Freeform v2 is a current format, not a historical compatibility branch;
- “Managed” and “Freeform” are the useful product semantics;
- numeric labels are implementation/wire details and should not be used as the main human-facing vocabulary.

A dedicated future protocol-design task should make family/revision semantics clearer. Do not change existing link wire format as incidental cleanup.

---

## 5. Historical/internal names that do not define product semantics

| Internal/historical identifier | Product meaning today |
| --- | --- |
| `ResourceHubNextPlugin`, `ResourceHubNextView`, `ResourceHubNextRuntimePlugin` | Internal class names for the current Go Study runtime layers |
| `rh-next-*` CSS classes | Internal presentation selectors used by Go Study |
| `learning-resource-hub-next` | Previous plugin identity used only where explicit conflict/history handling remains |
| `go-study-preview` | Preview identity used for controlled migration/recovery/coexistence logic |

Do not infer that a historical internal name means the corresponding old product is still supported.

---

## 6. Collaboration rule for future modules

When adding a meaningful product feature or subsystem, update this map in the same accepted work item if any of the following changes:

- a new product term/concept appears;
- ownership of an existing feature moves to a different module;
- a new persistent state key becomes part of product behavior;
- a new adapter/provider/player/browser integration is added;
- a compatibility surface is added or removed;
- a file becomes a required co-review target for a common user-facing change.

The goal is not to document every helper function. The goal is that a new human or Agent can translate **product intent → correct code surface** without relying on old chat history.
