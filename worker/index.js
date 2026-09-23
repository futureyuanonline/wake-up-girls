/**
 * Wake Up Girls · Worker 入口
 *
 * 作用：静态站点之外，增加两个接口
 *   POST /api/submit   读者在站内提交投稿 / 订阅 → 写入 KV
 *   GET  /inbox?key=…  主理人的私有收件箱（列表 + CSV 导出），需要密钥
 * 其余请求全部交给静态资源（env.ASSETS）。
 *
 * 绑定（在 wrangler.jsonc 与 Cloudflare 后台配置）
 *   INBOX     KV namespace   存放来信
 *   INBOX_KEY Secret         收件箱访问密钥（不要写进仓库）
 */

const MAX_LEN = 20000;        // 单条内容上限
const HONEYPOT = 'website';   // 蜜罐字段：真人看不见，机器人会填
const ALLOWED = ['submit', 'subscribe'];

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function clientIp(request) {
  return request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '';
}

/* ---------------- 提交 ---------------- */
async function handleSubmit(request, env) {
  if (request.method !== 'POST') return json({ ok: false, error: 'method' }, 405);
  let data;
  try {
    data = await request.json();
  } catch (e) {
    return json({ ok: false, error: 'bad_json' }, 400);
  }

  // 蜜罐：被填了就当作机器人，直接返回成功（不给机器人反馈）
  if (data[HONEYPOT]) return json({ ok: true });

  const type = String(data.type || 'submit');
  if (ALLOWED.indexOf(type) < 0) return json({ ok: false, error: 'bad_type' }, 400);

  const name = String(data.name || '').slice(0, 120).trim();
  const topic = String(data.topic || '').slice(0, 200).trim();
  const email = String(data.email || '').slice(0, 160).trim();
  const content = String(data.content || '').slice(0, MAX_LEN).trim();

  if (type === 'submit' && content.length < 5) return json({ ok: false, error: 'too_short' }, 400);
  if (type === 'subscribe' && !/^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$/.test(email)) {
    return json({ ok: false, error: 'bad_email' }, 400);
  }
  if (!env.INBOX) return json({ ok: false, error: 'no_store' }, 500);

  // 简单限流：同一 IP 每分钟最多 5 条
  const ip = clientIp(request);
  const bucket = 'rl:' + ip + ':' + Math.floor(Date.now() / 60000);
  try {
    const n = parseInt((await env.INBOX.get(bucket)) || '0', 10);
    if (n >= 5) return json({ ok: false, error: 'rate_limited' }, 429);
    await env.INBOX.put(bucket, String(n + 1), { expirationTtl: 180 });
  } catch (e) { /* 限流失败不阻断提交 */ }

  const rec = {
    type, name, topic, email, content,
    ua: request.headers.get('user-agent') || '',
    region: (request.cf && request.cf.country) || '',
    ip: ip.slice(0, 45),
    at: new Date().toISOString(),
  };
  const key = 'sub:' + Date.now() + ':' + Math.random().toString(36).slice(2, 8);
  try {
    await env.INBOX.put(key, JSON.stringify(rec));
  } catch (e) {
    return json({ ok: false, error: 'store_failed' }, 500);
  }
  return json({ ok: true });
}


/* ---------------- 轻量访问统计 ----------------
 * 只记「哪天、哪个页面、被访问几次」，不记录 IP、UA、Cookie 或任何可识别信息。
 * 键：stat:YYYY-MM-DD:<页面>  值：次数字符串（保留 120 天自动过期） */
async function countHit(env, pathname) {
  if (!env.INBOX) return;
  const day = new Date().toISOString().slice(0, 10);
  const name = pathname === '/' ? 'home'
    : pathname.replace(/^\/+|\/+$/g, '').replace(/[^a-zA-Z0-9\u4e00-\u9fa5]+/g, '_').slice(0, 40) || 'other';
  const key = 'stat:' + day + ':' + name;
  try {
    const n = parseInt((await env.INBOX.get(key)) || '0', 10);
    await env.INBOX.put(key, String(n + 1), { expirationTtl: 60 * 60 * 24 * 120 });
  } catch (e) { /* 统计失败绝不影响访问 */ }
}

async function readStats(env) {
  const byDay = {}, byPage = {}, pages = {}, days = {};
  let cursor = null;
  do {
    const page = await env.INBOX.list({ prefix: 'stat:', cursor, limit: 1000 });
    for (const k of page.keys) {
      const parts = k.name.split(':');
      const day = parts[1], name = parts.slice(2).join(':');
      const n = parseInt((await env.INBOX.get(k.name)) || '0', 10) || 0;
      days[day] = (days[day] || 0) + n;
      pages[name] = (pages[name] || 0) + n;
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  const dayList = Object.keys(days).sort().slice(-14).map((d) => ({ d, n: days[d] }));
  const pageList = Object.keys(pages).sort((a, b) => pages[b] - pages[a]).slice(0, 12)
    .map((k) => ({ p: k, n: pages[k] }));
  const total = Object.keys(days).reduce((a, d) => a + days[d], 0);
  return { total, dayList, pageList };
}


/* 访问信标：页面加载时由前端 POST /api/hit（静态资源请求默认不经过 Worker，故不能在那里记账） */
async function handleHit(request, env, ctx) {
  if (request.method !== 'POST') return new Response('', { status: 204 });
  let body = {};
  try { body = await request.json(); } catch (e) {}
  const raw = String(body.p || '/');
  const path = raw.split('?')[0].slice(0, 120);
  if (env.INBOX) {
    const task = countHit(env, path);
    if (ctx && ctx.waitUntil) ctx.waitUntil(task); else task.catch(() => {});
  }
  return new Response('', { status: 204, headers: { 'cache-control': 'no-store' } });
}

/* ---------------- 私有收件箱 ---------------- */
/* 密钥来源（二者皆可，优先 Secret）：
 *   1) Worker Secret  INBOX_KEY（在 Cloudflare 后台 Settings → Variables and Secrets 设置）
 *   2) KV 条目        key = config:inbox_key（在 KV Pairs 里 Add entry，无需任何授权）
 * 这样即使不方便设置 Secret，也能用 KV 里的密钥开门。 */
async function authed(env, url) {
  const key = url.searchParams.get('key') || '';
  if (!key) return false;
  let expected = env.INBOX_KEY || '';
  if (!expected && env.INBOX) {
    try { expected = (await env.INBOX.get('config:inbox_key')) || ''; } catch (e) {}
  }
  return !!expected && key === expected;
}

async function listAll(env, limit = 300) {
  const out = [];
  let cursor = null;
  do {
    const page = await env.INBOX.list({ prefix: 'sub:', cursor, limit: 100 });
    for (const k of page.keys) {
      const v = await env.INBOX.get(k.name);
      if (v) { try { out.push(JSON.parse(v)); } catch (e) {} }
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor && out.length < limit);
  return out.sort((a, b) => String(b.at).localeCompare(String(a.at)));
}

async function handleInbox(request, env, url) {
  if (!(await authed(env, url))) return json({ ok: false, error: 'unauthorized' }, 401);
  if (!env.INBOX) return json({ ok: false, error: 'no_store' }, 500);
  const items = await listAll(env);
  if (url.searchParams.get('format') === 'csv') {
    const head = '时间,类型,称呼,主题,邮箱,内容\n';
    const rows = items.map((r) => [r.at, r.type, r.name, r.topic, r.email, r.content]
      .map((x) => '"' + String(x == null ? '' : x).replace(/"/g, '""').replace(/\r?\n/g, ' ') + '"').join(',')).join('\n');
    return new Response('\ufeff' + head + rows, {
      headers: {
        'content-type': 'text/csv; charset=utf-8',
        'content-disposition': 'attachment; filename="wake-up-girls-inbox.csv"',
        'cache-control': 'no-store',
      },
    });
  }
  return json({ ok: true, count: items.length, items });
}

async function handleInboxPage(request, env, url) {
  if (!(await authed(env, url))) {
    return new Response(
      '<!doctype html><meta charset="utf-8"><title>收件箱</title>' +
      '<div style="font:16px/1.9 -apple-system,Segoe UI,Microsoft YaHei,sans-serif;max-width:640px;margin:80px auto;padding:0 20px">' +
      '<h1 style="font-size:22px">私有收件箱</h1>' +
      '<p>需要密钥才能查看。地址格式：<code>/inbox?key=你的密钥</code></p></div>',
      { status: 401, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
  }
  const items = await listAll(env);
  const rows = items.map((r) => (
    '<div style="border:1px solid #e2ded4;border-radius:6px;padding:14px 16px;margin:12px 0;background:#fff">' +
    '<div style="font-size:12px;color:#8a7a72">' + esc(r.at) + ' · ' + esc(r.type) +
    (r.region ? ' · ' + esc(r.region) : '') + '</div>' +
    '<div style="font-weight:700;margin:6px 0">' + esc(r.topic || r.email || '(无主题)') + '</div>' +
    (r.name ? '<div style="font-size:13px;color:#5a4f49">称呼：' + esc(r.name) + '</div>' : '') +
    (r.email ? '<div style="font-size:13px;color:#5a4f49">邮箱：' + esc(r.email) + '</div>' : '') +
    '<div style="white-space:pre-wrap;font-size:14px;line-height:1.85;margin-top:8px">' + esc(r.content) + '</div>' +
    '</div>'
  )).join('');
  const csv = esc(url.pathname + '?key=' + url.searchParams.get('key') + '&format=csv');
  let stats = { total: 0, dayList: [], pageList: [] };
  try { stats = await readStats(env); } catch (e) {}
  const statHtml =
    '<div style="background:#fff;border:1px solid #e2ded4;border-radius:6px;padding:16px;margin:16px 0">' +
    '<div style="font-weight:700;margin-bottom:10px">\u8bbf\u95ee\u7edf\u8ba1\uff08\u7ad9\u5185\u81ea\u5efa\uff0c\u4e0d\u8bb0\u5f55\u4e2a\u4eba\u4fe1\u606f\uff09</div>' +
    '<div style="font-size:13px;color:#5a4f49;margin-bottom:10px">\u7d2f\u8ba1\u6d4f\u89c8 ' + stats.total + ' \u6b21</div>' +
    (stats.dayList.length
      ? '<div style="font-size:13px;line-height:1.9">' + stats.dayList.map(function (x) {
          return esc(x.d) + '\u3000' + x.n + ' \u6b21';
        }).join('<br>') + '</div>'
      : '<div style="font-size:13px;color:#8a7a72">\u8fd8\u6ca1\u6709\u6570\u636e\uff08\u90e8\u7f72\u540e\u5f00\u59cb\u8bb0\u5f55\uff09</div>') +
    (stats.pageList.length
      ? '<div style="font-size:13px;line-height:1.9;margin-top:10px;color:#5a4f49">\u6700\u5e38\u8bbf\u95ee\uff1a' +
        stats.pageList.map(function (x) { return esc(x.p) + '(' + x.n + ')'; }).join(' \u00b7 ') + '</div>'
      : '') +
    '</div>';
  return new Response(
    '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>Wake Up Girls 收件箱（' + items.length + '）</title>' +
    '<meta name="robots" content="noindex,nofollow">' +
    '<div style="font:15px/1.7 -apple-system,Segoe UI,Microsoft YaHei,sans-serif;max-width:760px;margin:0 auto;padding:32px 20px 80px;background:#f4f1eb;min-height:100vh">' +
    '<h1 style="font-size:24px;margin:0 0 6px">收件箱</h1>' +
    '<p style="color:#8a7a72;font-size:13px;margin:0 0 6px">共 ' + items.length + ' 条 · ' +
    '投稿与订阅都在这里 · 本页不公开、不会被搜索引擎收录</p>' +
    '<p style="font-size:13px"><a href="' + csv + '" style="color:#a12627">下载 CSV</a></p>' +
    statHtml +
    (rows || '<p style="color:#8a7a72">还没有来信。</p>') +
    '</div>',
    { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/api/submit') return handleSubmit(request, env);
    if (url.pathname === '/api/inbox') return handleInbox(request, env, url);
    if (url.pathname === '/inbox') return handleInboxPage(request, env, url);
    const res = await env.ASSETS.fetch(request);
    // 只统计静态 HTML 页面的成功访问；用 waitUntil 记账，不影响响应速度
    if (request.method === 'GET' && res.status === 200 &&
        (res.headers.get('content-type') || '').includes('text/html')) {
      const task = countHit(env, url.pathname);
      if (ctx && ctx.waitUntil) ctx.waitUntil(task); else task.catch(() => {});
    }
    return res;
  },
};
