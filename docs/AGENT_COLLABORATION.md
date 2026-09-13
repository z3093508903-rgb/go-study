# Go Study — Multi-Agent Collaboration Protocol

This file defines the repository-wide collaboration contract for ChatGPT, Codex, and any other coding/review agents working on Go Study.

The purpose is not bureaucracy. It is to prevent silent overlap, stale assumptions, accidental schema changes, generated-file drift, and handoff loss when several agents work at the same time.

## 1. Repository roles

### Engineering source repository

`z3093508903-rgb/go-study` is the owner's development / engineering source repository.

It is the source of truth for current development decisions, code, tests, migration behavior, and agent handoff records.

### Distribution repository

Public distribution may be performed from a separate repository chosen by the owner.

Until that repository is explicitly named in this file or `docs/HANDOFF_CURRENT.md`:

- do not infer a distribution repository;
- do not assume GitHub Releases in this development repository are the final public distribution state;
- do not publish, tag, mirror, or sync to another repository without an explicit owner instruction.

Historical or internal names may remain in the engineering repository when they do not affect product identity or runtime correctness.

## 2. Read before work

Before changing anything, read in this order:

1. `/AGENTS.md`
2. `/docs/HANDOFF_CURRENT.md`
3. `/docs/AGENT_COLLABORATION.md`
4. the active work records relevant to the same files/feature
5. the code, tests, and docs directly relevant to the task

Repository state is authoritative. Do not rely on chat memory when it disagrees with the repository.

## 3. One task = one work_id = one branch

Every modification task must have a `work_id` before implementation begins.

Recommended format:

`YYYYMMDD-<agent>-<short-task>`

Example:

`20260913-codex-bilibili-bridge-auth`

Use a dedicated branch:

`work/<work_id>`

Do not write directly to `main` for normal feature, fix, refactor, migration, release-engineering, or documentation work.

Small emergency owner-directed edits may be exempted only when the owner explicitly asks for a direct `main` edit.

## 4. Register scope before editing

Create one work record:

`docs/agent-work/<work_id>.md`

before changing implementation files.

The record must contain at least:

- status;
- agent;
- branch;
- base branch / base SHA;
- goal;
- exact writable file scope;
- explicit do-not-touch scope;
- dependencies / blockers;
- compatibility and data/schema impact;
- validation plan.

The exact file scope is an ownership claim for that work item.

If another active work item already claims the same file or tightly coupled behavior, do not silently edit it. Either:

1. split the file/feature boundary cleanly;
2. coordinate by updating both work records; or
3. stop and leave the task blocked for integration.

## 5. Keep overlap small

Prefer small, reviewable work items.

Avoid one agent simultaneously owning unrelated areas such as:

- runtime behavior;
- migration/state schema;
- UI restyling;
- release workflow;
- documentation cleanup.

Large refactors must state why the wider scope is necessary.

Do not perform opportunistic cleanup outside the registered scope just because you noticed it.

## 6. State, schema, migration, and compatibility changes are special

Any change that can affect existing user data or old links must explicitly record:

- state/schema impact;
- migration direction;
- downgrade/rollback behavior;
- old-version compatibility behavior;
- whether the change is additive, destructive, or irreversible.

Never silently delete compatibility behavior.

Never silently add a new long-term compatibility promise either.

For compatibility code, document:

- what historical input is accepted;
- whether new output still generates that format;
- why compatibility exists;
- the removal condition, if any.

## 7. Generated files

`main.js` is generated from `src/**` and is committed in this repository.

If a work item changes bundled runtime source that affects `main.js`, the same work item owns the required rebuild/update unless the handoff explicitly delegates it.

Never treat a generated-file diff as an unrelated cleanup.

Do not hand-edit generated `main.js` to implement runtime behavior that belongs in `src/**`.

## 8. Testing language is standardized

Every completed work record must report validation using these exact markers:

- `[PASS]` — executed and passed;
- `[FAIL]` — executed and failed;
- `[UNRUN]` — not executed, with a reason;
- `[MANUAL REQUIRED]` — requires owner/real-machine acceptance.

Do not write vague statements such as “should work”, “looks fine”, or “probably fixed” as substitutes for test status.

For Windows/Obsidian integration, automated tests do not replace real-machine acceptance when the behavior depends on:

- PotPlayer;
- OpenList/mounted storage;
- Companion/native windows;
- global shortcuts;
- browser bridge;
- backup/restore;
- Preview -> Stable migration.

## 9. Required completion record

Before marking a work item `ready_for_review` or `complete`, update its work record with:

- final status;
- commits;
- files actually changed;
- decisions made;
- tests with `[PASS]`, `[FAIL]`, `[UNRUN]`, or `[MANUAL REQUIRED]`;
- state/schema impact;
- compatibility impact;
- rollback point / rollback method;
- remaining risks;
- exact next step for the next agent or owner.

If planned scope changed, record the deviation.

## 10. When to update HANDOFF_CURRENT.md

`docs/HANDOFF_CURRENT.md` is the project baseline summary, not a live scratchpad for every agent action.

Update it only when a merged/accepted task changes one of these:

- current release state;
- canonical architecture/baseline;
- migration or compatibility policy;
- known release blocker;
- repository role;
- major product decision;
- next required owner acceptance step.

Routine implementation details stay in the individual work record.

This reduces merge conflicts between concurrent agents.

## 11. Pull request / integration expectations

Normal path:

`main -> work/<work_id> -> tests/review -> PR -> main`

A PR or integration handoff should answer:

1. What changed?
2. Why was it necessary?
3. What did not change?
4. What was tested?
5. What still requires manual acceptance?
6. Does it alter data/schema/migration/compatibility?
7. How can it be rolled back?

Do not mix unrelated work_ids into one PR unless an integration agent explicitly owns the merge task.

## 12. Conflict rule

If repository state, another agent's work record, and chat instructions appear inconsistent:

1. preserve user data and current working behavior first;
2. do not guess at destructive intent;
3. record the conflict in the work item;
4. use the newest explicit owner instruction as the product decision;
5. update repository documentation so the contradiction does not survive into the next handoff.

## 13. Security and secrets

Never commit:

- real `data.json`;
- Vault content;
- credentials;
- cookies;
- API keys;
- bridge authentication tokens;
- personal backups;
- real OpenList secrets.

Examples and fixtures must use synthetic values.

## 14. Definition of a good handoff

A new agent should be able to answer, without reading old chats:

- what branch is current;
- what work is active;
- which files are owned by whom;
- what is safe to modify;
- what decisions are already settled;
- what tests passed or were not run;
- what could affect user data;
- what the next concrete action is.

If the repository cannot answer those questions, the handoff is incomplete.
