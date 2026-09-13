'use strict';

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


test('Bilibili metadata lookup has a finite timeout for a hung request', async () => {
  const { fetchBilibiliVideoTitle } = require('../src/bilibili-metadata.cjs');
  await assert.rejects(
    () => fetchBilibiliVideoTitle(() => new Promise(() => {}), BVID, { timeoutMs: 20 }),
    /bilibili_title_lookup_timeout/
  );
});
