# -*- coding: utf-8 -*-
"""每周「知乎发文包」生成器
读取最新一期 data/issues.js，挑 3 条可讨论的条目，生成：
  · 3 个问题建议（可直接搜现成问题，或自建）
  · 3 篇答案草稿（结论 → 事实 → 意义 → 来源 → 刊物介绍 + UTM 链接）
  · 话题标签、发布检查清单
输出：drafts/zhihu-<期号>.md
用法：python tools/make_zhihu_pack.py [--issue 008]
"""
import argparse
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://yuanxiuzhong.com'

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


def load_issues():
    path = os.path.join(ROOT, 'data', 'issues.js')
    txt = io.open(path, encoding='utf-8').read()
    m = re.search(r'window\.ISSUES\s*=\s*(\[[\s\S]*\])\s*;', txt)
    if not m:
        sys.exit('无法解析 data/issues.js')
    return json.loads(m.group(1))


# 优先挑：政策/法律/国际/职场，且带明确国家或地区
PREFER_CATS = ('政策与法律', '国际', '职场平等', '生育权利')
INTEREST_KW = ('法案', '判决', '判決', '禁令', '禁止', '抗议', '抗議', '遇害', '被杀', '性骚扰', '性侵',
               '工资', '薪酬', '堕胎', '堕胎权', '配额', '罢工', '起诉', '诉讼', '道歉', '辞职',
               '禁令', '签证', '难民', '家暴', '童婚', '割礼', '就业', '同工同酬')
BORING_KW = ('召开', '举行', '研讨', '座谈会', '交流会', '启动仪式', '揭牌')


def score(item, cat):
    s = 0
    if cat in PREFER_CATS:
        s += 3
    if item.get('region'):
        s += 1
    d = (item.get('d') or '')
    if len(d) >= 30:
        s += 1
    if item.get('src'):
        s += 1
    text = (item.get('t') or '') + (item.get('d') or '')
    s += sum(2 for k in INTEREST_KW if k in text)
    s -= sum(3 for k in BORING_KW if k in text)
    return s


def norm_title(t):
    return re.sub(r'^[《“"]|[》”"]$', '', (t or '').strip())


def build_answer(item, cat, issue, idx):
    title = norm_title(item.get('t'))
    region = item.get('region') or ''
    src = item.get('src') or ''
    url = item.get('url') or ''
    desc = (item.get('d') or '').strip()
    body = item.get('body') or []
    if isinstance(body, str):
        body = [body]
    utm = ('%s/i/%s?utm_source=zhihu&utm_medium=answer&utm_campaign=issue%s_%d'
           % (SITE, issue.get('id'), issue.get('id'), idx))

    lines = []
    lines.append('> 说明：以下为草稿，发布前请按自己的判断改写成口语，并核对事实与来源。')
    lines.append('')
    lines.append('## 问题建议（二选一）')
    lines.append('')
    lines.append('1. **如何看待「%s」？（%s）**' % (title, region))
    lines.append('2. **%s发生了什么？这对当地女性意味着什么？**' % (region or '这件事'))
    lines.append('')
    lines.append('> 发布前先在知乎搜一下：如果已有高浏览的同类问题，直接答那个（蹭现成流量）；没有就自建问题。')
    lines.append('')
    lines.append('## 答案草稿（约 700 字，按自己的话改）')
    lines.append('')
    CONCL = {
        '政策与法律': '关键不在「说了什么」，而在「预算和执行有没有跟上」。',
        '职场平等': '同一个制度，对资源不同的人效果完全不同——这才是差距所在。',
        '生育权利': '争的从来不是「要不要」，而是「谁有资格决定」。',
        '国际': '这类跨国呼声的影响，往往不在当天，而在它给本地行动者提供了什么依据。',
        '健康与权益': '这类议题最容易被说成「个人选择」，但真正的变量是制度给不给条件。',
    }
    concl = CONCL.get(cat, '表象是一条新闻，实质是「谁有条件做出不同选择」的问题。')
    lines.append('**一句话结论**')
    lines.append('')
    lines.append('%s%s' % (title, '。' if not title.endswith(('。', '？', '！')) else '') + concl)
    lines.append('')
    lines.append('**发生了什么**')
    lines.append('')
    if desc:
        lines.append(desc)
        lines.append('')
    for p in body[:3]:
        p = re.sub(r'\s+', ' ', str(p)).strip()
        if p:
            lines.append(p)
            lines.append('')
    lines.append('**为什么值得关注**')
    lines.append('')
    if item.get('why'):
        lines.append(item['why'])
    else:
        lines.append('（此处补 2–3 句你自己的判断：它改了什么、没改什么、卡在哪一环。）')
    lines.append('')
    lines.append('**资料来源**')
    lines.append('')
    gm = '（Google News 跳转链接，发布前请点开取原始媒体网址）' if 'news.google.com' in (url or '') else ''
    lines.append('- %s：%s%s' % (src or '原始报道', url or '（补链接）', gm))
    lines.append('')
    lines.append('**我在做什么（文末一句，不硬推）**')
    lines.append('')
    lines.append('我在做一份全球女性议题周报，每周从 10 个地区、用当地语言的公开来源采集，'
                 '写成中文摘要并附原始链接，也会标出「这条不能推出什么」。这期在这里：%s' % utm)
    lines.append('')
    lines.append('---')
    lines.append('')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--issue', default='', help='指定期号，默认最新一期')
    args = ap.parse_args()

    issues = load_issues()
    if not issues:
        sys.exit('没有期号数据')
    issue = issues[0]
    if args.issue:
        hit = [i for i in issues if str(i.get('id')) == args.issue]
        if hit:
            issue = hit[0]

    flat = []
    for sec in issue.get('sections') or []:
        for it in sec.get('items') or []:
            flat.append((score(it, sec.get('cat')), it, sec.get('cat')))

    flat.sort(key=lambda x: -x[0])
    picks = flat[:3]
    if not picks:
        sys.exit('本期没有可用条目')

    out = []
    out.append('# 知乎发文包 · 第 %s 期（%s）' % (issue.get('id'), issue.get('period')))
    out.append('')
    out.append('> 用途：每周从这一期里挑一条，去知乎答一个现成问题。')
    out.append('> 原则：① 不做政治评判，只讲事实与当地女性的实际处境；')
    out.append('> ② 一篇只放 1 次刊物链接（放多了会被判导流）；③ 先答 2–3 篇不带链接的建立账号权重。')
    out.append('')
    out.append('## 发布检查清单')
    out.append('')
    for c in ['搜一下有没有现成的高浏览问题（优先答现成的）',
              '把「一句话结论」改成你自己的语气，不要像通稿',
              '核对来源链接能打开、机构名与数字无误',
              '话题标签建议：#女性权益 #性别平等 #国际新闻 #社会观察（选 2–3 个即可）',
              '发布后把链接记到推广表，下次复盘看它带来多少 UV']:
        out.append('- [ ] ' + c)
    out.append('')

    for n, (sc, item, cat) in enumerate(picks, 1):
        out.append('=' * 60)
        out.append('')
        out.append('# 候选 %d（%s / %s）' % (n, cat, item.get('region') or '—'))
        out.append('')
        out.append(build_answer(item, cat, issue, n))

    path = os.path.join(ROOT, 'drafts', 'zhihu-%s.md' % issue.get('id'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print('已生成：%s（本期 %d 条，选 3 条）' % (path, len(flat)))
    for n, (sc, item, cat) in enumerate(picks, 1):
        print('  候选%d：[%s] %s' % (n, cat, norm_title(item.get('t'))[:40]))


if __name__ == '__main__':
    main()
