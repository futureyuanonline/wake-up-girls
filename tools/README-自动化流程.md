# 每周自动更新流程（全球视角）

## 现状：三个阶段，前两阶段已实现

```
① 采集（已实现·无需任何密钥）      tools/fetch_news.py
   ├─ 10 个地区版 × 当地语言查询（Google News RSS, when:7d）
   │    全球 en-US · 东亚 zh-CN/ja/ko · 东南亚 id-ID/en-PH
   │    南亚 en-IN/en-PK · 中东 ar-EG/en-AE · 非洲 en-NG/en-KE/en-ZA
   │    欧洲 en-GB/es-ES/fr-FR · 北美 en-US/en-CA · 拉美 es-419/pt-BR · 大洋洲 en-AU/en-NZ
   ├─ 3 个女性议题专源（UN News 妇女 / IPS Gender / allAfrica Women）
   ├─ 去重 + 剔除体育财经等噪音 + 只保留近 8 天
   └─ 按地区配额输出（每区最多 3 条，≥7 区）→ drafts/week-YYYY-MM-DD.md / .json

② 成稿（半自动 / 全自动可切换）
   ├─ 半自动：从候选里挑 12–15 条，人工或 AI 撰写「摘要 + 3 段正文 + 英文版」
   └─ 全自动：调用 LLM API（需你的 API Key）生成同一格式 JSON

③ 入库与发布
   ├─ 追加到 data/issues.js
   ├─ node build_i18n.mjs          → 生成繁体版
   └─ 部署静态站（GitHub Pages / Cloudflare Pages / Vercel，可 CI 自动）
```

## 定时运行

| 方式 | 说明 | 前提 |
|---|---|---|
| Windows 任务计划程序 | 每周五 09:00 本机自动跑 `tools/fetch_news.py` | 电脑开机 |
| GitHub Actions（推荐） | 云端 cron，每周五跑采集 + 成稿 + 提交 + 自动部署 | 网站放在 GitHub 仓库 |
| 手动 | 每周五你说一声，我跑采集并成稿 | 无 |

## 全球视角的保障机制

1. **按地区分别查询**：每个地区用当地语言与地区版（不是只看英文/中文源）
2. **地区配额**：每期每地区最多 3 条，至少覆盖 7 个地区
3. **地区字段**：每条新闻带 `region`，站内可筛选
4. **内容优先归类**：先按内容关键词判定所属地区，避免"按查询版号硬塞"

## 质量原则（重要）

- **自动采集 + AI 起草 + 人工复核 + 自动发布** 是推荐组合；
  纯自动发布有事实错误风险（本项目的新闻均需注明来源）。
- 每期发布的正文必须由人（或我）复核来源链接后再上线。
