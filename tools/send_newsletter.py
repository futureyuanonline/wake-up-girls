# -*- coding: utf-8 -*-
"""⑤ 邮件投递：把最新一期发给订阅者
   邮件服务：Resend（默认，https://resend.com）或 SendGrid（设 MAIL_PROVIDER=sendgrid）
   订阅名单：data/subscribers.json → {"subscribers":[{"email":"a@b.com","lang":"zh-CN"}]}
   环境变量：MAIL_API_KEY（必填）、MAIL_FROM、SITE_URL、MAIL_PROVIDER（resend|sendgrid）
"""
import io, os, re, json, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY = os.environ.get('MAIL_API_KEY', '').strip()
MAIL_FROM = os.environ.get('MAIL_FROM', 'Wake Up Girls <news@example.com>')
SITE_URL = os.environ.get('SITE_URL', 'https://yuanxiuzhong.com').rstrip('/')
PROVIDER = os.environ.get('MAIL_PROVIDER', 'resend').lower()

def load_latest_issue():
    """issues.js 是 JS 对象字面量（键无引号），用 node 解析后取最新一期"""
    import subprocess
    code = ("global.window={};require(process.argv[1]);"
            "console.log(JSON.stringify((window.ISSUES||[])[0]||null));")
    path = os.path.join(ROOT, 'data', 'issues.js')
    try:
        r = subprocess.run(['node', '-e', code, path], capture_output=True, text=True, encoding='utf-8', timeout=60)
    except Exception as e:
        sys.exit('调用 node 解析 issues.js 失败：%s' % e)
    if r.returncode != 0:
        sys.exit('解析 issues.js 失败：%s' % (r.stderr or '')[:300])
    out = (r.stdout or '').strip()
    if not out or out == 'null':
        return None
    try:
        return json.loads(out)
    except Exception as e:
        sys.exit('issues.js 结构异常：%s' % e)

def load_subscribers():
    p = os.path.join(ROOT, 'data', 'subscribers.json')
    if not os.path.exists(p):
        print('未找到 data/subscribers.json，跳过投递')
        return []
    try:
        return json.load(io.open(p, encoding='utf-8')).get('subscribers', [])
    except Exception as e:
        sys.exit('订阅名单解析失败：%s' % e)

def render_html(issue):
    rows = []
    for sec in issue['sections']:
        rows.append('<h3 style="margin:26px 0 8px;font-size:16px;color:#A12627">%s</h3>' % sec['cat'])
        for it in sec['items']:
            rows.append(
                '<div style="padding:10px 0;border-top:1px solid #eee">'
                '<a href="%s/news.html?id=%s" style="color:#1D1715;font-weight:600;text-decoration:none">%s</a>'
                '<div style="color:#5A4F49;font-size:14px;margin-top:4px">%s</div>'
                '<div style="color:#8A7A72;font-size:12px;margin-top:4px">%s · %s</div>'
                '</div>' % (SITE_URL, it['id'], it['t'], it['d'], it['region'], it['src']))
    return ('<div style="max-width:640px;margin:0 auto;font-family:-apple-system,\'Segoe UI\',sans-serif;color:#1D1715">'
            '<div style="border-bottom:3px solid #E1B62A;padding-bottom:10px">'
            '<div style="font-size:13px;letter-spacing:3px;color:#A12627">WAKE UP GIRLS · 第 %s 期</div>'
            '<h1 style="font-size:22px;margin:6px 0">%s</h1>'
            '<div style="color:#5A4F49;font-size:14px">%s</div></div>'
            '%s'
            '<p style="margin-top:28px"><a href="%s" style="color:#A12627">在网站上阅读完整报道 →</a></p>'
            '<p style="color:#8A7A72;font-size:12px;margin-top:20px">视角在她，规则由她。<br>'
            '如需退订请回复本邮件。</p></div>'
            % (issue['id'], issue['title'], issue.get('summary', ''), ''.join(rows), SITE_URL))

def send_resend(to, subject, html):
    body = json.dumps({'from': MAIL_FROM, 'to': [to], 'subject': subject, 'html': html}).encode('utf-8')
    req = urllib.request.Request('https://api.resend.com/emails', data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status

def send_sendgrid(to, subject, html):
    sender = MAIL_FROM
    m = re.match(r'(.*)<(.*)>', MAIL_FROM)
    if m:
        sender = {'name': m.group(1).strip(), 'email': m.group(2).strip()}
    body = json.dumps({
        'personalizations': [{'to': [{'email': to}]}], 'from': sender,
        'subject': subject, 'content': [{'type': 'text/html', 'value': html}],
    }).encode('utf-8')
    req = urllib.request.Request('https://api.sendgrid.com/v3/mail/send', data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status

def main():
    issue = load_latest_issue()
    if not issue:
        sys.exit('没有可投递的期数')
    subs = load_subscribers()
    if not subs:
        return
    if not API_KEY:
        sys.exit('缺少 MAIL_API_KEY（GitHub Actions 里配置为 Secret）')
    html = render_html(issue)
    subject = '【Wake Up Girls】第 %s 期 · %s' % (issue['id'], issue['title'])
    ok = fail = 0
    for s in subs:
        email = s.get('email') if isinstance(s, dict) else s
        if not email:
            continue
        try:
            if PROVIDER == 'sendgrid':
                send_sendgrid(email, subject, html)
            else:
                send_resend(email, subject, html)
            ok += 1
        except urllib.error.HTTPError as e:
            fail += 1
            print('  发送失败 %s: HTTP %s %s' % (email, e.code, e.read().decode('utf-8', 'ignore')[:160]))
        except Exception as e:
            fail += 1
            print('  发送失败 %s: %s' % (email, e))
    print('邮件投递完成：成功 %d，失败 %d' % (ok, fail))

if __name__ == '__main__':
    main()
