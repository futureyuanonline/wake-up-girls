# -*- coding: utf-8 -*-
"""生成「可分享视觉包」：二维码 + 微信 / 小红书 / 抖音 三套卡片

用法：python tools/make_share_kit.py
产出：share/ 目录（已 gitignore，属于个人分发素材）
  01-wechat-card.png   1080x1350  朋友圈/微信群：定位 + 本期 3 条 + 二维码
  02-xhs-cover.png     1080x1440  小红书封面
  03-xhs-digest.png    1080x1440  小红书：本周 3 件事（豆瓣式列表）
  04-xhs-watch.png     1080x1440  小红书：本周一位值得认识的女性
  05-xhs-works.png     1080x1440  小红书：她的作品（豆瓣卡片风）
  06-douyin-cover.png  1080x1920  抖音封面（9:16）
  07-douyin-page.png   1080x1920  抖音内容页
  qr.png               二维码（含站内图标，可直接用）
  文案.md              三渠道文案与话题标签
"""
import json
import os
import subprocess
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'share')
SITE = 'https://yuanxiuzhong.com'
FONTS = r'C:\Windows\Fonts'

WALL = (244, 241, 235)
WALL2 = (234, 229, 220)
INK = (29, 23, 21)
INK2 = (90, 79, 73)
INK3 = (138, 122, 114)
GOLD = (225, 182, 42)
BRICK = (161, 38, 39)
CORAL = (220, 135, 111)
TEAL = (14, 117, 135)
TEAL2 = (48, 108, 123)

SERIF = os.path.join(FONTS, 'STSONG.TTF')
SANS = os.path.join(FONTS, 'msyh.ttc')
SANS_B = os.path.join(FONTS, 'msyhbd.ttc')
EN_B = os.path.join(FONTS, 'BOOKOSB.TTF')


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, max_w):
    """CJK 友好换行"""
    lines, cur = [], ''
    for ch in str(text):
        if ch == '\n':
            lines.append(cur); cur = ''; continue
        if d.textlength(cur + ch, font=font) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def draw_par(d, xy, text, font, fill, max_w, line_h=None):
    x, y = xy
    lh = line_h or int(font.size * 1.55)
    for ln in wrap(d, text, font, max_w):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def tracked(d, xy, s, font, fill, sp=6):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + sp
    return x


def new_card(w, h, bg=WALL):
    im = Image.new('RGB', (w, h), bg)
    return im, ImageDraw.Draw(im)


def footer(d, w, h, light=False):
    """页脚：域名 + 字标"""
    col = INK3 if not light else (200, 195, 190)
    f = F(SANS, 30)
    d.text((72, h - 92), 'yuanxiuzhong.com', font=f, fill=col)
    f2 = F(EN_B, 30)
    t = 'WAKE UP GIRLS'
    d.text((w - 72 - d.textlength(t, font=f2), h - 92), t, font=f2, fill=col)


def make_qr(size=560, logo=True):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=12, border=2)
    qr.add_data(SITE)
    qr.make(fit=True)
    img = qr.make_image(fill_color=INK, back_color=WALL).convert('RGB')
    img = img.resize((size, size), Image.NEAREST)
    if logo:
        lp = os.path.join(ROOT, 'assets', 'img', 'logo-180.png')
        if os.path.exists(lp):
            lg = Image.open(lp).convert('RGBA')
            s = int(size * 0.19)
            lg = lg.resize((s, s))
            plate = Image.new('RGBA', (s + 16, s + 16), WALL + (255,))
            img.paste(plate.convert('RGB'), ((size - s) // 2 - 8, (size - s) // 2 - 8))
            img.paste(lg, ((size - s) // 2, (size - s) // 2), lg)
    return img


def load_data():
    files = {
        'issues': os.path.join(ROOT, 'data', 'issues.js'),
        'works': os.path.join(ROOT, 'data', 'works.js'),
        'covers': os.path.join(ROOT, 'data', 'covers.js'),
    }
    script = ('global.window={};'
              + ''.join('require(%s);' % json.dumps(p.replace('\\', '/')) for p in files.values())
              + 'console.log(JSON.stringify({issues:window.ISSUES,works:window.WORKS,covers:window.COVERS}));')
    r = subprocess.run(['node', '-e', script], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        sys.exit('读取数据失败：' + r.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(r.stdout.decode('utf-8'))


DATA = load_data()
ISSUE = DATA['issues'][0]
ITEMS = [it for s in ISSUE.get('sections', []) for it in s.get('items', [])]
WATCH = ISSUE.get('watch') or {}
PICKS = ISSUE.get('picks') or {}
WORKS = DATA['works']
COVERS = DATA['covers']

os.makedirs(OUT, exist_ok=True)


def find_work(title):
    """按标题找作品（返回 作品对象与下标）"""
    for i, w in enumerate(WORKS):
        if w.get('title') == title:
            return w, i
    for i, w in enumerate(WORKS):
        if title and str(title).strip('《》') in str(w.get('title', '')):
            return w, i
    return None, -1


def cover_img(idx, box):
    if idx < 0 or idx >= len(COVERS) or not COVERS[idx]:
        return None
    p = os.path.join(ROOT, COVERS[idx])
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGB')
    im.thumbnail(box)
    return im


# ══════════════════ 01 微信 / 朋友圈卡片（4:5）══════════════════
def card_wechat():
    W, H = 1080, 1350
    im, d = new_card(W, H)
    d.rectangle([W - 150, 0, W, 220], fill=GOLD)
    d.rectangle([0, H - 46, 300, H], fill=BRICK)

    d.text((72, 70), 'WAKE UP', font=F(EN_B, 40), fill=INK)
    d.text((72 + 236, 70), 'GIRLS', font=F(EN_B, 40), fill=BRICK)
    d.text((72 + 380, 80), '全球女性议题周报', font=F(SANS, 26), fill=INK3)

    y = 180
    y = draw_par(d, (72, y), '视角在她，规则由她。', F(SERIF, 86), INK, W - 200, 120)
    d.rectangle([72, y + 6, 72 + 470, y + 24], fill=GOLD)
    y += 60
    y = draw_par(d, (72, y), '记录女性正在经历的世界，也记录女性正在创造的世界。', F(SERIF, 34), INK2, W - 200)
    y += 26

    d.text((72, y), '第 %s 期 · %s' % (ISSUE['id'], ISSUE.get('period', '')), font=F(SANS, 28), fill=INK3)
    y += 66
    d.text((72, y), '本周我挑了 %d 条' % len(ITEMS), font=F(SANS_B, 34), fill=INK)
    y += 62

    for i, it in enumerate(ITEMS[:3], 1):
        d.text((72, y), '%d' % i, font=F(EN_B, 34), fill=BRICK)
        y = draw_par(d, (120, y), it.get('t', ''), F(SANS_B, 33), INK, W - 420, 50)
        y += 18

    qr = make_qr(300)
    im.paste(qr, (W - 72 - 300, H - 150 - 300))
    d.text((W - 72 - 300, H - 150 - 300 + 312), '扫码看本周全部 %d 条' % len(ITEMS),
           font=F(SANS, 26), fill=INK3)
    footer(d, W, H)
    p = os.path.join(OUT, '01-wechat-card.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 02 小红书封面（3:4）══════════════════
def card_xhs_cover():
    W, H = 1080, 1440
    im, d = new_card(W, H)
    d.rectangle([0, 0, W, 16], fill=BRICK)
    d.rectangle([W - 260, 120, W - 80, 400], fill=GOLD)
    d.rectangle([60, H - 380, 200, H - 120], fill=TEAL)

    y = 170
    d.text((72, y), '每周五 · 中文精选', font=F(SANS, 32), fill=BRICK)
    y += 78
    y = draw_par(d, (72, y), '这周，全球女性\n发生了什么？', F(SERIF, 92), INK, W - 150, 126)
    y += 40
    y = draw_par(d, (72, y), '我读完上百条新闻，只挑出这 %d 条。' % len(ITEMS), F(SANS, 40), INK2, W - 200)
    y += 60
    for it in ITEMS[:3]:
        d.text((72, y), '· ' + it.get('t', '')[:22], font=F(SANS, 36), fill=INK2)
        y += 60
    y += 30
    d.text((72, y), '第 %s 期 · %s' % (ISSUE['id'], ISSUE.get('period', '')), font=F(SANS, 28), fill=INK3)
    footer(d, W, H)
    p = os.path.join(OUT, '02-xhs-cover.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 03 小红书：本周 3 件事（豆瓣式列表）══════════════════
def card_xhs_digest():
    W, H = 1080, 1440
    im, d = new_card(W, H)
    d.rectangle([0, 0, 18, 320], fill=GOLD)
    d.text((72, 90), '本周值得知道的 %d 件事' % min(3, len(ITEMS)), font=F(SERIF, 62), fill=INK)
    d.text((72, 182), 'Wake Up Girls 第 %s 期' % ISSUE['id'], font=F(SANS, 30), fill=INK3)

    y = 290
    for i, it in enumerate(ITEMS[:3], 1):
        d.text((72, y), '%02d' % i, font=F(EN_B, 40), fill=BRICK)
        yy = draw_par(d, (140, y), it.get('t', ''), F(SANS_B, 40), INK, W - 280, 58)
        yy += 10
        yy = draw_par(d, (140, yy), it.get('why', ''), F(SANS, 32), INK2, W - 280, 48)
        y = yy + 56
        d.line([(72, y - 26), (W - 72, y - 26)], fill=(224, 219, 210), width=2)
    footer(d, W, H)
    p = os.path.join(OUT, '03-xhs-digest.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 04 小红书：一位值得认识的女性 ══════════════════
def card_xhs_watch():
    W, H = 1080, 1440
    im, d = new_card(W, H, WALL2)
    d.rectangle([0, 0, W, 14], fill=TEAL)
    d.text((72, 84), '本周，一位值得你认识的女性', font=F(SANS_B, 40), fill=TEAL)

    name = WATCH.get('name', '')
    cx = W // 2
    d.ellipse([cx - 150, 200, cx + 150, 500], fill=INK)
    ch = (name or '?')[:1]
    f = F(SERIF, 150)
    w = d.textlength(ch, font=f)
    d.text((cx - w / 2, 250), ch, font=f, fill=GOLD)

    f2 = F(SERIF, 76)
    w2 = d.textlength(name, font=f2)
    d.text((cx - w2 / 2, 550), name, font=f2, fill=INK)

    role = ' · '.join([x for x in [WATCH.get('role', ''), WATCH.get('region', '')] if x])
    f3 = F(SANS, 34)
    w3 = d.textlength(role, font=f3)
    d.text((cx - w3 / 2, 660), role, font=f3, fill=TEAL)

    d.rectangle([cx - 40, 740, cx + 40, 744], fill=GOLD)
    draw_par(d, (110, 800), WATCH.get('why', ''), F(SERIF, 42), INK, W - 220, 76)
    d.text((110, H - 210), '每期一位 · 她可能不是名人', font=F(SANS, 28), fill=INK3)
    footer(d, W, H)
    p = os.path.join(OUT, '04-xhs-watch.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 05 小红书：她的作品（豆瓣卡片风）══════════════════
def card_xhs_works():
    W, H = 1080, 1440
    im, d = new_card(W, H)
    d.rectangle([0, 0, 18, 300], fill=CORAL)
    d.text((72, 84), '本周她的作品', font=F(SERIF, 62), fill=INK)
    d.text((72, 178), '每周 1 电影 · 1 书 · 1 艺术', font=F(SANS, 30), fill=INK3)

    y = 280
    order = [('film', '电影'), ('book', '图书'), ('art', '艺术')]
    for key, label in order:
        title = PICKS.get(key)
        if not title:
            continue
        w, idx = find_work(title)
        box = (190, 250)
        cv = cover_img(idx, box)
        row_h = 260
        if cv:
            # 豆瓣卡片风：左封面、右标题+元信息+短评
            x = 72
            im.paste(cv, (x, y + (row_h - cv.height) // 2))
        tx = 72 + 210
        d.text((tx, y + 10), label, font=F(SANS_B, 28), fill=BRICK)
        yy = draw_par(d, (tx, y + 56), (w or {}).get('title', title), F(SANS_B, 42), INK, W - tx - 90, 58)
        meta = ' · '.join([x for x in [(w or {}).get('creator', ''), str((w or {}).get('year', ''))] if x])
        d.text((tx, yy + 8), meta, font=F(SANS, 30), fill=INK3)
        y += row_h + 30
        d.line([(72, y - 18), (W - 72, y - 18)], fill=(224, 219, 210), width=2)
    footer(d, W, H)
    p = os.path.join(OUT, '05-xhs-works.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 06 抖音封面（9:16）══════════════════
def card_douyin_cover():
    W, H = 1080, 1920
    im, d = new_card(W, H)
    d.rectangle([0, 0, W, 20], fill=BRICK)
    d.rectangle([W - 240, 260, W - 60, 620], fill=GOLD)

    d.text((80, 300), '本周，一位值得', font=F(SERIF, 96), fill=INK)
    d.text((80, 420), '你认识的女性', font=F(SERIF, 96), fill=INK)
    d.rectangle([80, 546, 80 + 520, 566], fill=GOLD)

    name = WATCH.get('name', '')
    f = F(SERIF, 78)
    d.text((80, 660), name, font=f, fill=BRICK)
    role = ' · '.join([x for x in [WATCH.get('role', ''), WATCH.get('region', '')] if x])
    d.text((80, 780), role, font=F(SANS, 40), fill=INK2)

    draw_par(d, (80, 900), (WATCH.get('why', '') or '')[:80] + '…', F(SERIF, 46), INK, W - 200, 84)

    d.text((80, H - 300), '@Wake Up Girls', font=F(SANS_B, 44), fill=INK)
    d.text((80, H - 236), '每周五 · 全球女性议题精选', font=F(SANS, 34), fill=INK3)
    footer(d, W, H)
    p = os.path.join(OUT, '06-douyin-cover.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 07 抖音内容页（9:16，带二维码）══════════════════
def card_douyin_page():
    W, H = 1080, 1920
    im, d = new_card(W, H)
    d.rectangle([0, 0, 14, 420], fill=TEAL)
    d.text((72, 140), '第 %s 期 · %s' % (ISSUE['id'], ISSUE.get('period', '')), font=F(SANS, 32), fill=INK3)
    y = draw_par(d, (72, 210), '本周值得知道的\n%d 件事' % min(3, len(ITEMS)), F(SERIF, 92), INK, W - 200, 118)
    y += 60
    for i, it in enumerate(ITEMS[:3], 1):
        d.text((72, y), '%d' % i, font=F(EN_B, 38), fill=BRICK)
        y = draw_par(d, (126, y), it.get('t', ''), F(SANS_B, 40), INK, W - 260, 56) + 24
    qr = make_qr(420)
    im.paste(qr, ((W - 420) // 2, H - 760))
    t = '扫码看本期全部 %d 条' % len(ITEMS)
    f = F(SANS, 34)
    d.text(((W - d.textlength(t, font=f)) / 2, H - 320), t, font=f, fill=INK2)
    footer(d, W, H)
    p = os.path.join(OUT, '07-douyin-page.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 二维码 ══════════════════
def card_qr():
    q = make_qr(700)
    im, d = new_card(900, 1000)
    im.paste(q, (100, 90))
    t = 'Wake Up Girls · 全球女性议题周报'
    f = F(SANS_B, 36)
    d.text(((900 - d.textlength(t, font=f)) / 2, 830), t, font=f, fill=INK)
    t2 = '视角在她，规则由她。'
    f2 = F(SERIF, 32)
    d.text(((900 - d.textlength(t2, font=f2)) / 2, 890), t2, font=f2, fill=INK3)
    p = os.path.join(OUT, 'qr.png')
    im.save(p, 'PNG', optimize=True)
    return p


# ══════════════════ 文案 ══════════════════
def captions():
    top = ITEMS[:3]
    md = ['# 三渠道分享文案（第 %s 期）' % ISSUE['id'], '',
          '> 图片在 `share/` 目录；文案可直接复制。二维码统一指向 %s' % SITE, '',
          '## 一、发给朋友 / 微信群（配 01-wechat-card.png）', '',
          '我做了个每周更新的东西：**Wake Up Girls 全球女性议题周报**。',
          '每周五，我从全球上百条新闻里挑出 %d 条，写成中文摘要，每条都标了「为什么值得关注」，并且附原始来源。' % len(ITEMS),
          '完全公益、不接广告、免费订阅。这周的内容：', '',
          ]
    for i, it in enumerate(top, 1):
        md.append('%d. %s' % (i, it.get('t', '')))
    md += ['', '完整一期：%s' % SITE, '', '---', '',
           '## 二、小红书（配 02 / 03 / 04 / 05 四张图）', '',
           '**标题（选一个）**',
           '1. 这周，全球女性发生了什么？我挑了 %d 条' % len(ITEMS),
           '2. 我每天读完全球女性新闻，只留下这 %d 条' % len(ITEMS),
           '3. 每周五，我用 %d 条新闻记录女性的世界' % len(ITEMS), '',
           '**正文**', '',
           '每周五更新一期，全部中文整理，每条都有：',
           '· 发生了什么（3 段完整摘要）',
           '· 为什么值得关注（这是我自己写的判断）',
           '· 原始来源链接', '',
           '这周的三个重点：']
    for i, it in enumerate(top, 1):
        md.append('%d. %s —— %s' % (i, it.get('t', ''), it.get('why', '')))
    md += ['', '除了周报，还有一个女性电影 / 图书 / 艺术作品的检索库（160 件，可按国家、年代、主题筛）。',
           '完全公益，不接广告。搜「Wake Up Girls」或 %s' % SITE, '',
           '**话题标签**',
           '#女性议题 #性别平等 #女性主义 #女性力量 #每周书影音 #女性电影 #女性艺术家 #公益项目', '',
           '---', '',
           '## 三、抖音（配 06 / 07 两张图，或做成视频）', '',
           '**封面文字**：本周，一位值得你认识的女性', '',
           '**口播稿（约 45 秒）**', '',
           '（0-5 秒）这周我想介绍一位女性给你认识。',
           '（5-20 秒）%s，%s。%s' % (WATCH.get('name', ''), WATCH.get('role', ''), (WATCH.get('why', '') or '')[:60]),
           '（20-35 秒）这周还有 %d 条全球女性议题新闻，我都写成了中文摘要。' % len(ITEMS),
           '（35-45 秒）每周五更新，完全免费，不收广告。想看的搜 Wake Up Girls。', '',
           '**文案**', '',
           '每周五，%d 条全球女性议题新闻，中文整理 + 我的判断。' % len(ITEMS),
           '不接广告，完全公益。', '',
           '**话题标签**',
           '#女性 #女性力量 #她力量 #性别平等 #女性成长 #人物故事', '',
           '---', '',
           '## 建议发布节奏', '',
           '| 渠道 | 频率 | 内容 |', '|---|---|---|',
           '| 朋友圈 / 微信群 | 每周一次 | 01 卡片 + 一段话 |',
           '| 小红书 | 每周一次（图文 4 张） | 02 封面 + 03 三件事 + 04 人物 + 05 作品 |',
           '| 抖音 | 每周一次 | 06 封面 + 07 内容页，或录 45 秒口播 |', '',
           '> ⚠️ 提醒：社交平台对性别议题审核较严，建议**以人物故事与作品推荐为主**，',
           '> 少评论社会事件、避免外媒截图、不要引导站外链接。']
    p = os.path.join(OUT, '文案.md')
    open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(md))
    return p


if __name__ == '__main__':
    jobs = [card_qr, card_wechat, card_xhs_cover, card_xhs_digest, card_xhs_watch,
            card_xhs_works, card_douyin_cover, card_douyin_page]
    print('生成分享视觉包 → share/')
    for f in jobs:
        p = f()
        print('  %-24s %6.1f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))
    p = captions()
    print('  %-24s %6.1f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))
