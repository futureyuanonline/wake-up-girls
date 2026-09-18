# -*- coding: utf-8 -*-
"""生成一封「可直接发送」的周报邮件（方案 C：手工发送）

产出文件 outbox/<日期>-issue-<期号>.txt，里面分三段，照着复制即可：
  ① 主题    → 粘到 Gmail 的「主题」
  ② 正文    → 粘到 Gmail 正文
  ③ BCC     → 粘到 Gmail 的密送（订阅者之间互相看不到彼此邮箱）

用法：
  python tools/make_newsletter_email.py            # 用最新一期
  python tools/make_newsletter_email.py 001        # 指定期号
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://yuanxiuzhong.com'


def load_issues():
    """用 node 读取 data/issues.js（它是 JS 文件，不是 JSON）"""
    import subprocess
    js = os.path.join(ROOT, 'data', 'issues.js')
    script = 'global.window={};require(%s);console.log(JSON.stringify(window.ISSUES||[]));' % json.dumps(js.replace('\\', '/'))
    out = subprocess.run(['node', '-e', script], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        sys.exit('读取 issues.js 失败：' + out.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(out.stdout.decode('utf-8'))


def load_subs():
    p = os.path.join(ROOT, 'data', 'subscribers.json')
    if not os.path.exists(p):
        return []
    return json.load(io.open(p, encoding='utf-8')).get('subscribers', [])


def main():
    issues = load_issues()
    if not issues:
        sys.exit('没有期数据')
    want = sys.argv[1] if len(sys.argv) > 1 else None
    issue = next((i for i in issues if i.get('id') == want), issues[0]) if want else issues[0]

    items = [it for s in issue.get('sections', []) for it in s.get('items', [])]
    lead = items[:3]                       # 邮件里只放 3 条亮点，其余引导到站内
    watch = issue.get('watch') or {}

    subject = 'Wake Up Girls 周报 · 第 %s 期｜%s' % (issue['id'], issue.get('title', ''))
    lines = []
    lines.append('本周全球女性议题，我挑了 %d 条。' % len(items))
    lines.append('')
    lines.append('【本期看点】')
    for i, it in enumerate(lead, 1):
        lines.append('%d. %s' % (i, it.get('t', '')))
        lines.append('   %s' % (it.get('d', '') or '')[:90])
        if it.get('why'):
            lines.append('   为什么值得关注：%s' % it['why'])
        lines.append('   %s/news.html?id=%s' % (SITE, it.get('id', '')))
        lines.append('')
    if watch.get('name'):
        lines.append('【本周，一位值得你认识的女性】')
        lines.append('%s（%s）' % (watch['name'], watch.get('role', '')))
        lines.append(watch.get('why', ''))
        lines.append('')
    if issue.get('picks'):
        p = issue['picks']
        lines.append('【她的作品】每周 1 电影 + 1 书 + 1 艺术')
        for k, label in (('film', '电影'), ('book', '图书'), ('art', '艺术')):
            if p.get(k):
                lines.append('· %s：%s' % (label, p[k]))
        lines.append('')
    lines.append('完整一期（%d 条 + 全文摘要）：%s/issue.html?id=%s' % (len(items), SITE, issue['id']))
    lines.append('')
    lines.append('——')
    lines.append('Wake Up Girls｜全球女性议题周报')
    lines.append('视角在她，规则由她。')
    lines.append('记录女性正在经历的世界，也记录女性正在创造的世界。')
    lines.append('')
    lines.append('想退订回信写「退订」即可，我会立即把你从名单移除。')
    body = '\n'.join(lines)

    subs = load_subs()
    bcc = ','.join(s['email'] for s in subs)

    outdir = os.path.join(ROOT, 'outbox')
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, '%s-issue-%s.txt' % (issue.get('date', 'draft'), issue['id']))
    io.open(path, 'w', encoding='utf-8', newline='\n').write(
        '① 主题（粘到 Gmail「主题」）\n%s\n\n'
        '② 正文（粘到 Gmail 正文）\n%s\n\n'
        '③ 密送 BCC（粘到 Gmail「密送」，%d 人；名单为空时自己先发给自己测试）\n%s\n'
        % (subject, body, len(subs), bcc or '（名单为空）'))

    print('已生成：%s' % os.path.relpath(path, ROOT))
    print('  期号：%s ｜ 条目 %d 条 ｜ 收件人 %d 位' % (issue['id'], len(items), len(subs)))
    print('  下一步：打开 Gmail → 写邮件 → 按文件里的①②③依次复制粘贴 → 发送')
    if not subs:
        print('  提示：名单为空。读者发来订阅邮件后，用 python tools/subscribers.py add 邮箱 加入名单。')


if __name__ == '__main__':
    main()
