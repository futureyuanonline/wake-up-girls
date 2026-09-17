# Wake Up Girls — 全球女性议题周报（本地版）

公益信息类网站：每周全球女性议题新闻精选（站内完整报道）+ 女性电影/图书/艺术作品检索库。
设计语言「浅色画廊 + 大胆色块」：暖白墙 `#F4F1EB`、墨黑 `#1D1715`、芥末黄 `#E1B62A`、砖红 `#A12627`、珊瑚粉 `#DC876F`、青绿 `#0E7587`；
标题 Playfair Display + Noto Serif SC，正文 Inter + 系统黑体；三语切换（EN / 简 / 繁）；全站响应式，已适配手机端。

## 目录结构
```
wake-up-girls/
├── index.html        首页（最新一期摘要 + 作品推荐）
├── archive.html      往期周报列表
├── issue.html        单期详情（?id=001）
├── news.html         站内完整报道页（?id=001-1 … 001-15，结尾注明来源）
├── works.html        作品检索库（搜索 + 分类筛选）
├── work.html         作品详情页（?id=《作品名》，含豆瓣/百科/公版下载链接）
├── about.html        关于项目 / 主理人
├── subscribe.html    订阅页（演示版 mailto 表单）
├── submit.html       投稿与勘误页
├── assets/css/style.css   全局样式（浅色画廊色板 + 全站响应式，末尾为「移动端适配」段落）
├── assets/js/app.js       三语切换 + 全部渲染逻辑 + 移动端菜单交互
├── assets/img/            配图、海报 posters/、封面 covers/、网站图标 logo*
├── data/
│   ├── issues.js          周报数据（简体，含 en 英文版与 body 正文）
│   ├── issues.hant.js     周报数据（繁体，由 build_i18n.mjs 自动生成）
│   ├── works.js           作品库（简体，160 条）
│   ├── works.hant.js      作品库（繁体，自动生成）
│   ├── works_en.js        作品英文名映射 + 公版下载链接（Project Gutenberg）
│   ├── posters.js         海报路径（按作品下标对齐）
│   ├── covers.js          真实封面路径（按作品下标对齐）
│   ├── initials.js        拼音首字母（字母筛选用）
│   └── subscribers.json   订阅者列表（自动化发信用）
├── build_i18n.mjs         繁体数据生成脚本（node build_i18n.mjs）
├── tools/                 采集/生成/发信脚本 + 移动端自检工具（见 README-*）
│   ├── mobile-check.ps1           一条命令的移动端自检
│   ├── mobile-audit.html          逐元素检测页（iframe 定宽加载 9 个页面）
│   ├── viewport-preview.html      指定宽度的预览页（配合截图）
│   └── patch_mobile.py            批量补 head 元信息与移动端菜单入口
├── .github/workflows/weekly-issue.yml   每周五自动更新周报（见 tools/README-自动化流程.md）
└── node_modules/          opencc-js（仅构建用，发布时不需要）
```

## 本地预览
方式一：`python -m http.server 8765` 后打开 http://localhost:8765
方式二：直接双击 `index.html`

手机端预览（按真实视口宽度渲染，不受桌面窗口最小宽度影响）：
`http://localhost:8765/tools/viewport-preview.html?p=index.html&w=375&h=1400`，
可选参数 `menu=1`（展开汉堡菜单后截图）、`scroll=600`（滚动到指定位置）。

## 移动端适配

断点与规则（全部写在 `assets/css/style.css` 末尾「移动端适配」段落）：

| 断点 | 主要变化 |
|---|---|
| ≤900px | 顶栏改汉堡菜单（下拉整行可点，末尾含「订阅周刊」金色按钮）；语言按钮 40×40；首屏单列、照片 4:3；三列网格降两列；本周精选右侧条目改横滑（吸附滚动）；文章缩略图由浮动改整行；表单/筛选控件整宽、字号 ≥16px（避免 iOS 聚焦放大） |
| ≤640px | 顶栏隐藏 CTA（入口收进下拉菜单）；海报墙 2 列；卡片、页脚、关于页全部单列；首屏按钮竖排整宽 |
| ≤400px | 品牌字号 16px、语言按钮 36×38，保证 320px 窄屏仍不横向溢出 |
| 横屏矮屏 | 压缩首屏高度，标题 26px |
| 触屏设备 | 去掉 hover 位移，改为按压反馈（`:active`） |

无障碍与手势：折叠菜单支持点链接/点空白/ESC/转桌面宽度自动收起，并带 `aria-expanded`；
作品卡、精选小格、本周精选大卡均为「整卡可点」（覆盖层技术），手机上不必点中一行文字。

自检（一条命令，跑 320/375/414/768/1280 五档视口，逐元素查横向溢出与触控目标）：
```powershell
pwsh -File tools\mobile-check.ps1                    # 默认五档
pwsh -File tools\mobile-check.ps1 -Widths 390,430    # 自定义
```
判定标准：横向溢出 0 处；触控目标不出现 WCAG 2.5.8 AA（<24px）不达标项。
桌面端（>900px）保持原有排版尺度，未做触控放大。

> 注意：不要用 `msedge --headless --window-size=375` 判断手机端效果——Windows 下窗口有最小宽度，
> 页面会按更宽的视口布局再被裁切，读数与截图都失真；必须用 `tools/viewport-preview.html` 这类
> iframe 定宽方式，或 `tools/mobile-check.ps1`。

## 每周更新周报（四步）
1. 打开 `data/issues.js`，复制一个期对象，改 `id`/`date`/`period`/`title`/`summary`；
2. 每条新闻填：`id`（如 "002-1"）、`t`/`d`/`body[]`（简体全文，3 段左右）、`en:{t,d,body}`（英文版）、`src`/`url`（来源）、`region`（地区）、`img`（配图路径，如 `assets/img/vote.png`；不填则自动显示主题占位图）；
3. 运行 `node build_i18n.mjs` 生成繁体版；
4. 刷新浏览器。首页自动取最新一期，摘要每分类取 1 条（保证全球地区覆盖）。

## 配图
现有素材库（`assets/img/`）：
| 文件 | 内容 | 适用主题 |
|---|---|---|
| `workplace.png` | 女性职场协作 | 职场平等、就业 |
| `vote.png` | 投票主题拼贴 | 政治参与、权利 |
| `podium.png` | 女性在讲台发言 | 国际治理、领导力 |
| `womens-rights.png` | WOMEN'S RIGHTS 海报 | 综合/权益（也用作首页与周报封面） |
| `women-power.png` | WOMEN POWER 游行标语 | 倡导、抗议、社会运动 |
| `body-choice.png` | MY BODY MY CHOICE | 生育权利、身体自主 |

新增配图：把图片放进 `assets/img/`，在对应新闻条目里加 `img: "assets/img/文件名.png"` 即可。
注意：配图均标注「示意图」，正式发布时请替换为已获授权或自有版权的图片。

## 往作品库添加条目
`data/works.js` 复制对象修改（`c`/`title`/`creator`/`year`/`country`/`d`/`a`/`tags`）；
英文名加在 `data/works_en.js`；公版作品把免费下载链接加进 `PD_LINKS`。
改动后运行 `node build_i18n.mjs`。

## 发布（待定）
静态站，可部署到任意静态托管（GitHub Pages / Cloudflare Pages / Vercel / 腾讯云 COS 等）。
发布时不需要 node_modules；订阅表单上线后接入邮件服务。
