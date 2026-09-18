# -*- coding: utf-8 -*-
"""生成站内原创图（替换 6 张来源不明的抓取图）+ 社交分享封面

为什么：原 6 张 PNG 是从网上抓的、连出处都查不到，是站内版权风险最高的一类；
        og:image（分享封面）也必须有图，否则分享到微信/小红书没有缩略图。

风格：复用站内色板与版式（米白墙 + 色块 + 华文宋体标题 + 页脚标记），与 160 张原创海报一致。

用法：python tools/make_images.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img')

WALL = (244, 241, 235)
INK = (29, 23, 21)
INK_3 = (138, 122, 114)
GOLD = (225, 182, 42)
BRICK = (161, 38, 39)
CORAL = (220, 135, 111)
TEAL = (14, 117, 135)
TEAL2 = (48, 108, 123)

SERIF_CN = r'C:\Windows\Fonts\STSONG.TTF'          # 华文宋体（正文附注）
SERIF_CN_B = r'C:\Windows\Fonts\STSONG.TTF'        # 华文宋体（实测可正常渲染；simsunb.ttf 会出空方框，禁用）
SERIF_EN_B = r'C:\Windows\Fonts\BOOKOSB.TTF'       # Bookman Old Style Bold
SANS_CN = r'C:\Windows\Fonts\msyh.ttc'             # 微软雅黑


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f, spacing=0):
    if spacing <= 0:
        return draw.textlength(s, font=f)
    return draw.textlength(s, font=f) + spacing * (len(s) - 1)


def draw_tracked(draw, xy, s, f, fill, spacing=0):
    """字距可控的文本绘制（英文小标签用）。"""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + spacing


# ── 6 张主题图（4:3，1200×900；CSS 用 object-fit 裁成 16:9 / 1:1 都不变形）──
TOPICS = [
    ('women-power.png',  ['在', '场'],   'PRESENCE',          '女性与公共空间'),
    ('womens-rights.png', ['权', '利'],  'RIGHTS',            '权益与法律'),
    ('vote.png',         ['投', '票'],   'THE VOTE',          '政治参与'),
    ('podium.png',       ['发', '声'],   'VOICE',             '国际治理与领导力'),
    ('body-choice.png',  ['身', '体'],   'BODILY AUTONOMY',   '身体自主与健康'),
    ('workplace.png',    ['劳', '动'],   'LABOUR',            '职场与经济'),
]
BLOCK_SETS = [
    (GOLD, BRICK, TEAL), (BRICK, TEAL, GOLD), (TEAL, GOLD, CORAL),
    (CORAL, TEAL2, GOLD), (GOLD, TEAL, BRICK), (BRICK, GOLD, TEAL2),
]


def make_topic(fname, chars, en, sub, blocks):
    W, H = 1200, 900
    im = Image.new('RGB', (W, H), WALL)
    d = ImageDraw.Draw(im)

    # 色块构图（右上两个、左下一条）
    d.rectangle([W - 300, 0, W - 90, 210], fill=blocks[0])
    d.rectangle([W - 78, 0, W, 300], fill=blocks[1])
    d.rectangle([0, H - 96, 340, H - 30], fill=blocks[2])

    # 英文小标签
    f_en = font(SERIF_EN_B, 30)
    draw_tracked(d, (86, 250), en, f_en, INK_3, spacing=6)

    # 中文大字（竖排式两字，主视觉）
    f_cn = font(SERIF_CN_B, 210)
    for i, ch in enumerate(chars):
        d.text((80, 300 + i * 230), ch, font=f_cn, fill=INK)

    # 主题说明
    f_sub = font(SANS_CN, 34)
    d.text((400, 700), sub, font=f_sub, fill=(90, 79, 73))

    # 页脚标记
    f_foot = font(SANS_CN, 24)
    d.text((86, H - 74), '示意图 · 本站原创插画', font=f_foot, fill=INK_3)
    d.text((W - 300, H - 74), 'WAKE UP GIRLS', font=font(SERIF_EN_B, 24), fill=INK_3)

    out = os.path.join(IMG, fname)
    im.save(out, 'PNG', optimize=True)
    return out


# ── 社交分享封面（1200×630，og:image 标准尺寸）──
def make_share_card():
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), WALL)
    d = ImageDraw.Draw(im)

    d.rectangle([W - 150, 0, W, 150], fill=GOLD)
    d.rectangle([0, H - 40, 220, H], fill=BRICK)
    d.rectangle([W - 260, H - 40, W, H], fill=TEAL)

    d.text((72, 66), 'WAKE UP', font=font(SERIF_EN_B, 34), fill=INK)
    d.text((72 + 210, 66), 'GIRLS', font=font(SERIF_EN_B, 34), fill=BRICK)
    d.text((72 + 330, 74), '全球女性议题周报', font=font(SANS_CN, 22), fill=INK_3)

    f_head = font(SERIF_CN_B, 96)
    d.text((72, 172), '视角在她，', font=f_head, fill=INK)
    y2 = 172 + 118
    d.text((72, y2), '规则由她。', font=f_head, fill=INK)
    # 金色下划线块
    d.rectangle([72, y2 + 118, 72 + text_w(d, '规则由她。', f_head), y2 + 118 + 26], fill=GOLD)

    d.text((72, 452), '记录女性正在经历的世界，也记录女性正在创造的世界。',
           font=font(SERIF_CN, 30), fill=(90, 79, 73))
    d.text((72, 524), 'yuanxiuzhong.com', font=font(SERIF_EN_B, 26), fill=BRICK)

    out = os.path.join(IMG, 'og-cover.jpg')
    im.save(out, 'JPEG', quality=90, optimize=True)
    return out


if __name__ == '__main__':
    print('生成 6 张原创主题图（就地替换原抓取图，文件名不变，站内引用无需改动）：')
    for i, (fn, chars, en, sub) in enumerate(TOPICS):
        p = make_topic(fn, chars, en, sub, BLOCK_SETS[i])
        print('  %-20s %5.1f KB' % (fn, os.path.getsize(p) / 1024))
    p = make_share_card()
    print('社交分享封面：%-16s %5.1f KB' % ('og-cover.jpg', os.path.getsize(p) / 1024))
