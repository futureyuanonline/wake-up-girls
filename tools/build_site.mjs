/* 组装发布目录 dist/ —— Cloudflare 的 Build command 就是跑本脚本。
 *
 * 为什么需要它：Worker 项目用 px wrangler deploy\ 发布，若把仓库根目录直接当静态资源目录，
 * 实测 wrangler 会读入 1619 个文件（含 .git 全部历史对象与 node_modules），
 * 既臃肿又会把仓库历史公开出去。所以这里用**白名单**：只把网站该公开的文件复制到 dist/。
 *
 * Cloudflare 项目设置里填：Build command = node tools/build_site.mjs
 *                          Deploy command = npx wrangler deploy
 *                          Root directory = /
 *
 * 用法（本地核对发布清单）：node tools/build_site.mjs  然后起服务看 dist/
 */
import { cp, mkdir, rm, stat, readdir, copyFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const DIST = path.join(ROOT, 'dist')

/* 要发布的单文件（存在才复制） */
const FILES = [
  'index.html', 'archive.html', 'issue.html', 'news.html',
  'works.html', 'work.html', 'about.html', 'subscribe.html', 'submit.html', 'shop.html', 'detail.html',
  '404.html', '_headers', '_redirects', 'robots.txt', 'sitemap.xml',
]

/* 要整目录发布的资源 */
const DIRS = ['assets', 'data']

/* 绝不发布的文件（隐私） */
const NEVER = ['data/subscribers.json']

async function dirSize(p) {
  let total = 0, n = 0
  for (const e of await readdir(p, { withFileTypes: true })) {
    const full = path.join(p, e.name)
    if (e.isDirectory()) { const r = await dirSize(full); total += r.total; n += r.n }
    else { total += (await stat(full)).size; n++ }
  }
  return { total, n }
}

await rm(DIST, { recursive: true, force: true })
await mkdir(DIST, { recursive: true })

const missing = []
for (const f of FILES) {
  const src = path.join(ROOT, f)
  if (existsSync(src)) await copyFile(src, path.join(DIST, f))
  else missing.push(f)
}

const excluded = []
for (const d of DIRS) {
  const src = path.join(ROOT, d)
  if (!existsSync(src)) { missing.push(d + '/'); continue }
  await cp(src, path.join(DIST, d), { recursive: true })
  // 目录内逐个剔除隐私文件
  for (const priv of NEVER) {
    if (priv.startsWith(d + '/')) {
      const p = path.join(DIST, priv)
      if (existsSync(p)) { await rm(p, { force: true }); excluded.push(priv) }
    }
  }
}

const { total, n } = await dirSize(DIST)
console.log(`构建完成 → dist/`)
console.log(`  文件数：${n}   体积：${(total / 1024 / 1024).toFixed(1)} MB`)
if (missing.length) console.log(`  跳过（源文件不存在）：${missing.join(', ')}`)
if (excluded.length) console.log(`  已剔除隐私文件：${excluded.join(', ')}`)

/* 健全性检查：没有首页就别发布了 */
if (!existsSync(path.join(DIST, 'index.html'))) {
  console.error('✗ dist/index.html 不存在，构建失败')
  process.exit(1)
}
if (!existsSync(path.join(DIST, 'assets/css/style.css'))) {
  console.error('✗ dist/assets/css/style.css 不存在，构建失败')
  process.exit(1)
}
console.log('  ✓ 首页与样式表齐备')
