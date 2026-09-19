/* 生成 sitemap.xml（每周出新期后由 CI 重新生成）
 * 用法：node tools/build_sitemap.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import vm from 'node:vm'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SITE = 'https://yuanxiuzhong.com'
const today = new Date().toISOString().slice(0, 10)

function loadData(rel) {
  const code = fs.readFileSync(path.join(ROOT, rel), 'utf8')
  const ctx = { window: {}, console }
  vm.createContext(ctx)
  vm.runInContext(code, ctx)
  return ctx.window
}

const { ISSUES = [] } = loadData('data/issues.js')
const { WORKS = [] } = loadData('data/works.js')

const urls = []
const add = (loc, lastmod, changefreq, priority) => {
  urls.push({ loc, lastmod, changefreq, priority })
}

// 静态页
;[['', '1.0', 'weekly'], ['archive.html', '0.9', 'weekly'], ['works.html', '0.9', 'weekly'],
  ['about.html', '0.6', 'monthly'], ['shop.html', '0.6', 'weekly'], ['subscribe.html', '0.5', 'monthly'], ['submit.html', '0.5', 'monthly']]
  .forEach(([f, pr, cf]) => add(SITE + '/' + f, today, cf, pr))

// 作品详情（索引即 ?i=）
WORKS.forEach((_, i) => add(`${SITE}/work.html?i=${i}`, '', 'yearly', '0.6'))

// 每期周报与每条报道
ISSUES.forEach((iss) => {
  const d = iss.date || ''
  add(`${SITE}/issue.html?id=${iss.id}`, d, 'weekly', '0.8')
  ;(iss.sections || []).forEach((sec) => {
    ;(sec.items || []).forEach((it) => {
      if (it.id) add(`${SITE}/news.html?id=${it.id}`, d, 'yearly', '0.5')
    })
  })
})

const body = urls.map((u) =>
  `  <url>\n    <loc>${u.loc}</loc>` +
  (u.lastmod ? `\n    <lastmod>${u.lastmod}</lastmod>` : '') +
  `\n    <changefreq>${u.changefreq}</changefreq>\n    <priority>${u.priority}</priority>\n  </url>`
).join('\n')

fs.writeFileSync(
  path.join(ROOT, 'sitemap.xml'),
  `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`,
  'utf8'
)

// robots.txt 里声明 sitemap
const robotsPath = path.join(ROOT, 'robots.txt')
let robots = fs.existsSync(robotsPath) ? fs.readFileSync(robotsPath, 'utf8') : 'User-agent: *\nAllow: /\n'
if (!robots.includes('Sitemap:')) {
  robots = robots.trimEnd() + `\n\nSitemap: ${SITE}/sitemap.xml\n`
  fs.writeFileSync(robotsPath, robots, 'utf8')
}

console.log(`sitemap.xml: ${urls.length} 个地址（静态 6 + 作品 ${WORKS.length} + 期数 ${ISSUES.length}）`)
