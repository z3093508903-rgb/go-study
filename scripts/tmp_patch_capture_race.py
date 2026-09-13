from pathlib import Path

# 1) Snapshot clipboard PNG before any optional metadata await.
p = Path('src/learning-capture.cjs')
s = p.read_text(encoding='utf-8')
old = """  const response = await requestLearningPlayer(plugin, 'capture', options);\n  const prepared = await resolvePreparedLearningContext(plugin, response, options);\n  const png = options.readClipboardPng ? options.readClipboardPng() : clipboardPngBuffer(options.clipboard || clipboard);\n  return { ...prepared.context, editor, player: prepared.response, png };\n"""
new = """  const response = await requestLearningPlayer(plugin, 'capture', options);\n  const png = options.readClipboardPng ? options.readClipboardPng() : clipboardPngBuffer(options.clipboard || clipboard);\n  const prepared = await resolvePreparedLearningContext(plugin, response, options);\n  return { ...prepared.context, editor, player: prepared.response, png };\n"""
assert old in s, 'capture ordering target not found'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')

# 2) Bound Bilibili title lookup so enrichment remains fail-open in finite time.
p = Path('src/bilibili-metadata.cjs')
s = p.read_text(encoding='utf-8')
s = s.replace(
    "const BILIBILI_VIEW_ENDPOINT = 'https://api.bilibili.com/x/web-interface/view';\n",
    "const BILIBILI_VIEW_ENDPOINT = 'https://api.bilibili.com/x/web-interface/view';\nconst BILIBILI_TITLE_LOOKUP_TIMEOUT_MS = 1500;\n",
    1
)
old_fetch = """async function fetchBilibiliVideoTitle(requestImpl, bvid) {\n  const id = extractBilibiliBvid(bvid);\n  if (!id || typeof requestImpl !== 'function') return '';\n  const response = await requestImpl({\n    url: `${BILIBILI_VIEW_ENDPOINT}?bvid=${encodeURIComponent(id)}`,\n    method: 'GET',\n    headers: {\n      Referer: 'https://www.bilibili.com/',\n      'User-Agent': 'Mozilla/5.0 Go-Study/0.3'\n    }\n  });\n"""
new_fetch = """async function fetchBilibiliVideoTitle(requestImpl, bvid, options = {}) {\n  const id = extractBilibiliBvid(bvid);\n  if (!id || typeof requestImpl !== 'function') return '';\n  const timeoutMs = Math.max(50, Number(options.timeoutMs || BILIBILI_TITLE_LOOKUP_TIMEOUT_MS));\n  let timeoutId = null;\n  const requestPromise = Promise.resolve().then(() => requestImpl({\n    url: `${BILIBILI_VIEW_ENDPOINT}?bvid=${encodeURIComponent(id)}`,\n    method: 'GET',\n    headers: {\n      Referer: 'https://www.bilibili.com/',\n      'User-Agent': 'Mozilla/5.0 Go-Study/0.3'\n    }\n  }));\n  const timeoutPromise = new Promise((_, reject) => {\n    timeoutId = setTimeout(() => reject(new Error('bilibili_title_lookup_timeout')), timeoutMs);\n  });\n  let response;\n  try {\n    response = await Promise.race([requestPromise, timeoutPromise]);\n  } finally {\n    if (timeoutId) clearTimeout(timeoutId);\n  }\n"""
assert old_fetch in s, 'metadata fetch target not found'
s = s.replace(old_fetch, new_fetch, 1)
s = s.replace(
    "  BILIBILI_VIEW_ENDPOINT,\n",
    "  BILIBILI_TITLE_LOOKUP_TIMEOUT_MS,\n  BILIBILI_VIEW_ENDPOINT,\n",
    1
)
p.write_text(s, encoding='utf-8')

# 3) Behavior test: clipboard bytes are frozen before delayed metadata lookup mutates source.
p = Path('tests/learning-capture.test.cjs')
s = p.read_text(encoding='utf-8')
addition = r'''

test('capture freezes clipboard bytes before delayed Bilibili title enrichment', async () => {
  const { prepareCaptureLearningPosition } = loadCaptureModule();
  const { plugin } = localPluginFixture();
  plugin.state.resources = {};
  plugin.activeMediaSession = null;
  plugin.resourceActions = () => ({});
  const bvid = 'BV1xx411c7mD';
  let clipboardBytes = [1, 2, 3];
  let reads = 0;
  const result = await prepareCaptureLearningPosition(plugin, {
    bridgeRequest: async () => ({
      ok: true,
      media: {
        path: `https://www.bilibili.com/video/${bvid}`,
        title: `${bvid} - PotPlayer`,
        positionSeconds: 42
      }
    }),
    readClipboardPng: () => {
      reads += 1;
      return Buffer.from(clipboardBytes);
    },
    requestUrl: async () => {
      await new Promise((resolve) => setTimeout(resolve, 15));
      clipboardBytes = [9, 9, 9];
      return { json: { code: 0, data: { title: '真实标题' } } };
    },
    editor: { replaceSelection() {} }
  });
  assert.equal(reads, 1);
  assert.deepEqual([...result.png], [1, 2, 3]);
  assert.equal(result.bridgeMedia.title, '真实标题');
});
'''
if "capture freezes clipboard bytes before delayed Bilibili title enrichment" not in s:
    s += addition
p.write_text(s, encoding='utf-8')

# 4) Finite timeout test for the metadata helper.
p = Path('tests/bilibili-metadata.test.cjs')
s = p.read_text(encoding='utf-8')
addition = r'''

test('Bilibili metadata lookup has a finite timeout for a hung request', async () => {
  const { fetchBilibiliVideoTitle } = require('../src/bilibili-metadata.cjs');
  await assert.rejects(
    () => fetchBilibiliVideoTitle(() => new Promise(() => {}), BVID, { timeoutMs: 20 }),
    /bilibili_title_lookup_timeout/
  );
});
'''
if "metadata lookup has a finite timeout" not in s:
    s += addition
p.write_text(s, encoding='utf-8')
