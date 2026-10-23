/* 生成「机器可读层」（SEO + GEO）
 *
 * 为什么需要：站内内容全部由 JS 渲染，服务端 HTML 只有空壳。
 *   - Google 会执行 JS，但 AI 爬虫（GPTBot / ClaudeBot / PerplexityBot 等）基本不执行；
 *   - 所以对 GEO（生成式引擎优化）而言，这个站目前是隐形的。
 *
 * 本脚本产出：
 *   seo/a-<id>.html   每条报道的静态全文页（含 JSON-LD NewsArticle、来源链接、canonical）
 *   seo/i-<id>.html   每期的静态页（标题、摘要、全部条目）
 *   llms.txt          AI 引擎入口：站点结构 + 最新内容清单（纯文本）
 *   feed.xml          RSS 2.0，供聚合器与爬虫发现
 *
 * 由 worker 把 /a/<id>、/i/<id> 重写到对应静态文件；sitemap 收录静态页。
 * 用法：node tools/build_seo.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import vm from 'node:vm'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SITE = 'https://yuanxiuzhong.com'
const SEO = path.join(ROOT, 'seo')
const today = new Date().toISOString().slice(0, 10)

function load(rel, name) {
  const code = fs.readFileSync(path.join(ROOT, rel), 'utf8')
  const ctx = { window: {}, console }
  vm.createContext(ctx)
  vm.runInContext(code, ctx)
  return ctx.window[name] || []
}

const ISSUES = load('data/issues.js', 'ISSUES')
const WORKS = load('data/works.js', 'WORKS')
const COLUMNS = load('data/columns.js', 'COLUMNS')
const NUMBERS = load('data/numbers.js', 'NUMBERS')

fs.rmSync(SEO, { recursive: true, force: true })
fs.mkdirSync(SEO, { recursive: true })

const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;')
const strip = (s) => String(s || '').replace(/[《》]/g, '').trim()

function page({ title, desc, url, body, json }) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}" />
<link rel="canonical" href="${esc(url)}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="Wake Up Girls 全球女性议题周报" />
<meta property="og:title" content="${esc(title)}" />
<meta property="og:description" content="${esc(desc)}" />
<meta property="og:url" content="${esc(url)}" />
<meta name="twitter:card" content="summary_large_image" />
${json ? `<script type="application/ld+json">${JSON.stringify(json)}</script>` : ''}
<style>
  :root { color-scheme: light }
  body { margin:0; background:#F4F1EB; color:#1D1715; font:16px/1.85 "Microsoft YaHei","Noto Serif SC",system-ui,sans-serif }
  .wrap { max-width:760px; margin:0 auto; padding:40px 20px 80px }
  .kicker { font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:#A12627; font-weight:700 }
  h1 { font-size:clamp(24px,4vw,34px); line-height:1.4; margin:14px 0 8px }
  .meta { font-size:13px; color:#6B5F58; margin-bottom:22px }
  h2 { font-size:14px; letter-spacing:.08em; color:#A12627; margin:26px 0 8px }
  p { margin:0 0 14px }
  a { color:#A12627 }
  .src { font-size:13px; color:#6B5F58; border-top:1px dashed #DAD4C8; padding-top:12px; margin-top:24px; word-break:break-all }
  .nav { font-size:13px; margin-top:26px }
  blockquote { margin:0; padding:8px 14px; border-left:3px solid #A12627; background:#FBF3E6; font-size:14px }
</style>
</head>
<body><div class="wrap">
${body}
</div></body>
</html>
`
}

/* ---------- 每条报道 ---------- */
let nArticles = 0
const articleIndex = []
for (const iss of ISSUES) {
  for (const sec of iss.sections || []) {
    for (const it of sec.items || []) {
      const id = it.id
      if (!id) continue
      const url = `${SITE}/a/${id}`
      const title = strip(it.t)
      const desc = strip(it.d).slice(0, 110)
      const paras = (it.body && it.body.length ? it.body : [it.d]).map((p) => `<p>${esc(p)}</p>`).join('\n')
      const body = `
<div class="kicker">${esc(sec.cat || '')} · 第 ${esc(iss.id)} 期 · ${esc(it.region || '')}</div>
<h1>${esc(title)}</h1>
<div class="meta">${esc(iss.period || '')} ｜ Wake Up Girls 全球女性议题周报</div>
${it.d ? `<blockquote>${esc(it.d)}</blockquote>` : ''}
<h2>正文</h2>
${paras}
${it.why ? `<h2>为什么值得关注</h2><p>${esc(it.why)}</p>` : ''}
<div class="src">原始来源：${it.url ? `<a href="${esc(it.url)}" rel="nofollow noopener">${esc(it.src || it.url)}</a>` : esc(it.src || '—')}</div>
<div class="nav"><a href="/">← 回到本周首页</a> · <a href="/issue.html?id=${esc(iss.id)}">第 ${esc(iss.id)} 期全部条目</a> · <a href="/a/${esc(id)}">本条固定链接</a></div>`
      const json = {
        '@context': 'https://schema.org',
        '@type': 'NewsArticle',
        headline: title,
        description: desc,
        url,
        mainEntityOfPage: url,
        datePublished: iss.date || today,
        dateModified: iss.date || today,
        inLanguage: 'zh-CN',
        articleSection: sec.cat || '',
        author: { '@type': 'Organization', name: 'Wake Up Girls 全球女性议题周报' },
        publisher: { '@type': 'Organization', name: 'Wake Up Girls', url: SITE },
        isBasedOn: it.url || undefined,
        citation: it.src || undefined
      }
      fs.writeFileSync(path.join(SEO, `a-${id}.html`),
        page({ title: `${title} ｜ Wake Up Girls`, desc: desc || title, url, body, json }), 'utf8')
      nArticles++
      articleIndex.push({ id, title, url, issue: iss.id, region: it.region || '', src: it.src || '', date: iss.date || '' })
    }
  }
}

/* ---------- 每期 ---------- */
for (const iss of ISSUES) {
  const url = `${SITE}/i/${iss.id}`
  const items = []
  for (const sec of iss.sections || []) {
    for (const it of sec.items || []) {
      items.push(`<li><a href="/a/${esc(it.id)}">${esc(strip(it.t))}</a><br/><span style="font-size:13px;color:#6B5F58">${esc(sec.cat || '')} · ${esc(it.region || '')} · ${esc(it.src || '')}</span></li>`)
    }
  }
  const body = `
<div class="kicker">第 ${esc(iss.id)} 期 · ${esc(iss.period || '')}</div>
<h1>${esc(strip(iss.title))}</h1>
<div class="meta">${esc(iss.period || '')} ｜ Wake Up Girls</div>
${iss.summary ? `<p>${esc(iss.summary)}</p>` : ''}
<h2>本期条目（${items.length}）</h2>
<ul>${items.join('\n')}</ul>
<div class="nav"><a href="/">← 回到首页</a> · <a href="/archive.html">往期全部</a></div>`
  const json = {
    '@context': 'https://schema.org',
    '@type': 'Periodical',
    name: `Wake Up Girls 第 ${iss.id} 期`,
    url,
    datePublished: iss.date || today,
    inLanguage: 'zh-CN',
    publisher: { '@type': 'Organization', name: 'Wake Up Girls', url: SITE }
  }
  fs.writeFileSync(path.join(SEO, `i-${iss.id}.html`),
    page({ title: `第 ${iss.id} 期：${strip(iss.title)} ｜ Wake Up Girls`,
      desc: strip(iss.summary).slice(0, 110), url, body, json }), 'utf8')
}

/* ---------- llms.txt ---------- */
const latest = ISSUES[0] || { sections: [], id: '—', period: '' }
const latestItems = latest.sections.flatMap((s) => (s.items || []).map((it) => ({ ...it, cat: s.cat })))
const lines = [
  '# Wake Up Girls 全球女性议题周报',
  '',
  '> 用证据读性别。每期从全球十个地区、用当地语言的公开来源采集女性议题新闻，写成中文摘要并附原始链接；',
  '> 同时维护一个女性创作作品库（电影 / 图书 / 艺术），以及一个只讲单个数字的「数字」栏目。',
  '',
  `最近更新：${today} ｜ 最新一期：第 ${latest.id} 期（${latest.period}）`,
  '',
  '## 栏目与入口',
  `- 最新一期：${SITE}/i/${latest.id}`,
  `- 往期归档：${SITE}/archive.html`,
  `- 作品库（${WORKS.length} 件）：${SITE}/works.html`,
  `- 专栏（按议题）：${SITE}/columns.html`,
  `- 数字栏目（每期一个数字，含"它不能推出什么"）：${SITE}/numbers.html`,
  `- sitemap：${SITE}/sitemap.xml ｜ RSS：${SITE}/feed.xml`,
  '',
  `## 第 ${latest.id} 期全部条目（${latestItems.length} 条，静态全文页可直读）`,
  ...latestItems.map((it) => `- [${strip(it.t)}](${SITE}/a/${it.id}) — ${it.cat || ''} · ${it.region || ''} · 来源：${it.src || '—'}`),
  '',
  '## 「数字」栏目（可引用格式）',
  ...NUMBERS.map((n) => `- ${n.value}（${n.valueLabel || ''}）：${strip(n.title)} — ${SITE}/n/${n.id}\n  唯一能支撑的结论：${strip(n.claim)}`),
  '',
  '## 专栏',
  ...COLUMNS.map((c) => `- ${c.name}（${c.en}）：${strip(c.intro).slice(0, 80)}… — ${SITE}/column.html?id=${c.id}`),
  '',
  '## 引用与许可',
  '- 站内文字由主理人编辑，可引用，请注明来源与期号。',
  '- 每条报道均附原始链接；摘要为二次整理，事实请以原文为准。',
  '- 作品库条目附 Wikidata QID（标签含 Q 编号者），可回溯核实。',
  '',
  '## 机器可读数据',
  `- ${SITE}/data/issues.js（全部期号与条目）`,
  `- ${SITE}/data/works.js（作品库）`,
  `- ${SITE}/data/numbers.js（数字栏目）`,
  `- ${SITE}/data/columns.js（专栏归类）`,
  ''
]
fs.writeFileSync(path.join(ROOT, 'llms.txt'), lines.join('\n'), 'utf8')

/* ---------- feed.xml（RSS 2.0） ---------- */
const rssItems = articleIndex.slice(0, 30).map((a) => {
  const d = a.date ? new Date(a.date + 'T09:00:00+08:00') : new Date()
  return `    <item>
      <title>${esc(a.title)}</title>
      <link>${a.url}</link>
      <guid isPermaLink="true">${a.url}</guid>
      <pubDate>${d.toUTCString()}</pubDate>
      <category>${esc(a.region)}</category>
    </item>`
}).join('\n')
fs.writeFileSync(path.join(ROOT, 'feed.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
    <title>Wake Up Girls 全球女性议题周报</title>
    <link>${SITE}/</link>
    <description>每期从全球十个地区采集女性议题新闻，附原始来源；另有女性创作作品库与「数字」栏目。</description>
    <language>zh-CN</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${rssItems}
</channel></rss>
`, 'utf8')

/* ---------- robots.txt：显式放行主流 AI 爬虫 ---------- */
const robotsPath = path.join(ROOT, 'robots.txt')
const marker = '# AI 爬虫显式放行'
let robots = fs.existsSync(robotsPath) ? fs.readFileSync(robotsPath, 'utf8') : 'User-agent: *\nAllow: /\n'
if (!robots.includes(marker)) {
  const bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'anthropic-ai',
    'PerplexityBot', 'Google-Extended', 'Applebot-Extended', 'CCBot', 'Bytespider']
  robots = robots.trimEnd() + '\n\n' + marker + '（希望被 AI 引擎引用；内容均为公开页面）\n' +
    bots.map((b) => `User-agent: ${b}\nAllow: /\n`).join('') +
    `\n# 机器可读入口\n# llms.txt: ${SITE}/llms.txt\n`
  if (!robots.includes('Sitemap:')) robots += `\nSitemap: ${SITE}/sitemap.xml\n`
  fs.writeFileSync(robotsPath, robots, 'utf8')
}

console.log(`build_seo: 报道静态页 ${nArticles} 个 ｜ 期页 ${ISSUES.length} 个 ｜ llms.txt ｜ feed.xml`)
