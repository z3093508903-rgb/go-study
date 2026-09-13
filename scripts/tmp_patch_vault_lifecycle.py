from pathlib import Path

# New small coordinator: gate the whole event and persist once after all mutations.
coordinator = r'''\'use strict\';

async function coordinateVaultLifecycleEvent(plugin, mutate) {
  if (plugin?._vaultLifecycleReady === false) {
    return { skipped: true, changed: false, result: null };
  }
  if (typeof mutate !== 'function') throw new Error('Vault 生命周期协调器缺少状态更新函数。');
  const outcome = await mutate() || {};
  const changed = Boolean(outcome.changed);
  if (!changed) return { skipped: false, changed: false, result: outcome.result ?? null };
  await plugin.persist();
  await plugin.workbenchLeaf?.view?.render?.();
  return { skipped: false, changed: true, result: outcome.result ?? null };
}

module.exports = { coordinateVaultLifecycleEvent };
'''
Path('src/vault-lifecycle.cjs').write_text(coordinator, encoding='utf-8')

# Base layer: split pure-ish mutation from persistence wrappers.
p = Path('src/main.cjs')
s = p.read_text(encoding='utf-8')
old = r'''  async handleVaultRename(entry, oldPath) {
    const oldNormalized = model.normalizeVaultPath(oldPath);
    const newNormalized = model.normalizeVaultPath(entry.path);
    const refs = Object.values(this.state.vaultRefs || {}).filter((item) => !item.deletedAt && (model.normalizeVaultPath(item.path) === oldNormalized || model.normalizeVaultPath(item.path).startsWith(`${oldNormalized}/`)));
    if (!refs.length) return;
    for (const ref of refs) {
      const current = model.normalizeVaultPath(ref.path);
      const nextPath = current === oldNormalized ? newNormalized : `${newNormalized}${current.slice(oldNormalized.length)}`;
      model.updateVaultRefPath(this.state, ref.id, nextPath);
    }
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
  }

  async handleVaultDelete(entry) {
    const deletedPath = model.normalizeVaultPath(entry.path);
    const refs = Object.values(this.state.vaultRefs || {}).filter((item) => !item.deletedAt && (model.normalizeVaultPath(item.path) === deletedPath || model.normalizeVaultPath(item.path).startsWith(`${deletedPath}/`)));
    if (!refs.length) return;
    for (const ref of refs) model.markVaultRefMissing(this.state, ref.id);
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
  }

  async handleVaultCreate(entry) {
    const createdPath = model.normalizeVaultPath(entry.path);
    const ref = Object.values(this.state.vaultRefs || {}).find((item) => item.missingAt && model.normalizeVaultPath(item.path) === createdPath);
    if (!ref) return;
    model.restoreVaultRef(this.state, ref.id);
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
  }
'''
new = r'''  applyVaultRename(entry, oldPath) {
    const oldNormalized = model.normalizeVaultPath(oldPath);
    const newNormalized = model.normalizeVaultPath(entry.path);
    const refs = Object.values(this.state.vaultRefs || {}).filter((item) => !item.deletedAt && (model.normalizeVaultPath(item.path) === oldNormalized || model.normalizeVaultPath(item.path).startsWith(`${oldNormalized}/`)));
    if (!refs.length) return false;
    for (const ref of refs) {
      const current = model.normalizeVaultPath(ref.path);
      const nextPath = current === oldNormalized ? newNormalized : `${newNormalized}${current.slice(oldNormalized.length)}`;
      model.updateVaultRefPath(this.state, ref.id, nextPath);
    }
    return true;
  }

  async handleVaultRename(entry, oldPath) {
    const changed = this.applyVaultRename(entry, oldPath);
    if (!changed) return false;
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
    return true;
  }

  applyVaultDelete(entry) {
    const deletedPath = model.normalizeVaultPath(entry.path);
    const refs = Object.values(this.state.vaultRefs || {}).filter((item) => !item.deletedAt && (model.normalizeVaultPath(item.path) === deletedPath || model.normalizeVaultPath(item.path).startsWith(`${deletedPath}/`)));
    if (!refs.length) return false;
    for (const ref of refs) model.markVaultRefMissing(this.state, ref.id);
    return true;
  }

  async handleVaultDelete(entry) {
    const changed = this.applyVaultDelete(entry);
    if (!changed) return false;
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
    return true;
  }

  applyVaultCreate(entry) {
    const createdPath = model.normalizeVaultPath(entry.path);
    const ref = Object.values(this.state.vaultRefs || {}).find((item) => item.missingAt && model.normalizeVaultPath(item.path) === createdPath);
    if (!ref) return false;
    model.restoreVaultRef(this.state, ref.id);
    return true;
  }

  async handleVaultCreate(entry) {
    const changed = this.applyVaultCreate(entry);
    if (!changed) return false;
    await this.persist();
    await this.workbenchLeaf?.view?.render?.();
    return true;
  }
'''
assert old in s, 'base Vault handlers target not found'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# Runtime layer: coordinate both domains before one persist; gate the complete override.
p = Path('src/runtime-entry.cjs')
s = p.read_text(encoding='utf-8')
import_marker = "const { installTimelineNavigator } = require('./timeline-navigator.cjs');\n"
assert import_marker in s
s = s.replace(import_marker, import_marker + "const { coordinateVaultLifecycleEvent } = require('./vault-lifecycle.cjs');\n", 1)
old = r'''  async handleVaultRename(entry, oldPath) {
    const result = await super.handleVaultRename(entry, oldPath);
    const changedNotes = updateProjectNotePathsOnRename(this.state, oldPath, entry?.path);
    const changedFolders = updateProjectNoteFoldersOnRename(this.state, oldPath, entry?.path);
    if (changedNotes || changedFolders) {
      await this.persist();
      await this.workbenchLeaf?.view?.render?.();
    }
    return result;
  }

  async handleVaultDelete(entry) {
    const result = await super.handleVaultDelete(entry);
    const changedNotes = markProjectNotesMissing(this.state, entry?.path);
    const changedFolders = clearProjectNoteFoldersOnDelete(this.state, entry?.path);
    if (changedNotes || changedFolders) {
      await this.persist();
      await this.workbenchLeaf?.view?.render?.();
    }
    return result;
  }

  async handleVaultCreate(entry) {
    const result = await super.handleVaultCreate(entry);
    const changed = restoreProjectNotePath(this.state, entry?.path);
    if (changed) {
      await this.persist();
      await this.workbenchLeaf?.view?.render?.();
    }
    return result;
  }
'''
new = r'''  async handleVaultRename(entry, oldPath) {
    return coordinateVaultLifecycleEvent(this, () => {
      const changedRefs = this.applyVaultRename(entry, oldPath);
      const changedNotes = updateProjectNotePathsOnRename(this.state, oldPath, entry?.path);
      const changedFolders = updateProjectNoteFoldersOnRename(this.state, oldPath, entry?.path);
      return { changed: Boolean(changedRefs || changedNotes || changedFolders), result: changedRefs };
    });
  }

  async handleVaultDelete(entry) {
    return coordinateVaultLifecycleEvent(this, () => {
      const changedRefs = this.applyVaultDelete(entry);
      const changedNotes = markProjectNotesMissing(this.state, entry?.path);
      const changedFolders = clearProjectNoteFoldersOnDelete(this.state, entry?.path);
      return { changed: Boolean(changedRefs || changedNotes || changedFolders), result: changedRefs };
    });
  }

  async handleVaultCreate(entry) {
    return coordinateVaultLifecycleEvent(this, () => {
      const changedRefs = this.applyVaultCreate(entry);
      const changedNotes = restoreProjectNotePath(this.state, entry?.path);
      return { changed: Boolean(changedRefs || changedNotes), result: changedRefs };
    });
  }
'''
assert old in s, 'runtime Vault handlers target not found'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# True behavior tests for whole-event gate and one-persist coordination.
test_text = r'''\'use strict\';

const test = require('node:test');
const assert = require('node:assert/strict');
const { coordinateVaultLifecycleEvent } = require('../src/vault-lifecycle.cjs');

function pluginFixture() {
  return {
    _vaultLifecycleReady: true,
    persistCalls: 0,
    renderCalls: 0,
    async persist() { this.persistCalls += 1; },
    workbenchLeaf: { view: { render: async () => { this.renderCalls += 1; } } }
  };
}

test('Vault lifecycle coordinator skips the complete event before layout readiness', async () => {
  const plugin = pluginFixture();
  plugin._vaultLifecycleReady = false;
  let mutationCalls = 0;
  const result = await coordinateVaultLifecycleEvent(plugin, () => {
    mutationCalls += 1;
    return { changed: true };
  });
  assert.equal(result.skipped, true);
  assert.equal(mutationCalls, 0);
  assert.equal(plugin.persistCalls, 0);
});

test('one Vault event persists once after all domain mutations finish', async () => {
  const order = [];
  const plugin = pluginFixture();
  plugin.persist = async () => { plugin.persistCalls += 1; order.push('persist'); };
  const result = await coordinateVaultLifecycleEvent(plugin, () => {
    order.push('vaultRefs');
    order.push('projectNotes');
    return { changed: true, result: 'renamed' };
  });
  assert.equal(result.changed, true);
  assert.equal(plugin.persistCalls, 1);
  assert.deepEqual(order, ['vaultRefs', 'projectNotes', 'persist']);
});

test('persist failure happens only after both Vault domains are mutated', async () => {
  const state = { vaultRefPath: 'old', projectNotePath: 'old' };
  const plugin = pluginFixture();
  plugin.persist = async () => { plugin.persistCalls += 1; throw new Error('disk failed'); };
  await assert.rejects(() => coordinateVaultLifecycleEvent(plugin, () => {
    state.vaultRefPath = 'new';
    state.projectNotePath = 'new';
    return { changed: true };
  }), /disk failed/);
  assert.equal(plugin.persistCalls, 1);
  assert.deepEqual(state, { vaultRefPath: 'new', projectNotePath: 'new' });
});

test('unchanged Vault event does not persist', async () => {
  const plugin = pluginFixture();
  const result = await coordinateVaultLifecycleEvent(plugin, () => ({ changed: false }));
  assert.equal(result.changed, false);
  assert.equal(plugin.persistCalls, 0);
});
'''
Path('tests/vault-lifecycle.test.cjs').write_text(test_text, encoding='utf-8')

# Extend architecture characterization with the new explicit contract.
p = Path('tests/runtime-architecture-characterization.test.cjs')
s = p.read_text(encoding='utf-8')
addition = r'''

test('Runtime coordinates Vault reference and Project Note mutations before one persistence boundary', () => {
  const main = source('main.cjs');
  const runtime = source('runtime-entry.cjs');
  assert.match(main, /applyVaultRename\(entry, oldPath\)/);
  assert.match(main, /applyVaultDelete\(entry\)/);
  assert.match(main, /applyVaultCreate\(entry\)/);
  assert.match(runtime, /coordinateVaultLifecycleEvent\(this/);
  assert.match(runtime, /this\.applyVaultRename\(entry, oldPath\)/);
  assert.match(runtime, /updateProjectNotePathsOnRename/);
  assert.doesNotMatch(runtime, /super\.handleVaultRename\(entry, oldPath\)/);
});
'''
if "Runtime coordinates Vault reference and Project Note mutations" not in s:
    s += addition
p.write_text(s, encoding='utf-8')

# Document the updated runtime control flow.
p = Path('docs/ARCHITECTURE_RUNTIME_MAP.md')
s = p.read_text(encoding='utf-8')
addition = r'''

## Vault lifecycle coordination update (2026-09-13)

Vault rename/delete/create callbacks still dispatch virtually from the Base registration, but Runtime now owns the complete current-product event boundary. Base exposes `applyVaultRename`, `applyVaultDelete`, and `applyVaultCreate` mutation helpers. Runtime combines those Vault Ref mutations with Project Notes path/folder mutations inside `coordinateVaultLifecycleEvent()` and performs one persist/render after all mutations have completed.

The coordinator applies `_vaultLifecycleReady` to the **entire** event. Before layout readiness, neither Vault Ref nor Project Notes state is changed. If persistence fails after a changed event, both domains have already moved in the same direction in memory; the previous split path where one domain could be new while the other stayed old is removed.

The lower `entry.cjs` readiness overrides remain as defensive behavior for lower-layer/direct use, but the built Runtime path does not rely on `super.handleVaultRename/Delete/Create()` for current-product coordination.
'''
if "## Vault lifecycle coordination update (2026-09-13)" not in s:
    s += addition
p.write_text(s, encoding='utf-8')
