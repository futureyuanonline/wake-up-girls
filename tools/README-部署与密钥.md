# 部署与自动出刊 · 配置清单（B/B/B 方案）

你选择的是：**① GitHub Actions 云端定时 ② LLM 自动成稿 ③ 自动发布**，并需要**真实邮件投递**，
网站目标域名：**https://yuanxiuzhong.com/**

---

## 一、需要你操作的 5 步（我做不了账号级操作）

### 1) 把网站放进 GitHub 仓库
在 GitHub 新建仓库（建议名 `wake-up-girls`，**Private 或 Public 均可**），然后本地执行：
```bash
cd D:\wake-up-girls
git init
git add .
git commit -m "init: Wake Up Girls 站点与自动出刊流水线"
git branch -M main
git remote add origin https://github.com/<你的用户名>/wake-up-girls.git
git push -u origin main
```

### 2) 部署到 yuanxiuzhong.com（Cloudflare Pages，推荐）
你的域名已在 Cloudflare 托管，所以用 Pages 最省事：
1. Cloudflare 控制台 → **Workers & Pages → Create → Pages → Connect to Git** → 选择上面那个仓库
2. 构建设置：**Framework preset = None**，Build command 留空，**Build output directory = `/`**（纯静态站，无需构建）
3. 部署完成后 → **Custom domains → 添加 `yuanxiuzhong.com` 和 `www.yuanxiuzhong.com`**（CF 会自动改 DNS）
4. ⚠️ 注意：当前 `yuanxiuzhong.com` 指向的是之前 AI 建站工具的 demo，接通后会被**替换为本站**

> 若你更想用 GitHub Pages：仓库 Settings → Pages → Source = Deploy from branch (main / root)，
> 然后在 Cloudflare DNS 里把 `yuanxiuzhong.com` 指向 GitHub Pages 的 CNAME。

### 3) 大模型 API Key（成稿用）
任选其一并在 GitHub 仓库 **Settings → Secrets and variables → Actions** 里配置：

| 类型 | Secret | Variable | 说明 |
|---|---|---|---|
| DeepSeek | `LLM_API_KEY` | `LLM_BASE_URL=https://api.deepseek.com/v1`<br>`LLM_MODEL=deepseek-chat` | 便宜、中文好 |
| OpenAI | `LLM_API_KEY` | `LLM_BASE_URL=https://api.openai.com/v1`<br>`LLM_MODEL=gpt-4o-mini` | 英文更好 |
| 其他兼容接口 | `LLM_API_KEY` | `LLM_BASE_URL` / `LLM_MODEL` | 只要兼容 `/chat/completions` |

### 4) 邮件服务（真实投递用）
推荐 **Resend**（对开发者友好，每月 3000 封免费）：
1. 注册 resend.com → **Domains → Add domain** → 填 `yuanxiuzhong.com`，按提示加 2 条 DNS 记录（SPF/DKIM）
2. 创建 **API Key** → 配置到 GitHub Secret：`MAIL_API_KEY`
3. 配置 Variable：`MAIL_FROM = Wake Up Girls <news@yuanxiuzhong.com>`、`SITE_URL = https://yuanxiuzhong.com`
4. 用 SendGrid 也可以：额外设 `MAIL_PROVIDER = sendgrid`

### 5) 订阅名单怎么来
当前 `data/subscribers.json` 是手工维护（空）。要收集真实订阅者，三选一：
- **A. Buttondown / Substack 托管订阅**（最省事）：订阅表单交给它们，投递也由它们做，
  我们的 `send_newsletter.py` 就不需要跑了
- **B. Resend + 自建表单**：表单用 Cloudflare Worker 或腾讯问卷收集 → 写入 subscribers.json（需要一点开发）
- **C. 暂时手工**：把邮箱加到 `data/subscribers.json` 里

---

## 二、已经建好的部分（无需你操作）

| 文件 | 作用 |
|---|---|
| `.github/workflows/weekly-issue.yml` | 每周五 09:00（北京时间）自动跑全流程，也可手动触发 |
| `tools/fetch_news.py` | ① 采集：10 个地区 × 当地语言 + 3 个女性议题专源，去重/筛相关/地区配额 → `drafts/` |
| `tools/generate_issue.py` | ② 成稿：调用 LLM 生成中文正文 + 英文版，**校验不通过则拒绝发布**（条目<10、地区<7、单区>3、字段缺失、链接异常） |
| `tools/send_newsletter.py` | ⑤ 投递：Resend / SendGrid 发 HTML 邮件（无名单则跳过，缺密钥则报错） |
| `build_i18n.mjs` | ③ 繁简同步（opencc） |
| `.gitignore` | 排除 node_modules、drafts、临时脚本 |

**流水线**：采集 → LLM 成稿（含校验）→ 繁简同步 → 提交（自动触发 Cloudflare Pages 部署）→ 邮件投递

## 三、质量与安全护栏（已内置）

1. **不让 LLM 编造**：提示词明确"只能基于候选信息与常识，禁止编造数字与机构"，并保留原始来源链接
2. **发布前硬校验**：地区数/条目数/字段/链接任一不达标 → 退出且不提交
3. **全球视角强制**：每期至少 7 个地区、单地区最多 3 条
4. **来源可追溯**：每条新闻都带 `src` 与 `url`，报道页结尾自动注明原文来源
5. **配图不涉版权**：自动出刊使用站内原创海报/示意图，图注标注"示意图"
