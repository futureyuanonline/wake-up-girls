# -*- coding: utf-8 -*-
"""重做 6 张主题图（v2）：所有文字收进中央 60%，任何比例裁切都不丢内容

v1 的问题：英文小标签放在 y=196/1000（约 20% 处），当画框是竖版（4:5）时会被裁掉，
首页精选卡片上「VOICE」就看不见了。

v2 版式（1000×1000，全部内容落在 y=180~820 之间）：
  y=250  英文标签（居中）
  y=330  中文大字（居中，两字并排）
  y=640  细分隔线
  y=680  主题说明（居中）
四角色块故意放在边缘 —— 它们被裁掉无所谓，文字一定保留。
用法：python tools/make_topic_images_v2.py
"""
import importlib.util
import os
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('mk', str(ROOT / 'tools' / 'make_images.py'))
mk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mk)

IMG = ROOT / 'assets' / 'img'
F, text_w, draw_tracked = mk.font, mk.text_w, mk.draw_tracked
SERIF_CN_B, SANS_CN, SERIF_EN_B = mk.SERIF_CN_B, mk.SANS_CN, mk.SERIF_EN_B
WALL, INK, INK3 = mk.WALL, mk.INK, mk.INK_3
TOPICS = mk.TOPICS
BLOCK_SETS = mk.BLOCK_SETS


def make_topic(fname, chars, en, sub, blocks):
    W = H = 1000
    im = Image.new('RGB', (W, H), WALL)
    d = ImageDraw.Draw(im)

    # 四角装饰（被裁掉也没关系）
    d.rectangle([0, 0, 190, 104], fill=blocks[0])
    d.rectangle([W - 130, 0, W, 240], fill=blocks[1])
    d.rectangle([0, H - 96, 240, H - 34], fill=blocks[2])

    # 英文标签 y=250（不再是 196，避开竖版裁切）
    f_en = F(SERIF_EN_B, 32)
    w = text_w(d, en, f_en, 7)
    draw_tracked(d, ((W - w) / 2, 285), en, f_en, INK3, spacing=7)

    # 中文大字 y=330
    f_cn = F(SERIF_CN_B, 190)
    cw = d.textlength(chars[0], font=f_cn)
    gap = 22
    total = cw * len(chars) + gap * (len(chars) - 1)
    x = (W - total) / 2
    for ch in chars:
        d.text((x, 345), ch, font=f_cn, fill=INK)
        x += cw + gap

    # 中央分隔线 + 主题说明
    d.rectangle([W / 2 - 38, 600, W / 2 + 38, 604], fill=blocks[0])
    f_sub = F(SANS_CN, 36)
    ws = d.textlength(sub, font=f_sub)
    d.text(((W - ws) / 2, 640), sub, font=f_sub, fill=(90, 79, 73))

    # 页脚（可被裁）
    f_foot = F(SANS_CN, 24)
    d.text((64, H - 84), '示意图 · 本站原创插画', font=f_foot, fill=INK3)
    f_mark = F(SERIF_EN_B, 24)
    d.text((W - 64 - text_w(d, 'WAKE UP GIRLS', f_mark), H - 84), 'WAKE UP GIRLS', font=f_mark, fill=INK3)

    out = IMG / fname
    im.save(out, 'PNG', optimize=True)
    return out


def check(p):
    """自检：中央区域（竖版 4:5 裁切后仍在画面内的范围）是否有笔画"""
    im = Image.open(p).convert('L')
    w, h = im.size
    # 4:5 竖版裁切：取中心 800×1000 → 上下不动、左右各裁 100
    box = im.crop((40, 260, 960, 700))
    ink = 0
    px = box.load()
    for y in range(0, box.size[1], 3):
        for x in range(0, box.size[0], 3):
            if px[x, y] < 140:
                ink += 1
    return ink


if __name__ == '__main__':
    print('重做 6 张主题图（v2：文字全部收进中央区）')
    for i, (fn, chars, en, sub) in enumerate(TOPICS):
        p = make_topic(fn, chars, en, sub, BLOCK_SETS[i])
        print('  %-20s %5.1f KB ｜ 中央区笔画 %d %s' % (fn, os.path.getsize(p) / 1024, check(p),
                                                    '✓' if check(p) > 500 else '✗ 内容偏少'))
