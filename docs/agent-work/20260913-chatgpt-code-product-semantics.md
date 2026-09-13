# Work Record — 20260913-chatgpt-code-product-semantics

- Status: `ready_for_review`
- Agent: ChatGPT
- Branch: `work/20260913-chatgpt-code-product-semantics`
- Base: `main@60e1f454de7afb70b8eb9b2b3f7294db76b7b92a`
- Started: 2026-09-13 (UTC+8)
- Updated: 2026-09-13 (UTC+8)

## Goal

Create a durable human/agent collaboration reference that maps product language and user-visible capabilities to the source files/modules that implement them.

Also record that current protocol labels `v2` and `v3` are implementation/version labels, not product-facing semantic names, and that future protocol naming should favor semantic families over a misleading linear-version impression.

## Exact writable file scope

Actual writes:

- `docs/CODE_PRODUCT_SEMANTICS.md` (new)
- `AGENTS.md`
- this work record

### Scope decision

`docs/ROADMAP.md` was originally allowed for protocol semantic naming cleanup, but that decision is being recorded by the separate `20260913-chatgpt-drop-v1-backlinks` work item to avoid overlapping edits. This work item does not edit the roadmap.

## Do not touch

Preserved:

- `src/**`
- `tests/**`
- `main.js`
- manifest/package versions
- state/schema/migration behavior
- protocol parser behavior

## What was added

`docs/CODE_PRODUCT_SEMANTICS.md` now provides four collaboration views:

1. product term -> meaning/state/code ownership;
2. source module -> product responsibility / role / required co-review surfaces;
3. common human request -> first files an Agent should inspect;
4. protocol and historical-name semantics so numeric versions/internal names are not mistaken for product generations.

Covered areas include projects/modules/resources/sources, Vault refs, Project Notes, managed/freeform media, resume/session state, Continue Learning, Companion, Study Mode, capture target, HUD/capture, Timeline, Bilibili Bridge, PotPlayer, OpenList, JV compatibility, settings, state safety, backups, Preview migration, build and release infrastructure.

`AGENTS.md` now requires Agents to read the product-semantics map before implementation and to update it when accepted work changes ownership/meaning of a product concept.

## Compatibility / data impact

- Runtime impact: none.
- State/schema impact: none.
- Migration impact: none.
- Backlink protocol impact: none.
- Documentation semantics intentionally describe Managed/Freeform as the useful product families; protocol wire labels remain implementation details.

## Validation

- [PASS] Mapping is based on current source/modules and the merged runtime architecture map, not chat-only history.
- [PASS] Human-request lookup table covers the main user-facing troubleshooting/change requests.
- [PASS] Historical/internal identifiers are explicitly separated from current product semantics.
- [PASS] No runtime/source/test/generated files changed.
- [UNRUN] Runtime tests — documentation-only work item.

## Rollback

Revert this work item/PR; there is no runtime or user-data impact.

## Remaining dependency

The separate v1-removal work item is intentionally responsible for making runtime compatibility match the simplified protocol semantics. Prefer merging/validating that protocol change before treating this document as the final compatibility truth on `main`.

## Handoff

Review the mapping for clarity and completeness, then merge after or alongside the validated protocol cleanup. Future feature work should update the map whenever product ownership or semantics move.
