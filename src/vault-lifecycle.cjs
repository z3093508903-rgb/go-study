'use strict';

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
