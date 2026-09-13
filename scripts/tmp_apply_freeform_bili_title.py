from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)

metadata = r"""'use strict';

const BILIBILI_VIEW_ENDPOINT = 'https://api.bilibili.com/x/web-interface/view';
const BVID_PATTERN = /BV[0-9A-Za-z]{10}/i;

function cleanBilibiliMediaTitle(value) {
  return String(value || '')
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/\s+-\s+PotPlayer\s*$/i, '')
    .replace(/\.(mp4|mkv|avi|mov|webm|m4v)\s*$/i, '')
    .trim()
    .slice(0, 300);
}

function extractBilibiliBvid(...values) {
  for (const value of values.flat(Infinity)) {
    const match = String(value || '').match(BVID_PATTERN);
    if (match) return match[0];
  }
  return '';
}

function isBilibiliMachineTitle(value, bvid = '') {
  const title = cleanBilibiliMediaTitle(value);
  if (!title) return true;
  const expected = String(bvid || extractBilibiliBvid(title)).toLowerCase();
  if (expected && title.toLowerCase() === expected) return true;
  if (/^BV[0-9A-Za-z]{10}$/i.test(title)) return true;
  if (/^https?:\/\//i.test(title) && extractBilibiliBvid(title)) return true;
  return false;
}

function bilibiliTitleCache(plugin) {
  if (!plugin) return null;
  if (!(plugin._goStudyBilibiliTitleCache instanceof Map)) {
    plugin._goStudyBilibiliTitleCache = new Map();
  }
  return plugin._goStudyBilibiliTitleCache;
}

function rememberBilibiliTitle(plugin, bvid, title) {
  const id = extractBilibiliBvid(bvid);
  const cleaned = cleanBilibiliMediaTitle(title);
  if (!id || !cleaned || isBilibiliMachineTitle(cleaned, id)) return '';
  bilibiliTitleCache(plugin)?.set(id.toLowerCase(), cleaned);
  return cleaned;
}

function cachedBilibiliTitle(plugin, bvid) {
  const id = extractBilibiliBvid(bvid);
  if (!id) return '';
  return cleanBilibiliMediaTitle(bilibiliTitleCache(plugin)?.get(id.toLowerCase()) || '');
}

async function fetchBilibiliVideoTitle(requestImpl, bvid) {
  const id = extractBilibiliBvid(bvid);
  if (!id || typeof requestImpl !== 'function') return '';
  const response = await requestImpl({
    url: `${BILIBILI_VIEW_ENDPOINT}?bvid=${encodeURIComponent(id)}`,
    method: 'GET',
    headers: {
      Referer: 'https://www.bilibili.com/',
      'User-Agent': 'Mozilla/5.0 Go-Study/0.3'
    }
  });
  let payload = response?.json;
  if (!payload && response?.text) {
    try { payload = JSON.parse(response.text); } catch {}
  }
  if (!payload || Number(payload.code) !== 0) return '';
  const title = cleanBilibiliMediaTitle(payload.data?.title);
  return title && !isBilibiliMachineTitle(title, id) ? title : '';
}

async function enrichBilibiliMediaTitle(plugin, media = {}, requestImpl) {
  const source = media && typeof media === 'object' ? media : {};
  const bvid = extractBilibiliBvid(source.web, source.path, source.url, source.title, source.name);
  if (!bvid) return source;

  const current = cleanBilibiliMediaTitle(source.title);
  if (current && !isBilibiliMachineTitle(current, bvid)) {
    rememberBilibiliTitle(plugin, bvid, current);
    return current === source.title ? source : { ...source, title: current };
  }

  const cached = cachedBilibiliTitle(plugin, bvid);
  if (cached) return { ...source, title: cached };

  try {
    const resolved = await fetchBilibiliVideoTitle(requestImpl, bvid);
    if (!resolved) return source;
    rememberBilibiliTitle(plugin, bvid, resolved);
    return { ...source, title: resolved };
  } catch {
    return source;
  }
}

function liveBilibiliTitleForReference(plugin, reference = {}) {
  const bvid = extractBilibiliBvid(reference.web, reference.locator, reference.title, reference.name);
  if (!bvid) return '';
  const cached = cachedBilibiliTitle(plugin, bvid);
  if (cached) return cached;

  const state = plugin?._goStudyBilibiliWebState;
  const stateBvid = extractBilibiliBvid(state?.url, state?.title);
  if (!stateBvid || stateBvid.toLowerCase() !== bvid.toLowerCase()) return '';
  const title = cleanBilibiliMediaTitle(state?.title);
  if (!title || isBilibiliMachineTitle(title, bvid)) return '';
  rememberBilibiliTitle(plugin, bvid, title);
  return title;
}

module.exports = {
  BILIBILI_VIEW_ENDPOINT,
  cachedBilibiliTitle,
  cleanBilibiliMediaTitle,
  enrichBilibiliMediaTitle,
  extractBilibiliBvid,
  fetchBilibiliVideoTitle,
  isBilibiliMachineTitle,
  liveBilibiliTitleForReference,
  rememberBilibiliTitle
};
"""
Path('src/bilibili-metadata.cjs').write_text(metadata, encoding='utf-8')

p = Path('src/learning-capture.cjs')
s = p.read_text(encoding='utf-8')
s = replace_once(
    s,
    "const { requestBilibiliWebBridge } = require('./bilibili-web-bridge.cjs');\n",
    "const { requestBilibiliWebBridge } = require('./bilibili-web-bridge.cjs');\nconst { enrichBilibiliMediaTitle } = require('./bilibili-metadata.cjs');\n",
    'learning-capture import'
)
helper = r"""async function resolvePreparedLearningContext(plugin, response, options = {}) {
  let playerResponse = response;
  let context = resolveLearningContext(plugin, playerResponse?.media);
  if (context.mode !== 'freeform') return { context, response: playerResponse };

  const media = await enrichBilibiliMediaTitle(
    plugin,
    playerResponse?.media || {},
    options.requestUrl || requestUrl
  );
  if (media !== playerResponse?.media) playerResponse = { ...playerResponse, media };
  context = resolveLearningContext(plugin, playerResponse?.media);
  return { context, response: playerResponse };
}

"""
s = replace_once(s, "function noteOutputOptions(plugin) {\n", helper + "function noteOutputOptions(plugin) {\n", 'learning-capture helper')
s = replace_once(
    s,
    "  const response = await requestLearningPlayer(plugin, 'current', options);\n  const context = resolveLearningContext(plugin, response.media);\n  return { ...context, editor, player: response };\n",
    "  const response = await requestLearningPlayer(plugin, 'current', options);\n  const prepared = await resolvePreparedLearningContext(plugin, response, options);\n  return { ...prepared.context, editor, player: prepared.response };\n",
    'prepare current'
)
s = replace_once(
    s,
    "  const response = await requestLearningPlayer(plugin, 'capture', options);\n  const context = resolveLearningContext(plugin, response.media);\n  const png = options.readClipboardPng ? options.readClipboardPng() : clipboardPngBuffer(options.clipboard || clipboard);\n  return { ...context, editor, player: response, png };\n",
    "  const response = await requestLearningPlayer(plugin, 'capture', options);\n  const prepared = await resolvePreparedLearningContext(plugin, response, options);\n  const png = options.readClipboardPng ? options.readClipboardPng() : clipboardPngBuffer(options.clipboard || clipboard);\n  return { ...prepared.context, editor, player: prepared.response, png };\n",
    'prepare capture'
)
p.write_text(s, encoding='utf-8')

p = Path('src/timeline-navigator.cjs')
s = p.read_text(encoding='utf-8')
s = replace_once(
    s,
    "const { currentResourceForReference } = require('./reference-fallback.cjs');\n",
    "const { currentResourceForReference } = require('./reference-fallback.cjs');\nconst {\n  extractBilibiliBvid,\n  isBilibiliMachineTitle,\n  liveBilibiliTitleForReference\n} = require('./bilibili-metadata.cjs');\n",
    'timeline import'
)
s = replace_once(
    s,
    "function freeformSource(reference) {\n  let fallback = cleanSourceTitle(reference.title) || cleanSourceTitle(reference.name);\n",
    "function freeformSource(reference, plugin) {\n  const bvid = extractBilibiliBvid(reference.web, reference.locator, reference.title, reference.name);\n  let fallback = cleanSourceTitle(reference.title) || cleanSourceTitle(reference.name);\n  if (bvid && (!fallback || isBilibiliMachineTitle(fallback, bvid))) {\n    fallback = cleanSourceTitle(liveBilibiliTitleForReference(plugin, reference)) || fallback;\n  }\n",
    'timeline freeform source'
)
s = replace_once(s, "  return freeformSource(reference);\n", "  return freeformSource(reference, plugin);\n", 'timeline freeform call')
p.write_text(s, encoding='utf-8')

metadata_test = r"""'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const {
  cachedBilibiliTitle,
  enrichBilibiliMediaTitle,
  extractBilibiliBvid,
  fetchBilibiliVideoTitle,
  isBilibiliMachineTitle,
  liveBilibiliTitleForReference
} = require('../src/bilibili-metadata.cjs');

const BVID = 'BV1xx411c7mD';

test('Bilibili metadata extracts BV identity from URL, title, and local filename', () => {
  assert.equal(extractBilibiliBvid(`https://www.bilibili.com/video/${BVID}?p=2`), BVID);
  assert.equal(extractBilibiliBvid(`${BVID} - PotPlayer`), BVID);
  assert.equal(extractBilibiliBvid(`D:\\Course\\${BVID}.mp4`), BVID);
});

test('BV-only player titles are machine labels but human titles are not', () => {
  assert.equal(isBilibiliMachineTitle(`${BVID} - PotPlayer`, BVID), true);
  assert.equal(isBilibiliMachineTitle(`${BVID}.mp4`, BVID), true);
  assert.equal(isBilibiliMachineTitle('摄影构图：从零到一', BVID), false);
});

test('metadata lookup resolves and caches a human Bilibili title', async () => {
  const plugin = {};
  let requests = 0;
  const media = await enrichBilibiliMediaTitle(plugin, {
    path: `https://www.bilibili.com/video/${BVID}`,
    title: `${BVID} - PotPlayer`
  }, async (options) => {
    requests += 1;
    assert.match(options.url, new RegExp(BVID));
    return { json: { code: 0, data: { title: '真正的视频标题' } } };
  });
  assert.equal(media.title, '真正的视频标题');
  assert.equal(cachedBilibiliTitle(plugin, BVID), '真正的视频标题');

  const second = await enrichBilibiliMediaTitle(plugin, { path: BVID, title: BVID }, async () => {
    requests += 1;
    throw new Error('cache should avoid a second request');
  });
  assert.equal(second.title, '真正的视频标题');
  assert.equal(requests, 1);
});

test('existing human title never causes a remote metadata request', async () => {
  let requests = 0;
  const media = await enrichBilibiliMediaTitle({}, {
    path: `https://www.bilibili.com/video/${BVID}`,
    title: '已经是正常标题'
  }, async () => { requests += 1; return {}; });
  assert.equal(media.title, '已经是正常标题');
  assert.equal(requests, 0);
});

test('metadata failure is fail-open and keeps the original usable media identity', async () => {
  const media = await enrichBilibiliMediaTitle({}, {
    path: `https://www.bilibili.com/video/${BVID}`,
    title: BVID
  }, async () => { throw new Error('offline'); });
  assert.equal(media.title, BVID);
});

test('live Bilibili web state can repair a BV-only Timeline title without note rewriting', () => {
  const plugin = {
    _goStudyBilibiliWebState: {
      url: `https://www.bilibili.com/video/${BVID}`,
      title: '浏览器中的真实标题'
    }
  };
  assert.equal(liveBilibiliTitleForReference(plugin, {
    locator: `https://www.bilibili.com/video/${BVID}`,
    title: BVID
  }), '浏览器中的真实标题');
});

test('fetch helper accepts the public view endpoint payload shape', async () => {
  const title = await fetchBilibiliVideoTitle(async () => ({
    json: { code: 0, data: { title: '公开接口标题' } }
  }), BVID);
  assert.equal(title, '公开接口标题');
});
"""
Path('tests/bilibili-metadata.test.cjs').write_text(metadata_test, encoding='utf-8')

p = Path('tests/learning-capture.test.cjs')
s = p.read_text(encoding='utf-8').rstrip()
addition = r"""

test('BV-only Freeform PotPlayer capture enriches the backlink with the real Bilibili title', async () => {
  const { insertCurrentLearningPosition } = loadCaptureModule();
  const { plugin, inserted } = localPluginFixture();
  plugin.state.resources = {};
  plugin.activeMediaSession = null;
  plugin.resourceActions = () => ({});
  const bvid = 'BV1xx411c7mD';
  const result = await insertCurrentLearningPosition(plugin, {
    bridgeRequest: async () => ({
      ok: true,
      media: {
        path: `https://www.bilibili.com/video/${bvid}`,
        title: `${bvid} - PotPlayer`,
        positionSeconds: 37.5
      }
    }),
    requestUrl: async () => ({ json: { code: 0, data: { title: '真正的视频标题' } } }),
    editor: { replaceSelection: (text) => inserted.push(text) }
  });
  assert.equal(result.mode, 'freeform');
  assert.equal(result.bridgeMedia.title, '真正的视频标题');
  assert.match(decodeURIComponent(inserted[0]), /title=真正的视频标题/);
  assert.match(inserted[0], /v=2/);
});

test('BV title lookup failure never blocks Freeform timestamp insertion', async () => {
  const { insertCurrentLearningPosition } = loadCaptureModule();
  const { plugin, inserted } = localPluginFixture();
  plugin.state.resources = {};
  plugin.activeMediaSession = null;
  plugin.resourceActions = () => ({});
  const bvid = 'BV1xx411c7mD';
  const result = await insertCurrentLearningPosition(plugin, {
    bridgeRequest: async () => ({
      ok: true,
      media: { path: `D:\\Loose\\${bvid}.mp4`, title: bvid, positionSeconds: 12 }
    }),
    requestUrl: async () => { throw new Error('offline'); },
    editor: { replaceSelection: (text) => inserted.push(text) }
  });
  assert.equal(result.mode, 'freeform');
  assert.equal(inserted.length, 1);
  assert.match(inserted[0], /obsidian:\/\/go-study\?/);
});
"""
if 'BV-only Freeform PotPlayer capture enriches' in s:
    raise RuntimeError('learning capture tests already patched')
p.write_text(s + addition + '\n', encoding='utf-8')

p = Path('tests/timeline-navigator.test.cjs')
s = p.read_text(encoding='utf-8').rstrip()
addition = r"""

test('Timeline upgrades a BV-only Freeform label from the in-memory Bilibili title cache', () => {
  const bvid = 'BV1xx411c7mD';
  const uri = buildFreeformReferenceUri({
    locator: `D:\\Loose\\${bvid}.mp4`,
    name: `${bvid}.mp4`,
    title: bvid,
    position: { type: 'time', seconds: 65 }
  });
  const plugin = pluginFixture();
  plugin._goStudyBilibiliTitleCache = new Map([[bvid.toLowerCase(), '真实课程标题']]);
  const groups = timelineGroupsFromMarkdown(`[回到课程](${uri})`, plugin);
  assert.equal(groups.length, 1);
  assert.equal(groups[0].title, '真实课程标题');
  assert.equal(groups[0].items[0].time, '01:05');
});
"""
if 'BV-only Freeform label' in s:
    raise RuntimeError('timeline tests already patched')
p.write_text(s + addition + '\n', encoding='utf-8')

p = Path('docs/CODE_PRODUCT_SEMANTICS.md')
s = p.read_text(encoding='utf-8')
s = replace_once(
    s,
    '| **Freeform media** | Local/portable/web media currently being studied without requiring a stored Resource | media locator + name/web/title | `src/media-session.cjs`, `src/freeform-playback.cjs`, `src/resource-reference.cjs` | Current Freeform backlink wire format is presently `v=2`; it is **current**, not “old v2”. |',
    '| **Freeform media** | Local/portable/web media currently being studied without requiring a stored Resource | media locator + name/web/title | `src/media-session.cjs`, `src/freeform-playback.cjs`, `src/resource-reference.cjs`, `src/bilibili-metadata.cjs` | Current Freeform backlink wire format is presently `v=2`; it is **current**, not “old v2”. Bilibili BV-only machine labels may be enriched to a human title without changing Resource/project membership. |',
    'Freeform semantics row'
)
anchor = '| `src/bilibili-web-bridge.cjs` | Localhost bridge listener, Bilibili state normalization and timestamp helpers | **browser integration adapter** | browser extension, `learning-capture`, bridge tests |'
s = replace_once(
    s,
    anchor,
    anchor + '\n| `src/bilibili-metadata.cjs` | Detect BV-only machine labels, best-effort resolve/cache human Bilibili titles for Freeform media | **metadata adapter** | `learning-capture`, Timeline, Bilibili bridge state |',
    'metadata semantics row'
)
p.write_text(s, encoding='utf-8')

p = Path('docs/agent-work/20260913-chatgpt-freeform-bilibili-title.md')
s = p.read_text(encoding='utf-8')
s = s.replace('- `src/bilibili-web-bridge.cjs`\n', '')
s = s.replace('- `tests/bilibili-web-bridge.test.cjs`\n', '')
s = s.replace('Verify Bilibili Web Bridge can remember a good title in an in-memory cache.\n', 'Verify Timeline can use an already-known cached/live Bilibili title without performing network I/O itself.\n')
s = s.replace('- this work record\n', '- `.github/workflows/tmp-freeform-bili-title.yml` (temporary branch-only helper; deleted before merge)\n- `scripts/tmp_apply_freeform_bili_title.py` (temporary branch-only helper; deleted before merge)\n- this work record\n')
p.write_text(s, encoding='utf-8')
