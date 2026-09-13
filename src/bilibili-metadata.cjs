'use strict';

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
