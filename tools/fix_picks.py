# -*- coding: utf-8 -*-
"""picks 去重：同一个作品不得跨期重复推荐

背景：出刊提示词里已写了「最近几期推荐过的禁止再选」，但那只是**建议**，模型不一定听；
实测出现了同一本书/同一位艺术家在 002、003、006、007 被反复推荐。

规则
  * 以「期号升序」为时间顺序，**先发布的先用**：早的那期保留，晚的重复项被替换；
  * 只有「重复」才替换，其余字段一律不动；
  * 替换池 = 站内作品库中同类、且从未被任何一期选过的作品；
    优先取有奖项（a 字段）的，其次取年份更近的；
  * 找不到可用替代时保留原样并告警（不静默丢弃）。

用法
  python tools/fix_picks.py --dry-run
  python tools/fix_picks.py --min-id 007        # 只修 007 及之后（不动已发出的历史）
  python tools/fix_picks.py                     # 全部（幂等）
"""
import argparse
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISSUES = os.path.join(ROOT, 'data', 'issues.js')
WORKS = os.path.join(ROOT, 'data', 'works.js')

TYPES = [('film', 'film'), ('book', 'book'), ('art', 'art')]   # picks 键 → works.c


def load_js_window(path, var):
    """issues.js 是 JSON 兼容的；works.js 是 JS 对象字面量，必须用 node 解析。"""
    txt = open(path, encoding='utf-8').read()
    m = re.search(var + r'\s*=\s*(\[[\s\S]*\])\s*;', txt)
    if not m:
        raise SystemExit('无法解析 %s' % path)
    try:
        return txt, m.start(1), m.end(1), json.loads(m.group(1))
    except json.JSONDecodeError:
        data = load_via_node(path, var.replace('window.', ''))
        return txt, m.start(1), m.end(1), data


def load_via_node(path, var):
    js = ('global.window={};require(%s);console.log(JSON.stringify(window.%s||[]));'
          % (json.dumps(path.replace('\\', '/')), var))
    r = subprocess.run(['node', '-e', js], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit('node 解析 %s 失败：%s' % (path, r.stderr.decode('utf-8', 'replace')[:300]))
    return json.loads(r.stdout.decode('utf-8'))


def norm(s):
    return re.sub(r'[《》〈〉「」『』\s·・]', '', str(s or ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--min-id', default='', help='只修这个期号及之后的期（历史不动）')
    args = ap.parse_args()

    itxt, istart, iend, issues = load_js_window(ISSUES, 'window.ISSUES')
    _, _, _, works = load_js_window(WORKS, 'window.WORKS')

    # 期号升序处理，先发布者优先
    order = sorted(range(len(issues)), key=lambda i: str(issues[i].get('id', '')))
    used = {'film': set(), 'book': set(), 'art': set()}
    by_type = {'film': [], 'book': [], 'art': []}
    for w in works:
        if w.get('c') in by_type:
            by_type[w['c']].append(w)
    for t in by_type:
        by_type[t].sort(key=lambda w: (1 if w.get('a') else 0, w.get('year') or 0), reverse=True)

    changes = []
    for i in order:
        iss = issues[i]
        pk = iss.get('picks') or {}
        if str(iss.get('id', '')) < args.min_id:
            for key, _ in TYPES:                       # 历史期：只登记占用，不改
                if pk.get(key):
                    used[key].add(norm(pk[key]))
            continue
        new_pk = dict(pk)
        for key, ctype in TYPES:
            val = pk.get(key)
            if not val:
                continue
            if norm(val) not in used[key]:
                used[key].add(norm(val))
                continue
            repl = next((w for w in by_type[ctype]
                         if norm(w.get('title')) not in used[key]), None)
            if not repl:
                print('⚠ 第 %s 期 %s：找不到可替换的 %s' % (iss.get('id'), key, ctype))
                continue
            new_title = str(repl.get('title') or '').strip('《》')
            changes.append((iss.get('id'), key, val, new_title,
                            repl.get('a') or '—', repl.get('year')))
            used[key].add(norm(new_title))
            new_pk[key] = new_title
        if new_pk != pk:
            iss['picks'] = new_pk

    if not changes:
        print('没有发现跨期重复的 picks ✓')
        return

    print('需要替换 %d 处：' % len(changes))
    for cid, key, old, new, award, year in changes:
        print('  第 %s 期 %-4s %s → %s（%s，%s）' % (cid, key, old, new, award, year))

    if args.dry_run:
        print('\n（dry-run，未写入）')
        return

    body = json.dumps(issues, ensure_ascii=False, indent=2)
    with open(ISSUES, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(itxt[:istart] + body + itxt[iend:])
    print('\n✓ 已写回 data/issues.js')


if __name__ == '__main__':
    main()
