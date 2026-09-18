# -*- coding: utf-8 -*-
"""② 用 LLM 把候选写成新一期周报（OpenAI 兼容接口）
   - 输入：drafts/week-*.json（最新）
   - 输出：追加到 data/issues.js 数组最前面（最新期在最上）
          同时把每条新闻的「为什么值得关注」备选句写到 drafts/why-<期号>.md，供主理人选句/改写
   - 校验：条目 8–12、覆盖地区 ≥4、覆盖分类 ≥4、单区 ≤3、每条必须有 t/d/body/why_candidates/src/url/region；
           不达标即失败退出（不发布）
   - 环境变量：LLM_API_KEY（必填）、LLM_BASE_URL、LLM_MODEL

⚠️ 关于推理模型：DeepSeek 现有模型（deepseek-v4-pro / deepseek-flash）都会先产出 reasoning_content，
   再产出 content。**max_tokens 给小了会被推理过程吃光，content 变成空字符串**，因此：
     * MAX_TOKENS 设得足够大（默认 16000，可用 LLM_MAX_TOKENS 覆盖）
     * 若 content 为空或 finish_reason == 'length'，直接报明确错误，不写文件
"""
import io, os, re, json, glob, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))
API_KEY = os.environ.get('LLM_API_KEY', '').strip()
BASE = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
MODEL = os.environ.get('LLM_MODEL', 'deepseek-v4-pro')
FORCE = '--force' in sys.argv          # 同周已有期数时仍强制再出一期
MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS', '32000'))

MIN_ITEMS, MAX_ITEMS = 8, 12
MIN_REGIONS = 4
MIN_CATS = 4
MAX_PER_REGION = 3

# 站内可用配图（按分类轮换，图注统一为「示意图」）
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

【最重要的原则】这是「个人策展」而不是新闻搬运：条数要少、判断要清楚。
宁可选 8 条说得明白的，也不要凑 15 条。

要求：
1. 从候选中挑选 %d–%d 条。覆盖：至少 %d 个不同地区（region），至少 %d 个不同分类（cat），
   同一地区不超过 %d 条。优先选与女性权益/性别平等直接相关的。
2. 每条写成：
   - 标题 t：中文，≤34 字，基于候选标题改写，不要编造。**必须语法通顺、可独立读懂**，不要堆砌名词（例：「致命胎儿诊断女性被迫离开奥克拉荷马州堕胎遭诉讼」这种生硬拼接不合格）
   - 摘要 d：中文 40–70 字
   - 正文 body：中文 3 段，每段 90–150 字。第一段陈述事实，第二段补充背景或数据，第三段说明意义或争议。
     只能基于候选信息与常识，**禁止编造具体数字、机构名与人名**
   - why_candidates：**3 句中文短句**，每句 20–45 字，回答「为什么值得关注」。三句必须角度不同：
     第 1 句讲事实的特别之处（哪里反常、哪里被忽略），第 2 句讲结构性问题（制度/权力/行业惯性），
     第 3 句讲它与你我处境的关系。**不要金句、不要口号、不要「我们应该」**，写成一个具体的人的观察。
   - 英文版 en.t / en.d / en.body（2 段，简洁）
6. 另外从候选里挑 **一位值得认识的女性**（可以是新闻中的人物，也可以是被报道的普通女性），输出 watch：
   {"name":"姓名","name_en":"拉丁字母名（无则留空）","role":"身份（如：建筑师 / 研究者 / 行动者 / 工程师）",
    "role_en":"Role in English","region":"地区","why":"为什么值得认识，中文 40–80 字，写她具体做了什么，不要吹捧、不要煽情",
    "why_en":"English, 1–2 sentences","url":"与该人物相关的原文链接","img":""}
7. 再为「她的作品」各推荐 1 件（**必须从下面给出的站内作品库里选，标题要一字不差**），输出 picks：
   {"film":"电影标题","book":"书名","art":"艺术家或作品名"}
3. 分类 cat 只能取这些之一：国际 / 政策与法律 / 健康与权益 / 职场平等 / 生育权利 / 社会 / 文化 / 科技与公益 / 体育
4. 每条保留其原始 src（来源名）与 url（原链接）。**region 要根据新闻实际发生地判定**（候选里的 region 是抓取时按来源媒体所在地标的，常有误，仅作参考）；可选值：东亚 / 东南亚 / 南亚 / 中东 / 非洲 / 欧洲 / 北美 / 拉美 / 大洋洲 / 全球（跨国机构或综述类用「全球」）。
5. 输出 JSON（不要任何解释文字、不要 markdown 代码块），结构：
{"title":"本期标题","summary":"本期摘要（60–90字）","en":{"title":"...","summary":"..."},
 "watch":{"name":"","name_en":"","role":"","role_en":"","region":"","why":"","why_en":"","url":"","img":""},
 "picks":{"film":"","book":"","art":""},
 "sections":[{"cat":"国际","en_cat":"International","items":[{"t":"","d":"","body":["","",""],
   "why_candidates":["","",""],"en":{"t":"","d":"","body":["",""]},"src":"","url":"","region":"欧洲"}]}]}

候选新闻（JSON）：
''' % (MIN_ITEMS, MAX_ITEMS, MIN_REGIONS, MIN_CATS, MAX_PER_REGION)


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
        'max_tokens': MAX_TOKENS,
        'response_format': {'type': 'json_object'},
    }).encode('utf-8')
    req = urllib.request.Request(BASE + '/chat/completions', data=body, headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        sys.exit('LLM 调用失败: HTTP %s %s' % (e.code, e.read().decode('utf-8', 'ignore')[:400]))
    except Exception as e:
        sys.exit('LLM 调用失败: %s' % e)

    choice = (data.get('choices') or [{}])[0]
    content = (choice.get('message') or {}).get('content') or ''
    finish = choice.get('finish_reason')
    usage = data.get('usage') or {}
    reasoning = usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)
    print('  模型=%s finish=%s tokens=%s(推理 %s) 正文字符=%d'
          % (data.get('model'), finish, usage.get('completion_tokens'), reasoning, len(content)))
    if finish == 'length':
        sys.exit('LLM 输出被截断（finish_reason=length，max_tokens=%d 不够）。'
                 '请调大 LLM_MAX_TOKENS 或减少条目数。' % MAX_TOKENS)
    if not content.strip():
        sys.exit('LLM 返回空正文（推理模型常见原因：max_tokens=%d 被 reasoning_content 吃光）。'
                 '请调大 LLM_MAX_TOKENS。' % MAX_TOKENS)
    return content


def current_week_span(now=None):
    """返回本周的 (周一, 周日) 日期字符串。"""
    now = now or datetime.now(CST)
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')


def issue_dates(js_text):
    """从 issues.js 里取出所有期数的 date（两种键写法都要认）。"""
    return re.findall(r'"?date"?\s*:\s*"(\d{4}-\d{2}-\d{2})"', js_text)


def load_works_hint():
    """把站内作品库的标题按类型整理成提示词片段，让 picks 只能选到库里真实存在的作品。"""
    try:
        txt = io.open(os.path.join(ROOT, 'data', 'works.js'), encoding='utf-8').read()
    except Exception as e:
        print('  读取作品库失败（picks 将退回自动挑选）：%s' % e)
        return ''
    by_type = {'film': [], 'book': [], 'art': []}
    for line in txt.splitlines():
        mc = re.search(r"c:\s*['\"](film|book|art)['\"]", line)
        mt = re.search(r"title:\s*['\"]([^'\"]+)['\"]", line)
        if mc and mt:
            by_type[mc.group(1)].append(mt.group(1))
    if not any(by_type.values()):
        return ''
    out = ['\n\n【站内作品库（picks 只能从中选，标题要一字不差）】']
    label = {'film': '电影', 'book': '图书', 'art': '艺术'}
    for k in ('film', 'book', 'art'):
        out.append('%s：%s' % (label[k], '、'.join(by_type[k])))
    return '\n'.join(out)


def validate(issue):
    errs = []
    items = [it for s in issue.get('sections', []) for it in s.get('items', [])]
    n = len(items)
    if n < MIN_ITEMS:
        errs.append('条目不足（%d < %d）' % (n, MIN_ITEMS))
    if n > MAX_ITEMS:
        errs.append('条目过多（%d > %d，策展应当少而精）' % (n, MAX_ITEMS))
    regions = {it.get('region', '') for it in items}
    if len(regions) < MIN_REGIONS:
        errs.append('地区不足（%d < %d）' % (len(regions), MIN_REGIONS))
    cats = {s.get('cat', '') for s in issue.get('sections', []) if s.get('items')}
    if len(cats) < MIN_CATS:
        errs.append('分类不足（%d < %d）' % (len(cats), MIN_CATS))
    per = {}
    for it in items:
        per[it.get('region', '')] = per.get(it.get('region', ''), 0) + 1
    over = [r for r, c in per.items() if c > MAX_PER_REGION]
    if over:
        errs.append('地区超额（%s，单区上限 %d）' % ('/'.join(over), MAX_PER_REGION))
    for it in items:
        for k in ('t', 'd', 'body', 'src', 'url', 'region'):
            if not it.get(k):
                errs.append('缺字段 %s：%s' % (k, str(it.get('t', '?'))[:20]))
        whys = it.get('why_candidates') or []
        if len(whys) < 2:
            errs.append('「为什么值得关注」备选句不足 2 句：%s' % str(it.get('t', '?'))[:20])
        if not str(it.get('url', '')).startswith('http'):
            errs.append('链接异常：%s' % it.get('url'))
    wt = issue.get('watch') or {}
    for k in ('name', 'role', 'why'):
        if not str(wt.get(k, '')).strip():
            errs.append('watch 缺字段 %s' % k)
    pk = issue.get('picks') or {}
    miss = [k for k in ('film', 'book', 'art') if not str(pk.get(k, '')).strip()]
    if miss:
        print('  提示：picks 缺少 %s，前端对该类型将回退为自动挑选' % '/'.join(miss))
    return errs


def next_issue_id(js_text):
    """取下一个可用期号。

    注意：手工写的第一期是 JS 风格 `id: "001"`，而生成器写入的是 JSON 风格 `"id": "002"`，
    两种都要认——历史上这里只匹配前者，导致每次生成都算出同一个号（无限重复的 002）。
    同时跳过已被占用的号，避免任何情况下产生重复期号。
    """
    ids = set(int(m) for m in re.findall(r'"?id"?\s*:\s*"(\d{3})"', js_text))
    nxt = (max(ids) + 1) if ids else 1
    while nxt in ids:            # 兜底：号被占用就往后找
        nxt += 1
    return '%03d' % nxt


def write_why_sheet(issue_id, items, period, issue):
    """把每条的备选句写成待选清单，供主理人选句/改写后再定稿。"""
    lines = ['# 第 %s 期 ·「为什么值得关注」备选句（%s）' % (issue_id, period), '',
             '> 用法：从每条的 3 句里选一句，或直接改写；把你选定的句子回填到 `data/issues.js`',
             '> 里对应条目的 `why` 字段。这份清单只是草稿，AI 写的句子不是最终稿。', '']
    for i, it in enumerate(items, 1):
        lines.append('## %d. %s' % (i, it.get('t', '')))
        lines.append('')
        lines.append('来源：%s ｜ 地区：%s' % (it.get('src', ''), it.get('region', '')))
        lines.append('')
        for j, w in enumerate(it.get('why_candidates') or [], 1):
            lines.append('%d. %s' % (j, w))
        lines.append('')
        lines.append('→ 选定/改写：______________________')
        lines.append('')
    path = os.path.join(ROOT, 'drafts', 'why-%s.md' % issue_id)
    wt = issue.get('watch') or {}
    if wt.get('name'):
        lines += ['---', '', '## WOMEN TO WATCH（待定稿）', '',
                  '**%s**（%s，%s）' % (wt.get('name', ''), wt.get('role', ''), wt.get('region', '')),
                  '', 'AI 草稿：%s' % wt.get('why', ''), '', '→ 你的定稿：______________________', '']
    pk = issue.get('picks') or {}
    if any(pk.values()):
        lines += ['## 她的作品（每周 1 电影 + 1 书 + 1 艺术，待你确认）', '',
                  '- 电影：%s' % pk.get('film', '（未选）'),
                  '- 图书：%s' % pk.get('book', '（未选）'),
                  '- 艺术：%s' % pk.get('art', '（未选）'), '',
                  '→ 确认或改写在 data/issues.js 的 `picks` 字段里。', '']
    io.open(path, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    return path


def main():
    # ── 同周护栏（必须在调用 LLM 之前，否则每周仍会先花一次 API 费用）──
    _js_now = io.open(os.path.join(ROOT, 'data', 'issues.js'), encoding='utf-8').read()
    mon, sun = current_week_span()
    dup_dates = [d for d in issue_dates(_js_now) if mon <= d <= sun]
    if dup_dates and not FORCE:
        print('本周（%s ~ %s）已有期数（%s），按「同周不重复」规则跳过。' % (mon, sun, '、'.join(sorted(set(dup_dates)))))
        print('如需强制再出一期（例如补跑测试），加参数：--force')
        sys.exit(0)

    draft = json.load(io.open(latest_draft(), encoding='utf-8'))
    cand = draft.get('picks', [])[:40]
    if len(cand) < MIN_ITEMS:
        sys.exit('候选不足（%d < %d），本期跳过' % (len(cand), MIN_ITEMS))
    print('候选 %d 条，调用 %s（max_tokens=%d）…' % (len(cand), MODEL, MAX_TOKENS))
    works_hint = load_works_hint()
    raw = call_llm(PROMPT + json.dumps(cand, ensure_ascii=False) + works_hint)
    raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
    try:
        issue = json.loads(raw)
    except Exception as e:
        sys.exit('LLM 返回不是合法 JSON：%s' % e)

    errs = validate(issue)
    if errs:
        sys.exit('校验未通过，已阻止发布：\n- ' + '\n- '.join(errs))

    now = datetime.now(CST)
    _existing = io.open(os.path.join(ROOT, 'data', 'issues.js'), encoding='utf-8').read()
    issue_id = next_issue_id(io.open(os.path.join(ROOT, 'data', 'issues.js'), encoding='utf-8').read())
    monday = now - timedelta(days=now.weekday())
    sunday = monday + timedelta(days=6)
    period = '%s.%02d.%02d – %s.%02d.%02d' % (monday.year, monday.month, monday.day,
                                              sunday.year, sunday.month, sunday.day)


    # 生成站内格式对象（why 先放第一句备选，主理人可改）
    sections = []
    flat = []
    for s in issue['sections']:
        items = []
        for i, it in enumerate(s['items']):
            whys = it.get('why_candidates') or []
            rec = {
                'id': '%s-%d' % (issue_id, len(flat) + 1),
                't': it['t'], 'd': it['d'], 'body': it['body'],
                'why': (whys[0] if whys else ''),
                'en': it.get('en', {}),
                'img': IMG_POOL.get(s['cat'], 'assets/img/womens-rights.png'),
                'src': it['src'], 'url': it['url'], 'region': it['region'],
            }
            items.append(rec)
            flat.append(dict(it, id=rec['id']))
        sections.append({'cat': s['cat'], 'en_cat': s.get('en_cat', s['cat']), 'items': items})

    obj = {
        'id': issue_id, 'date': now.strftime('%Y-%m-%d'), 'period': period,
        'title': issue['title'], 'summary': issue['summary'],
        'en': issue.get('en', {}),
        'img': 'assets/img/womens-rights.png',
        'watch': issue.get('watch') or {},
        'picks': issue.get('picks') or {},
        'sections': sections,
    }

    js_path = os.path.join(ROOT, 'data', 'issues.js')
    js = io.open(js_path, encoding='utf-8').read()
    js = js.replace('window.ISSUES = [', 'window.ISSUES = [\n' + json.dumps(obj, ensure_ascii=False, indent=2) + ',', 1)
    io.open(js_path, 'w', encoding='utf-8', newline='').write(js)

    sheet = write_why_sheet(issue_id, flat, period, issue)
    n = len(flat)
    print('已生成第 %s 期：%d 条，覆盖 %d 个地区 / %d 个分类'
          % (issue_id, n, len({i['region'] for i in flat}), len({s['cat'] for s in sections})))
    print('备选句清单：%s' % sheet)


if __name__ == '__main__':
    main()
