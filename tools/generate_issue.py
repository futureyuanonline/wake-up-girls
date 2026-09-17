# -*- coding: utf-8 -*-
"""② 用 LLM 把候选写成新一期周报（OpenAI 兼容接口）
   - 输入：drafts/week-*.json（最新）
   - 输出：追加到 data/issues.js 数组最前面（最新期在最上）
   - 校验：条目 ≥10、覆盖地区 ≥7、每条必须有 t/d/body/src/url/region；不达标即失败退出（不发布）
   环境变量：LLM_API_KEY（必填）、LLM_BASE_URL、LLM_MODEL
"""
import io, os, re, json, glob, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))
API_KEY = os.environ.get('LLM_API_KEY', '').strip()
BASE = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
MODEL = os.environ.get('LLM_MODEL', 'deepseek-chat')

# 站内可用配图（自动轮换，图注统一为「示意图」）
IMG_POOL = {
    '政策与法律': 'assets/img/womens-rights.png',
    '国际': 'assets/img/podium.png',
    '健康与权益': 'assets/img/body-choice.png',
    '职场平等': 'assets/img/workplace.png',
    '生育权利': 'assets/img/body-choice.png',
    '社会': 'assets/img/women-power.png',
    '文化': 'assets/img/womens-rights.png',
    '科技与公益': 'assets/img/workplace.png',
    '体育': 'assets/img/women-power.png',
    '经济与职场': 'assets/img/workplace.png',
}

PROMPT = '''你是「Wake Up Girls 全球女性议题周报」的主编。请根据下面的候选新闻，撰写本期周报。
要求：
1. 从候选中挑选 12–15 条，必须覆盖至少 7 个不同地区（region），单一地区不超过 3 条；优先选与女性权益/性别平等直接相关的。
2. 每条写成：标题 t（中文，≤34 字，基于候选标题改写，不要编造）、摘要 d（中文 40–70 字）、正文 body（中文 3 段，每段 90–150 字，第一段陈述事实，第二段补充背景或数据，第三段说明意义或争议；只能基于候选信息与常识，禁止编造具体数字与机构）、英文版 en.t / en.d / en.body（2 段，简洁）。
3. 分类只能取这些之一：国际 / 政策与法律 / 健康与权益 / 职场平等 / 生育权利 / 社会 / 文化 / 科技与公益 / 体育。
4. 每条保留其原始 src（来源名）与 url（原链接）。region 用其候选里的地区。
5. 输出 JSON（不要任何解释文字、不要 markdown 代码块），结构：
{"title":"本期标题","summary":"本期摘要（60–90字）","en":{"title":"...","summary":"..."},
 "sections":[{"cat":"国际","en_cat":"International","items":[{"t":"","d":"","body":["","",""],
   "en":{"t":"","d":"","body":["",""]},"src":"","url":"","region":"欧洲"}]}]}

候选新闻（JSON）：
'''

def latest_draft():
    files = sorted(glob.glob(os.path.join(ROOT, 'drafts', 'week-*.json')))
    if not files:
        sys.exit('未找到 drafts/week-*.json，请先运行 tools/fetch_news.py')
    return files[-1]

def call_llm(prompt):
    if not API_KEY:
        sys.exit('缺少 LLM_API_KEY 环境变量（GitHub Actions 里配置为 Secret）')
    body = json.dumps({
        'model': MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.4,
        'response_format': {'type': 'json_object'},
    }).encode('utf-8')
    req = urllib.request.Request(BASE + '/chat/completions', data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        sys.exit('LLM 调用失败: HTTP %s %s' % (e.code, e.read().decode('utf-8', 'ignore')[:300]))
    except Exception as e:
        sys.exit('LLM 调用失败: %s' % e)
    return data['choices'][0]['message']['content']

def validate(issue):
    errs = []
    items = [it for s in issue.get('sections', []) for it in s.get('items', [])]
    if len(items) < 10:
        errs.append('条目不足（%d < 10）' % len(items))
    regions = {it.get('region', '') for it in items}
    if len(regions) < 7:
        errs.append('地区不足（%d < 7）' % len(regions))
    per = {}
    for it in items:
        per[it.get('region', '')] = per.get(it.get('region', ''), 0) + 1
    over = [r for r, n in per.items() if n > 3]
    if over:
        errs.append('地区超额（%s）' % '/'.join(over))
    for it in items:
        for k in ('t', 'd', 'body', 'src', 'url', 'region'):
            if not it.get(k):
                errs.append('缺字段 %s：%s' % (k, it.get('t', '?')[:20]))
        if not str(it.get('url', '')).startswith('http'):
            errs.append('链接异常：%s' % it.get('url'))
    return errs

def next_issue_id(js_text):
    ids = [int(m) for m in re.findall(r'id:\s*"(\d{3})"', js_text)]
    return '%03d' % ((max(ids) + 1) if ids else 1)

def main():
    draft = json.load(io.open(latest_draft(), encoding='utf-8'))
    cand = draft.get('picks', [])[:40]
    if len(cand) < 10:
        sys.exit('候选不足（%d），本期跳过' % len(cand))
    print('候选 %d 条，调用 %s …' % (len(cand), MODEL))
    raw = call_llm(PROMPT + json.dumps(cand, ensure_ascii=False))
    raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
    try:
        issue = json.loads(raw)
    except Exception as e:
        sys.exit('LLM 返回不是合法 JSON：%s' % e)

    errs = validate(issue)
    if errs:
        sys.exit('校验未通过，已阻止发布：\n- ' + '\n- '.join(errs))

    now = datetime.now(CST)
    issue_id = next_issue_id(io.open(os.path.join(ROOT, 'data', 'issues.js'), encoding='utf-8').read())
    period = '%s.%02d.%02d – %s.%02d.%02d' % (now.year, now.month, now.day,
                                              now.year, now.month, now.day)
    # 生成站内格式对象
    sections = []
    for s in issue['sections']:
        items = []
        for i, it in enumerate(s['items']):
            items.append({
                'id': '%s-%d' % (issue_id, len([x for sec in sections for x in sec['items']]) + i + 1),
                't': it['t'], 'd': it['d'], 'body': it['body'],
                'en': it.get('en', {}),
                'img': IMG_POOL.get(s['cat'], 'assets/img/womens-rights.png'),
                'src': it['src'], 'url': it['url'], 'region': it['region'],
            })
        sections.append({'cat': s['cat'], 'en_cat': s.get('en_cat', s['cat']), 'items': items})

    obj = {
        'id': issue_id, 'date': now.strftime('%Y-%m-%d'), 'period': period,
        'title': issue['title'], 'summary': issue['summary'],
        'en': issue.get('en', {}),
        'img': 'assets/img/womens-rights.png',
        'sections': sections,
    }

    js_path = os.path.join(ROOT, 'data', 'issues.js')
    js = io.open(js_path, encoding='utf-8').read()
    js = js.replace('window.ISSUES = [', 'window.ISSUES = [\n' + json.dumps(obj, ensure_ascii=False, indent=2) + ',', 1)
    io.open(js_path, 'w', encoding='utf-8', newline='').write(js)

    n = len([x for s in sections for x in s['items']])
    print('已生成第 %s 期：%d 条，覆盖 %d 个地区' % (issue_id, n, len({i['region'] for s in sections for i in s['items']})))

if __name__ == '__main__':
    main()
