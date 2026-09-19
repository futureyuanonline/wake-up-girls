# -*- coding: utf-8 -*-
"""生成一页纸的网站架构图 → docs/架构图.png
用法：python tools/make_architecture.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs')
FONTS = r'C:\Windows\Fonts'

WALL = (244, 241, 235)
INK = (29, 23, 21)
INK2 = (90, 79, 73)
INK3 = (138, 122, 114)
GOLD = (225, 182, 42)
GOLD_L = (250, 243, 219)
BRICK = (161, 38, 39)
BRICK_L = (250, 236, 235)
TEAL = (14, 117, 135)
TEAL_L = (228, 243, 245)
CORAL = (220, 135, 111)
CORAL_L = (252, 240, 236)
LINE = (214, 208, 198)

SERIF = os.path.join(FONTS, 'STSONG.TTF')
SANS = os.path.join(FONTS, 'msyh.ttc')
SANS_B = os.path.join(FONTS, 'msyhbd.ttc')
EN_B = os.path.join(FONTS, 'BOOKOSB.TTF')


def F(p, s):
    return ImageFont.truetype(p, s)


def box(d, xy, title, lines, accent, light, tf=F(SANS_B, 30), lf=F(SANS, 25)):
    x, y, w, h = xy
    d.rounded_rectangle([x, y, x + w, y + h], 10, fill=light, outline=accent, width=3)
    d.rectangle([x, y, x + 8, y + h], fill=accent)
    d.text((x + 28, y + 18), title, font=tf, fill=INK)
    yy = y + 18 + 44
    for ln in lines:
        d.text((x + 28, yy), ln, font=lf, fill=INK2)
        yy += 36


def arrow(d, x, y1, y2, accent=INK3, label=''):
    d.line([(x, y1), (x, y2 - 16)], fill=accent, width=4)
    d.polygon([(x - 11, y2 - 18), (x + 11, y2 - 18), (x, y2)], fill=accent)
    if label:
        f = F(SANS, 24)
        d.text((x + 18, (y1 + y2) / 2 - 16), label, font=f, fill=accent)


def main():
    W, H = 1680, 1290
    im = Image.new('RGB', (W, H), WALL)
    d = ImageDraw.Draw(im)

    d.rectangle([0, 0, W, 14], fill=BRICK)
    d.text((64, 54), 'Wake Up Girls', font=F(EN_B, 46), fill=INK)
    d.text((64 + 372, 64), '全球女性议题周报 · 网站架构', font=F(SANS_B, 34), fill=BRICK)
    d.text((64, 118), 'yuanxiuzhong.com ｜纯静态站：无数据库、无服务器运维，每周五自动出刊', font=F(SANS, 26), fill=INK3)

    # ── 第一层：读者与页面 ──
    box(d, (64, 176, 1552, 200), '① 读者看到的（10 个页面 · 三语 简体/繁體/English · 手机与桌面自适应）',
        ['首页（本周精选 + 她的作品 + 一位值得认识的女性）',
         '往期 　　单期周报（每条：摘要 + 3 段正文 + 为什么值得关注 + 原文来源）',
         '作品检索库（160 件：电影 63 / 图书 56 / 艺术 31 / 专题 10）',
         '可按类型 · 地区 · 年代 · 首字母筛选　｜　作品详情 · 关于 · 订阅 · 投稿 · 404'],
        BRICK, BRICK_L)

    # ── 第二层：静态数据与资源 ──
    y2 = 400
    box(d, (64, y2, 760, 250), '② 数据层 data/（纯 JS 文件，随页面一起加载）',
        ['issues.js / issues.hant.js　每期周报（含英文版）',
         'works.js / works.hant.js / works_en.js　160 件作品',
         'posters.js　原创海报 160 张 ｜ covers.js　真实封面 115 张',
         'initials.js　拼音首字母 ｜ notes.js　策展人手记（暂空）'],
        GOLD, GOLD_L)
    box(d, (856, y2, 760, 250), '③ 资源层 assets/',
        ['css/style.css　全站样式（浅色画廊色板 + 移动端适配）',
         'js/app.js　三语切换 + 全部页面渲染',
         'img/　海报与封面（WebP，共 6 MB）＋ 6 张原创主题图',
         'img/og-cover.jpg　社交分享封面'],
        CORAL, CORAL_L)

    # ── 第三层：每周自动出刊 ──
    y3 = 690
    d.rounded_rectangle([64, y3, 1616, y3 + 300], 12, fill=TEAL_L, outline=TEAL, width=3)
    d.rectangle([64, y3, 72, y3 + 300], fill=TEAL)
    d.text((96, y3 + 18), '④ 每周五 09:00 自动出刊（GitHub Actions 云端，无需你操作）',
           font=F(SANS_B, 30), fill=INK)
    steps = [
        ('采集', ['tools/fetch_news.py', '10 个地区 × 当地语言', '＋ 3 个女性议题专源', '→ 约 26–30 条候选']),
        ('成稿', ['tools/generate_issue.py', 'LLM 写中文正文 + 英文', '「为什么值得关注」3 句备选', '→ 校验不通过就拒绝发布']),
        ('同步', ['node build_i18n.mjs', 'opencc 自动转繁体', '→ issues/works 繁体版']),
        ('发布', ['git commit + push', 'Cloudflare 自动部署', '→ 30 秒后线上生效', 'sitemap 同步更新']),
    ]
    sw, gap = 356, 20
    for i, (t, ls) in enumerate(steps):
        x = 96 + i * (sw + gap)
        d.rounded_rectangle([x, y3 + 66, x + sw, y3 + 272], 10, fill=(255, 255, 255), outline=TEAL, width=2)
        d.text((x + 20, y3 + 82), '%d. %s' % (i + 1, t), font=F(SANS_B, 28), fill=TEAL)
        yy = y3 + 130
        for ln in ls:
            d.text((x + 20, yy), ln, font=F(SANS, 23), fill=INK2)
            yy += 32
        if i < 3:
            d.polygon([(x + sw + 4, y3 + 160), (x + sw + gap - 4, y3 + 169), (x + sw + 4, y3 + 178)], fill=TEAL)

    # ── 第四层：部署与访问链路 ──
    y4 = 1020
    chain = [
        ('本地开发', 'D:\\wake-up-girls', BRICK, BRICK_L),
        ('GitHub 仓库', 'futureyuanonline/wake-up-girls', INK, (238, 236, 233)),
        ('Cloudflare Worker', '静态资源（dist/ 白名单构建）', TEAL, TEAL_L),
        ('线上站点', 'yuanxiuzhong.com', GOLD, GOLD_L),
    ]
    cw = 356
    for i, (t, s, ac, lg) in enumerate(chain):
        x = 96 + i * (cw + gap)
        d.rounded_rectangle([x, y4, x + cw, y4 + 96], 10, fill=lg, outline=ac, width=2)
        d.text((x + 20, y4 + 18), t, font=F(SANS_B, 27), fill=ac)
        d.text((x + 20, y4 + 54), s, font=F(SANS, 22), fill=INK2)
        if i < 3:
            d.polygon([(x + cw + 4, y4 + 40), (x + cw + gap - 4, y4 + 48), (x + cw + 4, y4 + 56)], fill=INK3)
    d.text((96, y4 + 112), '⑤ 质量保障：tools/preflight.ps1 —— 语法 + 出刊脚本回归测试 + 10 页冒烟 + 320–1280 五档版式',
           font=F(SANS, 23), fill=INK3)
    d.text((96, y4 + 146), '　　　　　另：tools/mobile-check.ps1（移动端专项）　｜　tools/make_share_kit.py（分享视觉包：二维码 + 微信/小红书/抖音）',
           font=F(SANS, 23), fill=INK3)

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, '架构图.png')
    im.save(p, 'PNG', optimize=True)
    print('已生成：docs/架构图.png  %.0f KB' % (os.path.getsize(p) / 1024))


if __name__ == '__main__':
    main()
