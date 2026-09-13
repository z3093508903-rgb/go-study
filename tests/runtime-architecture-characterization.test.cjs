'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const source = (name) => fs.readFileSync(path.join(root, 'src', name), 'utf8');

function sliceBetween(text, start, end) {
  const from = text.indexOf(start);
  assert.notEqual(from, -1, `missing start marker: ${start}`);
  const to = text.indexOf(end, from + start.length);
  assert.notEqual(to, -1, `missing end marker: ${end}`);
  return text.slice(from, to);
}

test('runtime entry keeps the current three-layer inheritance chain explicit', () => {
  const runtime = source('runtime-entry.cjs');
  const entry = source('entry.cjs');

  assert.match(runtime, /const ResourceHubNextPlugin = require\('\.\/entry\.cjs'\)/);
  assert.match(runtime, /class ResourceHubNextRuntimePlugin extends ResourceHubNextPlugin/);
  assert.match(entry, /const BaseResourceHubNextPlugin = require\('\.\/main\.cjs'\)/);
  assert.match(entry, /class ResourceHubNextPlugin extends BaseResourceHubNextPlugin/);
});

test('startup defers base Vault validation until layout readiness', () => {
  const entry = source('entry.cjs');
  const onload = sliceBetween(entry, '  async onload() {', '\n  enabledPluginIds() {');

  const guardIndex = onload.indexOf('this._vaultLifecycleReady = false');
  const superIndex = onload.indexOf('await super.onload()');
  const readyIndex = onload.indexOf('this._vaultLifecycleReady = true');
  const validateIndex = onload.indexOf('await super.validateVaultRefs()');

  assert.ok(guardIndex >= 0 && guardIndex < superIndex, 'Vault guard must be set before base onload');
  assert.ok(readyIndex > superIndex, 'Vault lifecycle should activate after base onload');
  assert.ok(validateIndex > readyIndex, 'base Vault validation should run only after lifecycle activation');
  assert.match(onload, /onLayoutReady/);

  const validationOverride = sliceBetween(entry, '  async validateVaultRefs() {', '\n  async handleVaultRename');
  assert.match(validationOverride, /if \(this\._vaultLifecycleReady === false\) return false/);
  assert.match(validationOverride, /return super\.validateVaultRefs\(\)/);
});

test('base settings registration is intentionally intercepted by runtime product settings', () => {
  const main = source('main.cjs');
  const runtime = source('runtime-entry.cjs');

  assert.match(main, /this\.addSettingTab\?\.\(new ResourceHubNextSettingTab\(this\.app, this\)\)/);

  const override = sliceBetween(runtime, '  addSettingTab(tab) {', '\n  async onload() {');
  assert.match(override, /_goStudySettingsTabRegistered/);
  assert.match(override, /new GoStudySettingsTab\(this\.app, this\)/);
  assert.match(override, /return super\.addSettingTab\(tab\)/);
});

test('runtime startup adds product integrations only after lower layers finish loading', () => {
  const runtime = source('runtime-entry.cjs');
  const onload = sliceBetween(runtime, '  async onload() {', '\n  async openResourceAction');

  const superIndex = onload.indexOf('await super.onload()');
  assert.ok(superIndex >= 0);

  for (const marker of [
    'installTimelineNavigator(this)',
    'registerRememberedNoteTarget(this)',
    'registerCompanionNoteCommands(this)',
    'registerBilibiliWebBridge(this)',
    'registerImmersiveHotkeys(this)',
    'installLearningControls(this)',
    'installProjectNoteEntryPoints(this)'
  ]) {
    const index = onload.indexOf(marker);
    assert.ok(index > superIndex, `${marker} must remain after super.onload()`);
  }
});

test('resource play remains layered through runtime -> entry -> base behavior', () => {
  const runtime = source('runtime-entry.cjs');
  const entry = source('entry.cjs');
  const main = source('main.cjs');

  const runtimeOpen = sliceBetween(runtime, '  async openResourceAction(resource, actionType, target, options = {}) {', '\n  async continueRecentProjectStudy');
  assert.match(runtimeOpen, /chooseStudyNote\(this, projectId, resource\)/);
  assert.match(runtimeOpen, /await super\.openResourceAction\(resource, actionType, target, options\)/);
  assert.match(runtimeOpen, /recordRecentStudy\(this\.state, projectId, resource\.id/);
  assert.ok(runtimeOpen.indexOf('chooseStudyNote') < runtimeOpen.indexOf('await super.openResourceAction'));
  assert.ok(runtimeOpen.indexOf('await super.openResourceAction') < runtimeOpen.indexOf('recordRecentStudy'));

  const entryOpen = sliceBetween(entry, '  async openResourceAction(resource, actionType, target, options = {}) {', '\n  async relinkOpenListResourceToPath');
  assert.match(entryOpen, /const opened = await super\.openResourceAction\(resource, actionType, target, options\)/);
  assert.match(entryOpen, /this\.activeMediaSession =/);

  const baseOpen = sliceBetween(main, '  async openResourceAction(resource, actionType, target, options = {}) {', '\n  async openResource(resource) {');
  assert.match(baseOpen, /await this\.markResourceStarted\(resource\)/);
  assert.match(baseOpen, /return true/);
});

test('base persistence keeps data-safety checks around every saveData write', () => {
  const main = source('main.cjs');
  const persist = sliceBetween(main, '  async persist() {', '\n  bindMemoHeight(');

  const assertIndex = persist.indexOf('assertSafePersist(this)');
  const readonlyIndex = persist.indexOf('readOnlySafety');
  const protectIndex = persist.indexOf('protectBeforePersist(this, retention)');
  const saveIndex = persist.indexOf('await this.saveData(this.state)');
  const refreshIndex = persist.indexOf('refreshPersistBaseline(this)');

  assert.ok(assertIndex >= 0);
  assert.ok(readonlyIndex > assertIndex);
  assert.ok(protectIndex > readonlyIndex);
  assert.ok(saveIndex > protectIndex);
  assert.ok(refreshIndex > saveIndex);
});

test('Vault callbacks remain virtual so lifecycle and project-note layers can extend base behavior', () => {
  const main = source('main.cjs');
  const entry = source('entry.cjs');
  const runtime = source('runtime-entry.cjs');

  assert.match(main, /this\.handleVaultRename\(entry, oldPath\)/);
  assert.match(main, /this\.handleVaultDelete\(entry\)/);
  assert.match(main, /this\.handleVaultCreate\(entry\)/);

  for (const method of ['handleVaultRename', 'handleVaultDelete', 'handleVaultCreate']) {
    assert.match(entry, new RegExp(`async ${method}\\(`));
    assert.match(runtime, new RegExp(`async ${method}\\(`));
  }

  assert.match(entry, /if \(this\._vaultLifecycleReady === false\) return/);
  assert.match(runtime, /updateProjectNotePathsOnRename/);
  assert.match(runtime, /markProjectNotesMissing/);
  assert.match(runtime, /restoreProjectNotePath/);
});
