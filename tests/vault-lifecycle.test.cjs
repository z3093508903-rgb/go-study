'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { coordinateVaultLifecycleEvent } = require('../src/vault-lifecycle.cjs');

function pluginFixture() {
  return {
    _vaultLifecycleReady: true,
    persistCalls: 0,
    renderCalls: 0,
    async persist() { this.persistCalls += 1; },
    workbenchLeaf: { view: { render: async () => {} } }
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
