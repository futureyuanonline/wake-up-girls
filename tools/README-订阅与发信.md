# 订阅与发信 · 操作手册（方案 C：手工收集与发送）

> 现状：网站订阅页是**一键预填邮件**（读者点一下，邮件主题与正文已写好，只需按发送）。
> 你自己收信 → 加入名单 → 每周用工具生成一封邮件，粘进 Gmail 发送。
> 全部零成本、零配置；订阅者超过几十人再考虑升级（见文末）。

---

## 一、读者怎么订阅（无需你操作）

订阅页 <https://yuanxiuzhong.com/subscribe> 上：

1. 读者填入自己的邮箱 → 点「一键订阅（邮件已预填）」
2. 他的邮件程序打开，**主题和正文已经写好**（主题：订阅 Wake Up Girls 周报；正文：我的邮箱：xxx）
3. 他按发送 → 你的 `futureyuan39@gmail.com` 收到

页面上还有**隐私说明**与**退订说明**（合规必需），不用你额外解释。

---

## 二、收到订阅邮件后：加入名单

```powershell
cd D:\wake-up-girls
python tools\subscribers.py add 读者的邮箱
```

一次加多个就空格隔开；会自动去重、校验收件地址格式。

| 命令 | 作用 |
|---|---|
| `python tools\subscribers.py list` | 查看全部订阅者（含加入日期） |
| `python tools\subscribers.py add a@b.com c@d.com` | 添加（自动去重与校验） |
| `python tools\subscribers.py remove a@b.com` | 移除（有人退订时用） |
| `python tools\subscribers.py bcc` | 输出密送名单（逗号分隔，直接粘 Gmail） |
| `python tools\subscribers.py secret` | 输出 `SUBSCRIBERS_JSON` 的值（将来升级自动化时粘到 GitHub Secret） |

名单存在 `data/subscribers.json`，**已被 .gitignore 忽略**（含邮箱，属隐私数据，不会上传 GitHub）。

---

## 三、每周发信（约 2 分钟）

```powershell
python tools\make_newsletter_email.py
```

会生成 `outbox/<日期>-issue-<期号>.txt`，里面分三段，照着复制即可：

```
① 主题   → 粘到 Gmail「主题」
② 正文   → 粘到 Gmail 正文
③ 密送   → 粘到 Gmail「密送」（订阅者互相看不到彼此的邮箱）
```

邮件内容是自动从最新一期生成的：3 条看点（标题 + 摘要 + **为什么值得关注** + 站内链接）
+ 本周人物 + 她的作品 + 完整一期入口 + 退订说明。

> `outbox/` 同样已被 gitignore（含收件人邮箱）。

---

## 四、以后要升级成「自动发信」时

现在的瓶颈只有两个，都补齐即可全自动（每周五随周报一起发）：

| 缺什么 | 怎么补 |
|---|---|
| 发信服务 | 注册 [Resend](https://resend.com)（每月 3000 封免费）→ 给它验证域名 `yuanxiuzhong.com`（加 SPF/DKIM 记录，我可以带你做）→ 拿到 API Key |
| 名单进 CI | `python tools\subscribers.py secret` 复制输出 → 粘到 GitHub Secret `SUBSCRIBERS_JSON` |

之后在 GitHub 加两个配置即可：Secret `MAIL_API_KEY`、Variable `MAIL_FROM`。
流水线里发信步骤已经写好（`tools/send_newsletter.py`），**配好即自动生效，无需改代码**。

---

## 五、或者换成托管服务（最省事）

如果嫌手工发信麻烦，也可以把订阅交给 [Buttondown](https://buttondown.com)（免费 100 人）等托管服务：
收集、投递、退订全托管，网站的订阅入口指向它即可（我可以 20 分钟改完）。

**注意**：国内读者用邮件的比例较低，邮件订阅更适合「愿意留邮箱的忠实读者」；
面向大众的渠道建议仍以社交平台为主。
