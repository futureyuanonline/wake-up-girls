# -*- coding: utf-8 -*-
"""订阅名单管理（方案 C：手工收集）

名单文件：data/subscribers.json（已被 .gitignore 忽略，不会上传到 GitHub）
格式：{"subscribers":[{"email":"a@b.com","lang":"zh-CN","since":"2026-09-18"}]}

用法：
  python tools/subscribers.py list                     列出全部订阅者
  python tools/subscribers.py add a@b.com c@d.com      添加（可一次多个，自动去重与校验）
  python tools/subscribers.py remove a@b.com           移除（退订）
  python tools/subscribers.py bcc                      输出 BCC 收件人（逗号分隔，可直接粘进 Gmail）
  python tools/subscribers.py secret                   输出 SUBSCRIBERS_JSON 的值（粘到 GitHub Secret）
"""
import io
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'subscribers.json')
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$')


def load():
    if not os.path.exists(PATH):
        return []
    try:
        d = json.load(io.open(PATH, encoding='utf-8'))
    except Exception as e:
        sys.exit('名单文件损坏：%s' % e)
    return d.get('subscribers', [])


def save(subs):
    subs = sorted(subs, key=lambda x: x['email'].lower())
    io.open(PATH, 'w', encoding='utf-8', newline='\n').write(
        json.dumps({'subscribers': subs}, ensure_ascii=False, indent=2) + '\n')
    return subs


def cmd_list(_):
    subs = load()
    if not subs:
        print('名单为空。')
        print('提示：读者发邮件订阅后，用这条命令加入：python tools/subscribers.py add 他的邮箱')
        return
    print('共 %d 位订阅者：' % len(subs))
    for i, s in enumerate(subs, 1):
        print('  %2d. %-32s 加入于 %s' % (i, s['email'], s.get('since', '—')))


def cmd_add(args):
    subs = load()
    have = {s['email'].lower() for s in subs}
    added, dup, bad = [], [], []
    for e in args:
        e = e.strip().strip('<>').strip()
        if not EMAIL_RE.match(e):
            bad.append(e)
            continue
        if e.lower() in have:
            dup.append(e)
            continue
        subs.append({'email': e, 'lang': 'zh-CN', 'since': date.today().isoformat()})
        have.add(e.lower())
        added.append(e)
    save(subs)
    print('已添加 %d 位%s%s%s' % (
        len(added),
        ('：' + ', '.join(added)) if added else '',
        ('｜已存在跳过 %d 位' % len(dup)) if dup else '',
        ('｜格式不对 %d 个：%s' % (len(bad), ', '.join(bad))) if bad else ''))
    print('当前共 %d 位订阅者' % len(load()))


def cmd_remove(args):
    subs = load()
    targets = {a.strip().lower() for a in args}
    kept = [s for s in subs if s['email'].lower() not in targets]
    removed = len(subs) - len(kept)
    save(kept)
    print('已移除 %d 位，当前共 %d 位订阅者' % (removed, len(kept)))
    if removed == 0:
        print('（没有匹配到，请确认邮箱拼写；用 list 查看现有名单）')


def cmd_bcc(_):
    subs = load()
    if not subs:
        print('（名单为空，暂时不用发信）')
        return
    print(','.join(s['email'] for s in subs))


def cmd_secret(_):
    subs = load()
    print('把下面这一整行（含大括号）粘到 GitHub → Settings → Secrets and variables → Actions '
          '→ Secrets → New repository secret，Name 填 SUBSCRIBERS_JSON：')
    print()
    print(json.dumps({'subscribers': subs}, ensure_ascii=False, separators=(',', ':')))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, args = sys.argv[1], sys.argv[2:]
    table = {'list': cmd_list, 'add': cmd_add, 'remove': cmd_remove, 'bcc': cmd_bcc, 'secret': cmd_secret}
    if cmd not in table:
        sys.exit('未知命令：%s（可用：%s）' % (cmd, ' / '.join(table)))
    table[cmd](args)


if __name__ == '__main__':
    main()
