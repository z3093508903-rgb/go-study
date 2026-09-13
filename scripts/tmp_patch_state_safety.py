from pathlib import Path

# state-safety: only mark raw as protected after snapshot success, expose failure, and keep retries possible.
p = Path('src/state-safety.cjs')
s = p.read_text(encoding='utf-8')
old = """function protectBeforePersist(plugin, keep = 10) {\n  const safety = plugin?._goStudyStateSafety || (plugin._goStudyStateSafety = {});\n  const raw = readRawPluginData(plugin);\n  if (!raw.raw) return { protected: false, recoveryPath: '' };\n  if (raw.raw === safety.lastProtectedRaw) return { protected: false, recoveryPath: '' };\n  const protectedRaw = protectRawPluginData(plugin, 'before-save');\n  if (protectedRaw.raw) safety.lastProtectedRaw = protectedRaw.raw;\n  pruneRecoveryBackups(plugin, keep);\n  return { protected: Boolean(protectedRaw.recoveryPath), recoveryPath: protectedRaw.recoveryPath || '' };\n}\n"""
new = """function protectBeforePersist(plugin, keep = 10) {\n  const safety = plugin?._goStudyStateSafety || (plugin._goStudyStateSafety = {});\n  const raw = readRawPluginData(plugin);\n  if (!raw.raw) return { protected: false, recoveryPath: '', protectionError: null };\n  if (raw.raw === safety.lastProtectedRaw) return { protected: false, recoveryPath: '', protectionError: null };\n  const protectedRaw = protectRawPluginData(plugin, 'before-save');\n  const protectedOk = Boolean(protectedRaw.recoveryPath);\n  const protectionError = protectedOk\n    ? null\n    : (protectedRaw.protectionError || new Error('Go Study 无法创建保存前恢复快照。'));\n  if (protectedOk) {\n    safety.lastProtectedRaw = protectedRaw.raw;\n    safety.lastProtectionError = null;\n    safety.protectionDegraded = false;\n    pruneRecoveryBackups(plugin, keep);\n  } else {\n    safety.lastProtectionError = protectionError;\n    safety.protectionDegraded = true;\n  }\n  return { protected: protectedOk, recoveryPath: protectedRaw.recoveryPath || '', protectionError };\n}\n\nfunction requireRecoverySnapshot(result, operation = '高风险操作') {\n  if (result?.recoveryPath) return result;\n  const cause = result?.protectionError || result?.error || null;\n  const error = new Error(`Go Study 无法为${String(operation || '高风险操作')}创建保护快照，已停止操作。`);\n  if (cause) error.cause = cause;\n  error.code = 'GO_STUDY_RECOVERY_REQUIRED';\n  throw error;\n}\n"""
assert old in s, 'protectBeforePersist target not found'
s = s.replace(old, new, 1)
s = s.replace("  protectRawPluginData,\n", "  protectRawPluginData,\n  requireRecoverySnapshot,\n", 1)
p.write_text(s, encoding='utf-8')

# main: surface degraded ordinary-save protection; require migration and restore snapshots.
p = Path('src/main.cjs')
s = p.read_text(encoding='utf-8')
s = s.replace("  readRawPluginData,\n", "  readRawPluginData,\n  requireRecoverySnapshot,\n", 1)

old_migration = """      if (candidate.eligible) {\n        const protectedMigration = protectPreviewMigration(this, candidate);\n        loaded = candidate.data;\n        previewMigration = {\n          sourcePluginId: candidate.pluginId,\n          sourcePath: candidate.filePath,\n          recoveryPath: protectedMigration.recoveryPath || ''\n        };\n      }\n"""
new_migration = """      if (candidate.eligible) {\n        const protectedMigration = protectPreviewMigration(this, candidate);\n        try {\n          requireRecoverySnapshot(protectedMigration, 'Preview 迁移');\n          loaded = candidate.data;\n          previewMigration = {\n            sourcePluginId: candidate.pluginId,\n            sourcePath: candidate.filePath,\n            recoveryPath: protectedMigration.recoveryPath\n          };\n        } catch (error) {\n          console.error('Go Study: Preview migration safety snapshot failed; loading Preview read-only.', error);\n          loaded = candidate.data;\n          this._goStudyStateSafety.readOnlySafety = true;\n          new Notice('Go Study 无法创建 Preview 迁移保护快照，已只读加载 Preview 数据并停止迁移写入。请先检查 Vault 写入权限或磁盘状态。', 12000);\n        }\n      }\n"""
assert old_migration in s, 'preview migration target not found'
s = s.replace(old_migration, new_migration, 1)

old_persist = """    const retention = Math.max(3, Math.min(10, Number(this.state?.uiState?.backupRetention || 10)));\n    protectBeforePersist(this, retention);\n    await this.saveData(this.state);\n    refreshPersistBaseline(this);\n"""
new_persist = """    const retention = Math.max(3, Math.min(10, Number(this.state?.uiState?.backupRetention || 10)));\n    const protection = protectBeforePersist(this, retention);\n    if (protection.protectionError) {\n      console.warn('Go Study: pre-save recovery snapshot failed; continuing ordinary save with degraded protection.', protection.protectionError);\n    }\n    await this.saveData(this.state);\n    refreshPersistBaseline(this);\n    return { protection };\n"""
assert old_persist in s, 'persist target not found'
s = s.replace(old_persist, new_persist, 1)

old_restore = """    restored.uiState.lastAction = null;\n    this.state = restored;\n"""
new_restore = """    restored.uiState.lastAction = null;\n    // Restoring replaces the entire in-memory state; require a real snapshot of\n    // the current state first so a failed recovery-folder write cannot destroy\n    // the only known-good state. writeRecoveryState throws on failure.\n    writeRecoveryState(this, this.state, 'before-restore');\n    this.state = restored;\n"""
assert old_restore in s, 'restore target not found'
s = s.replace(old_restore, new_restore, 1)
p.write_text(s, encoding='utf-8')

# Pure state-safety behavior tests.
p = Path('tests/state-safety.test.cjs')
s = p.read_text(encoding='utf-8')
s = s.replace("  protectBeforePersist,\n", "  protectBeforePersist,\n  requireRecoverySnapshot,\n", 1)
addition = r'''

test('failed pre-save protection does not advance lastProtectedRaw and retries later', () => {
  const { pluginDir, plugin } = fixture();
  const state = richState();
  const raw = JSON.stringify(state);
  fs.writeFileSync(path.join(pluginDir, 'data.json'), raw, 'utf8');
  plugin._goStudyStateSafety = { lastProtectedRaw: '' };

  const originalWrite = fs.writeFileSync;
  fs.writeFileSync = function failRecovery(target, ...args) {
    if (String(target).includes('go-study-recovery')) throw new Error('disk denied');
    return originalWrite.call(this, target, ...args);
  };
  let failed;
  try { failed = protectBeforePersist(plugin, 10); }
  finally { fs.writeFileSync = originalWrite; }

  assert.equal(failed.protected, false);
  assert.match(String(failed.protectionError?.message || ''), /disk denied/);
  assert.equal(plugin._goStudyStateSafety.lastProtectedRaw, '');
  assert.equal(plugin._goStudyStateSafety.protectionDegraded, true);

  const retried = protectBeforePersist(plugin, 10);
  assert.equal(retried.protected, true);
  assert.equal(retried.protectionError, null);
  assert.equal(plugin._goStudyStateSafety.lastProtectedRaw, raw);
  assert.equal(plugin._goStudyStateSafety.protectionDegraded, false);
});

test('required recovery snapshots reject high-risk operations when protection failed', () => {
  assert.throws(
    () => requireRecoverySnapshot({ recoveryPath: '', error: new Error('read only') }, 'Preview 迁移'),
    (error) => error?.code === 'GO_STUDY_RECOVERY_REQUIRED' && /Preview 迁移/.test(error.message)
  );
  assert.doesNotThrow(() => requireRecoverySnapshot({ recoveryPath: '/tmp/safe.json' }, '恢复'));
});
'''
if "failed pre-save protection does not advance" not in s:
    s += addition
p.write_text(s, encoding='utf-8')

# Integration contract checks for strict high-risk paths.
p = Path('tests/state-safety-integration.test.cjs')
s = p.read_text(encoding='utf-8')
addition = r'''

test('high-risk migration and restore require protective snapshots before replacing state', () => {
  assert.match(mainSource, /requireRecoverySnapshot\(protectedMigration, 'Preview 迁移'\)/);
  assert.match(mainSource, /readOnlySafety = true/);
  const snapshotIndex = mainSource.indexOf("writeRecoveryState(this, this.state, 'before-restore')");
  const replaceIndex = mainSource.indexOf('this.state = restored;', snapshotIndex);
  assert.ok(snapshotIndex >= 0 && replaceIndex > snapshotIndex);
});
'''
if "high-risk migration and restore require protective snapshots" not in s:
    s += addition
p.write_text(s, encoding='utf-8')
