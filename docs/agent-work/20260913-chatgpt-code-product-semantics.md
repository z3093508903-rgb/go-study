# Work Record — 20260913-chatgpt-code-product-semantics

- Status: `in_progress`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-code-product-semantics`
- Base: `main@60e1f454de7afb70b8eb9b2b3f7294db76b7b92a`
- Started: 2026-09-13 (UTC+8)

## Goal

Create a durable human/agent collaboration reference that maps product language and user-visible capabilities to the source files/modules that implement them.

Also record that current protocol labels `v2` and `v3` are implementation/version labels, not product-facing semantic names, and that future protocol naming should favor semantic families over a misleading linear-version impression.

## Exact writable file scope

- `docs/CODE_PRODUCT_SEMANTICS.md` (new)
- `AGENTS.md` (navigation/required reading only if useful)
- `docs/ROADMAP.md` (protocol semantic naming cleanup only)
- this work record

## Do not touch

- `src/**`
- `tests/**`
- `main.js`
- manifest/package versions
- state/schema/migration behavior
- protocol parser behavior

## Compatibility / data impact

None. Documentation only.

## Validation plan

Base mappings on current source. Cover workbench/projects/resources, local/PotPlayer, OpenList, Bilibili, Companion, Study Mode, HUD/capture, timestamps/backlinks, Timeline, Vault/project notes, settings, state safety/backups, Preview migration, legacy compatibility, and release/build infrastructure. Clearly distinguish product terms from internal/historical names and cross-reference `docs/ARCHITECTURE_RUNTIME_MAP.md` for deep call flow.

## Rollback

Delete/revert the documentation-only changes.

## Test log

- [UNRUN] documentation review — document not written yet.
