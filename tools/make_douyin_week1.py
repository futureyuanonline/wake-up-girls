# -*- coding: utf-8 -*-
"""抖音推广素材：网站满一周（2026-09-23）
产出 share/douyin-week1/ ：5 张竖版图（1080×1920）+ 文案.md（含口播稿）
用法：python tools/make_douyin_week1.py
"""
import importlib.util
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 复用分享包的绘图与数据工具（该模块有 __main__ 保护，导入不会触发生成）
spec = importlib.util.spec_from_file_location('kit', str(ROOT / 'tools' / 'make_share_kit.py'))
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)

OUT = ROOT / 'share' / 'douyin-week1'
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
F = kit.F
esc = lambda x: str(x)
SERIF, SANS, SANS_B, EN_B = kit.SERIF, kit.SANS, kit.SANS_B, kit.EN_B
INK, INK2, INK3 = kit.INK, kit.INK2, kit.INK3
WALL, WALL2 = kit.WALL, kit.WALL2
GOLD, BRICK, CORAL, TEAL, TEAL2 = kit.GOLD, kit.BRICK, kit.CORAL, kit.TEAL, kit.TEAL2

ISSUE = kit.ISSUE
ITEMS = kit.ITEMS
WORKS = kit.WORKS
COVERS = kit.COVERS
find_work, cover_img = kit.find_work, kit.cover_img

CNT_FILM = len([w for w in WORKS if w.get('c') == 'film'])
CNT_BOOK = len([w for w in WORKS if w.get('c') == 'book'])
CNT_ART = len([w for w in WORKS if w.get('c') == 'art'])
CNT_THEME = len([w for w in WORKS if w.get('c') == 'theme'])
TOTAL_ITEMS = len(ITEMS) + 15          # 002 期 10 条 + 001 创刊号 15 条


def card(fn, draw_fn):
    im, d = kit.new_card(W, H)
    draw_fn(im, d)
    p = OUT / fn
    im.save(p, 'PNG', optimize=True)
    return p


def c1_cover(im, d):
    d.rectangle([0, 0, W, 18], fill=BRICK)
    d.rectangle([W - 220, 300, W - 60, 640], fill=GOLD)
    d.rectangle([0, H - 300, 150, H - 120], fill=TEAL)
    d.text((72, 150), 'WAKE UP', font=F(EN_B, 46), fill=INK)
    d.text((72 + 270, 150), 'GIRLS', font=F(EN_B, 46), fill=BRICK)
    d.text((72 + 430, 162), '全球女性议题周报', font=F(SANS, 28), fill=INK3)

    kit.draw_par(d, (72, 330), '我的小网站', F(SERIF, 100), INK, W - 300, 130)
    kit.draw_par(d, (72, 460), '今天满一周了', F(SERIF, 100), INK, W - 300, 130)
    d.rectangle([72, 610, 72 + 560, 634], fill=GOLD)

    kit.draw_par(d, (72, 700), '一个人，一台电脑，一周。', F(SANS_B, 48), INK2, W - 200, 70)
    kit.draw_par(d, (72, 790), '每周挑 10 条全球女性议题，写成中文；', F(SANS, 40), INK2, W - 200, 62)
    kit.draw_par(d, (72, 850), '再建一个 160 件女性作品的库。', F(SANS, 40), INK2, W - 200, 62)

    y = 1010
    for label, val in [('上线', '7 天'), ('周报', '2 期'), ('新闻', '%d 条' % TOTAL_ITEMS), ('作品', '%d 件' % len(WORKS))]:
        d.text((72, y), label, font=F(SANS, 30), fill=INK3)
        d.text((72, y + 40), val, font=F(SERIF, 62), fill=BRICK)
        y += 150
        if y > 1600:
            break

    d.text((72, H - 190), 'yuanxiuzhong.com', font=F(EN_B, 34), fill=INK2)
    d.text((72, H - 130), '链接在我的主页', font=F(SANS_B, 36), fill=BRICK)


def c2_digest(im, d):
    d.rectangle([0, 0, 20, 420], fill=GOLD)
    d.text((72, 140), '这一周，我挑了这些', font=F(SERIF, 66), fill=INK)
    d.text((72, 235), '第 %s 期 · %s' % (ISSUE['id'], ISSUE.get('period', '')), font=F(SANS, 30), fill=INK3)
    y = 340
    for i, it in enumerate(ITEMS[:4], 1):
        d.text((72, y), '%02d' % i, font=F(EN_B, 40), fill=BRICK)
        y = kit.draw_par(d, (150, y), it.get('t', ''), F(SANS_B, 42), INK, W - 220, 60) + 14
        y = kit.draw_par(d, (150, y), it.get('why', ''), F(SANS, 32), INK2, W - 220, 48) + 46
        d.line([(72, y - 24), (W - 72, y - 24)], fill=(224, 219, 210), width=2)
    d.text((72, H - 150), '每周五更新 · 全部免费 · yuanxiuzhong.com', font=F(SANS, 30), fill=INK3)


def c3_works(im, d):
    d.rectangle([0, 0, 20, 420], fill=CORAL)
    d.text((72, 140), '160 件女性作品', font=F(SERIF, 66), fill=INK)
    d.text((72, 240), '电影 %d · 图书 %d · 艺术 %d · 主题 %d' % (CNT_FILM, CNT_BOOK, CNT_ART, CNT_THEME),
           font=F(SANS, 30), fill=INK3)
    picks = [('film', '电影'), ('book', '图书'), ('art', '艺术')]
    y = 350
    for key, label in picks:
        title = (ISSUE.get('picks') or {}).get(key)
        w, idx = find_work(title) if title else (None, -1)
        cv = cover_img(idx, (220, 300))
        if cv:
            im.paste(cv, (72, y + (300 - cv.height) // 2))
        tx = 72 + 250
        d.text((tx, y + 20), label, font=F(SANS_B, 30), fill=BRICK)
        yy = kit.draw_par(d, (tx, y + 70), (w or {}).get('title', title or ''), F(SANS_B, 46), INK, W - tx - 90, 62)
        meta = ' · '.join([x for x in [(w or {}).get('creator', ''), str((w or {}).get('year', ''))] if x])
        d.text((tx, yy + 10), meta, font=F(SANS, 32), fill=INK3)
        y += 360
    d.text((72, H - 160), '可按类型 / 地区 / 年代筛选 · 链接在主页', font=F(SANS, 30), fill=INK3)


def c4_detail(im, d):
    d.rectangle([0, 0, W, 16], fill=TEAL)
    d.text((72, 150), '新栏目：细节', font=F(SANS_B, 42), fill=TEAL)
    kit.draw_par(d, (72, 250), '每期一个问题，\n把它拆到可核查的细节里',
                 F(SERIF, 76), INK, W - 160, 104)
    d.rectangle([72, 520, 72 + 420, 542], fill=GOLD)
    kit.draw_par(d, (72, 620), '第一期的问题是：', F(SANS, 36), INK3, W - 200, 56)
    kit.draw_par(d, (72, 700), '女性在艺术史里\n缺失了什么？', F(SERIF, 82), BRICK, W - 160, 112)
    kit.draw_par(d, (72, 980),
                 '不喊口号。先把"缺失"拆成可以核查的几层：\n'
                 '缺在藏品里？叙事里？市场里？还是档案里？',
                 F(SANS, 34), INK2, W - 180, 56)
    kit.draw_par(d, (72, 1220), '（第一期正在写，欢迎来看进度）', F(SANS, 30), INK3, W - 200, 50)
    d.text((72, H - 150), 'yuanxiuzhong.com · 链接在主页', font=F(SANS, 30), fill=INK3)


def c5_end(im, d):
    d.rectangle([0, 0, W, 18], fill=BRICK)
    kit.draw_par(d, (72, 170), '谢谢你看到这里', F(SERIF, 76), INK, W - 160, 104)
    kit.draw_par(d, (72, 300),
                 '这个网站叫 Wake Up Girls，\n是我一个人做的公益项目：\n不接广告，不接政治赞助。',
                 F(SANS, 38), INK2, W - 160, 62)
    kit.draw_par(d, (72, 520), '视角在她，规则由她。', F(SERIF, 60), BRICK, W - 160, 84)
    kit.draw_par(d, (72, 640),
                 '记录女性正在经历的世界，\n也记录女性正在创造的世界。',
                 F(SANS, 36), INK2, W - 160, 58)
    qr = kit.make_qr(460)
    im.paste(qr, ((W - 460) // 2, 900))
    t = '扫码或点主页链接'
    f = F(SANS_B, 40)
    d.text(((W - d.textlength(t, font=f)) / 2, 1420), t, font=f, fill=INK)
    t2 = 'yuanxiuzhong.com'
    f2 = F(EN_B, 36)
    d.text(((W - d.textlength(t2, font=f2)) / 2, 1490), t2, font=f2, fill=BRICK)
    kit.draw_par(d, (110, 1600), '如果你是女性创作者、研究者或公益从业者，欢迎来信——'
                                 '投稿、指正、或只是说一句你希望这里有什么。', F(SANS, 30), INK3, W - 220, 48)


CAPTION = f'''# 抖音推广素材 · 网站满一周（2026-09-23）

> 图片在 `share/douyin-week1/`（5 张，1080×1920 竖版）
> 发布方式：抖音图文（选这 5 张按顺序）或做成视频（配口播稿）

---

## 一、标题（选一个）

1. 我做了一个只讲女性的网站，今天满一周了
2. 一个人，一周，2 期周报 25 条新闻 160 件女性作品
3. 这个网站今天满一周：我用一周时间，把全球女性议题搬进了中文世界

---

## 二、正文（复制直接用）

一周前，我做了一个小网站。

每周从全球挑 10 条女性议题新闻，写成中文摘要，**每条都标上"为什么值得关注"**——一句读完就能知道它跟你有什么关系。
还建了一个库：{CNT_FILM} 部女性导演的电影、{CNT_BOOK} 本女作家的书、{CNT_ART} 位女艺术家的作品，一共 {len(WORKS)} 件。
今天它满一周了 🎂

一周里它长出了这些：
· 2 期周报，共 {TOTAL_ITEMS} 条全球女性议题
· 一个 {len(WORKS)} 件的作品检索库（可按类型/地区/年代筛）
· 一个新栏目「细节」：每期一个问题，把它拆到可核查的细节里
· 简体 / 繁體 / English 三语

全部免费，不接广告，不接政治赞助。
链接在我的主页，欢迎来看，也欢迎骂我哪里做得不对。

---

## 三、话题标签

#女性 #她力量 #女性成长 #女性主义 #女性力量 #性别平等 #个人项目 #独立开发 #网站上线 #女性电影 #女性艺术家 #书单推荐

---

## 四、口播稿（约 45 秒，如果做成视频）

（0-5 秒）
我做了一个只讲女性的网站，今天满一周了。

（5-18 秒）
每周，我从全球挑 10 条女性议题新闻，写成中文，每条后面都有一句我自己写的"为什么值得关注"。

（18-30 秒）
还建了一个库，{len(WORKS)} 件作品——{CNT_FILM} 部女性导演的电影、{CNT_BOOK} 本女作家的书、{CNT_ART} 位女艺术家的作品，可以按地区、年代筛。

（30-40 秒）
新开了一个栏目叫「细节」，第一期的问题是：女性在艺术史里缺失了什么？不喊口号，只把问题拆到能核查的细节。

（40-45 秒）
完全免费，不接广告。链接在我的主页，来看。

---

## 五、发布小提示

- 前 3 秒最关键：**直接说"我做了一个只讲女性的网站，今天满一周"**，不要绕
- 图文发布时把 5 张图按顺序放好（01 封面 → 02 周报 → 03 作品 → 04 细节 → 05 结尾）
- 抖音对性别议题审核较严：**这条文案已避开敏感表述**，以"个人项目 + 数据 + 人物/作品"为主
- 有评论问链接就回复"主页有"，不要在评论里贴网址（会被限流）
- 发布后把数据（播放/点赞/涨粉）截图发我，我据此调整下一批内容
'''


if __name__ == '__main__':
    jobs = [('01-cover.png', c1_cover), ('02-digest.png', c2_digest),
            ('03-works.png', c3_works), ('04-detail.png', c4_detail),
            ('05-end.png', c5_end)]
    print('生成抖音一周推广素材 → share/douyin-week1/')
    for fn, dfn in jobs:
        p = card(fn, dfn)
        print('  %-18s %6.1f KB' % (fn, os.path.getsize(p) / 1024))
    (OUT / '文案.md').write_text(CAPTION, encoding='utf-8', newline='\n')
    print('  %-18s %6.1f KB' % ('文案.md', os.path.getsize(OUT / '文案.md') / 1024))
