# 部署与自动出刊 · 配置清单（B/B/B 方案）

你选择的是：**① GitHub Actions 云端定时 ② LLM 自动成稿 ③ 自动发布**，并需要**真实邮件投递**，
网站目标域名：**https://yuanxiuzhong.com/**

> 现状（已核实）：仓库已建好并推送 → <https://github.com/futureyuanonline/wake-up-girls>
> **域名的 DNS 托管在 GoDaddy**（NS = `ns23.domaincontrol.com` / `ns24.domaincontrol.com`），**不在 Cloudflare**，
> 且当前没有 MX 记录。域名现在指向的是之前的 AI 建站 demo。因此第 2 步需要**先把域名接入 Cloudflare**。

---

## 一、需要你操作的步骤（账号级操作，我做不了）

### 1) 仓库 —— ✅ 已完成，无需操作
`main` 分支已推送到 <https://github.com/futureyuanonline/wake-up-girls>（323 个文件）。
本机 git 凭据已从旧账号 `707813244-ui` 切换为 `futureyuanonline`；属于旧账号的其它仓库下次推送会要求重新登录一次。

日常提交：
```bash
cd D:\wake-up-girls
pwsh -File tools\preflight.ps1      # 提交前预检：语法 + 冒烟测试 + 移动端版式
git add -A && git commit -m "..." && git push
```

### 2) 部署到 yuanxiuzhong.com（Cloudflare Pages）

**2.1 先把域名接入 Cloudflare（免费套餐即可）**
1. 注册/登录 <https://dash.cloudflare.com> → **Add a site** → 输入 `yuanxiuzhong.com` → 选 **Free**
2. Cloudflare 会扫描并导入现有 DNS 记录。逐条检查：
   - 指向旧 AI demo 的 A 记录 → **可以删掉**（马上会被 Pages 取代）
   - 如果旧 demo 还挂在某个子域上、你仍想保留 → **保留该子域记录**
   - 目前无 MX 记录，所以迁 NS 不会影响收信
3. Cloudflare 会给你两个 NS（形如 `xxx.ns.cloudflare.com` / `yyy.ns.cloudflare.com`）
4. 到 **GoDaddy** → 我的产品 → 该域名 → **DNS → Nameservers → Change → I'll use my own nameservers**
   → 填入上面那两个 NS → 保存
5. 等待生效（通常几分钟，最长 24 小时）。Cloudflare 后台出现 **Active** 即完成

**2.2 建 Pages 项目**
1. Cloudflare 控制台 → **Workers & Pages → Create → Pages → Connect to Git**
2. 授权 GitHub → 选仓库 `futureyuanonline/wake-up-girls` → 分支 `main`
3. 构建设置（纯静态站，**不需要构建**）：
   | 字段 | 填什么 |
   |---|---|
   | Framework preset | **None** |
   | Build command | **留空** |
   | Build output directory | **`/`**（若界面不接受，改填 `.`） |
4. **Save and Deploy** → 先访问分配到的 `https://wake-up-girls.pages.dev`，确认站点正常（这一步不碰域名，安全）

**2.3 绑定自定义域名**
1. Pages 项目 → **Custom domains → Set up a custom domain**
2. 输入 `yuanxiuzhong.com` → Cloudflare 自动创建 DNS 记录并签发免费证书
3. 再添加 `www.yuanxiuzhong.com`
4. 建议把 `www` 301 跳到裸域（或反之），避免两个地址内容重复：Pages 项目里加 **Redirect Rules**，
   或用仓库里的 `_redirects` 文件

**2.4 验证**
```powershell
nslookup -type=ns yuanxiuzhong.com 1.1.1.1     # 应显示 *.ns.cloudflare.com
curl.exe -I https://yuanxiuzhong.com           # 应为 200，且 server: cloudflare
```
> 注意：你本机有代理会把 DNS 解析成 `198.18.x.x`（fake-IP），所以**本机 `Resolve-DnsName` 看到的地址不可信**，
> 用上面的 `1.1.1.1` 直查，或到 <https://dnschecker.org> 查。

**替代方案（不迁 NS）**：在 Cloudflare 之外托管 DNS 时，只能较顺地给 `www` 加 CNAME → `wake-up-girls.pages.dev`；
裸域 `yuanxiuzhong.com` 需要 DNS 商支持 CNAME 展平（GoDaddy 不支持），只能靠转发，不推荐。
将来 `news@yuanxiuzhong.com` 要发信（Resend 的 SPF/DKIM）也是迁到 Cloudflare 后一次配好最省事。

### 3) 大模型 API Key（成稿用）
任选其一并在 GitHub 仓库 **Settings → Secrets and variables → Actions** 里配置：

| 类型 | Secret | Variable | 说明 |
|---|---|---|---|
| DeepSeek | `LLM_API_KEY` | `LLM_BASE_URL=https://api.deepseek.com/v1`<br>`LLM_MODEL=deepseek-chat` | 便宜、中文好 |
| OpenAI | `LLM_API_KEY` | `LLM_BASE_URL=https://api.openai.com/v1`<br>`LLM_MODEL=gpt-4o-mini` | 英文更好 |
| 其他兼容接口 | `LLM_API_KEY` | `LLM_BASE_URL` / `LLM_MODEL` | 只要兼容 `/chat/completions` |

> ⚠️ 定时任务是**每周五 09:00（北京时间）**。密钥没配好之前它会失败并给你发失败邮件，
> 建议先在 **Actions → Weekly Issue → ⋯ → Disable workflow** 关掉，配好密钥再启用。

### 4) 邮件服务（真实投递用）
推荐 **Resend**（对开发者友好，每月 3000 封免费）：
1. 注册 resend.com → **Domains → Add domain** → 填 `yuanxiuzhong.com`，按提示加 2 条 DNS 记录（SPF/DKIM）
   （域名迁到 Cloudflare 后，这些记录直接在 Cloudflare 里加）
2. 创建 **API Key** → 配置到 GitHub Secret：`MAIL_API_KEY`
3. 配置 Variable：`MAIL_FROM = Wake Up Girls <news@yuanxiuzhong.com>`、`SITE_URL = https://yuanxiuzhong.com`
4. 用 SendGrid 也可以：额外设 `MAIL_PROVIDER = sendgrid`

### 5) 订阅名单怎么来
`data/subscribers.json` 已设为**不入库**（含邮箱属隐私数据，公开仓库不应提交），格式见
`data/subscribers.example.json`。要收集真实订阅者，三选一：
- **A. Buttondown / Substack 托管订阅**（最省事）：订阅表单交给它们，投递也由它们做，
  我们的 `send_newsletter.py` 就不需要跑了
- **B. Resend + 自建表单**：表单用 Cloudflare Worker、腾讯问卷等收集 → 写回 `subscribers.json`
- **C. 暂时手工**：把邮箱加到 `data/subscribers.json` 里（该文件不会被提交）

> 首次跑流水线前先手动创建 `data/subscribers.json`（内容 `{"subscribers":[]}`），否则发信步骤会打印
> 「未找到 data/subscribers.json，跳过投递」——这是预期行为，不算失败。

---

## 二、已经建好的部分（无需你操作）

| 文件 | 作用 |
|---|---|
| `.github/workflows/weekly-issue.yml` | 每周五 09:00（北京时间）自动跑全流程，也可手动触发；已声明 `permissions: contents: write` |
| `tools/fetch_news.py` | ① 采集：10 个地区 × 当地语言 + 3 个女性议题专源，去重/筛相关/地区配额 → `drafts/` |
| `tools/generate_issue.py` | ② 成稿：调用 LLM 生成中文正文 + 英文版，**校验不通过则拒绝发布**（条目<10、地区<7、单区>3、字段缺失、链接异常） |
| `tools/send_newsletter.py` | ⑤ 投递：Resend / SendGrid 发 HTML 邮件（无名单则跳过，缺密钥则报错） |
| `build_i18n.mjs` | ③ 繁简同步（opencc） |
| `404.html` / `_headers` / `robots.txt` | Cloudflare Pages 用的 404 页、缓存与安全响应头、抓取规则 |
| `tools/preflight.ps1` | 提交前预检：JS 语法 + 渲染后冒烟测试（10 页）+ 移动端 320–1280 版式审计 |
| `tools/mobile-check.ps1` | 移动端专项自检（横向溢出 / 触控目标 AA 达标） |
| `.gitattributes` | 仓库内统一 LF，避免 Windows 上产生成片换行符差异 |

**流水线**：采集 → LLM 成稿（含校验）→ 繁简同步 → 提交（自动触发 Cloudflare Pages 部署）→ 邮件投递

## 三、质量与安全护栏（已内置）

1. **不让 LLM 编造**：提示词明确"只能基于候选信息与常识，禁止编造数字与机构"，并保留原始来源链接
2. **发布前硬校验**：地区数/条目数/字段/链接任一不达标 → 退出且不提交
3. **全球视角强制**：每期至少 7 个地区、单地区最多 3 条
4. **来源可追溯**：每条新闻都带 `src` 与 `url`，报道页结尾自动注明原文来源
5. **配图不涉版权**：自动出刊使用站内原创海报/示意图，图注标注"示意图"
6. **隐私**：订阅者邮箱 `data/subscribers.json` 不入库；仓库内无任何硬编码密钥（全部走 `secrets.*`）

## 四、上线前必须处理的一件事：图片版权

站内现有 **160 张海报 + 115 张封面**，其中封面多来自豆瓣、部分来自 Wikimedia。
本地预览无所谓，但**挂到公开域名后就属于公开发布**，豆瓣封面/剧照是有版权风险的。三个选项：

- **A. 换成自由许可图片**：Wikimedia Commons 等（可保留 115 张里已来自 Commons 的部分，其余替换）
- **B. 用站内生成的色块海报**：`posters.js` 已支持占位海报，风格统一且完全无版权风险
- **C. 维持现状**：仅标注来源，承担被投诉/要求下架的风险

告诉我选哪个，我来批量处理。
