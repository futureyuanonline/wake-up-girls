# -*- coding: utf-8 -*-
"""「数字」栏目自动起草器

用途：从 data/numbers_candidates.json 取一条待写的选题，让大模型按体例写成
五段结构，校验后追加到 data/numbers.js。

用法：
    python tools/generate_number.py                # 起草下一条 pending 并写入
    python tools/generate_number.py --dry-run      # 只打印，不写文件
    python tools/generate_number.py --offline      # 不调用模型，写一条骨架（联调用）
    python tools/generate_number.py --check        # 只校验现有条目是否完整（CI 用）
    python tools/generate_number.py --promote 007-03   # 人工核对后把 draft 改成 false
    python tools/generate_number.py --candidate c03    # 指定候选 key

设计原则（为什么默认写成草稿）：
    * 模型可以起草，但不能替人核对来源。所以新条目默认 draft: true，页面上显示「待核查」；
    * 只有两个途径会把它变成已验证：人工跑 --promote，或者候选来源是「本站自建」
      （本站自己的数据可以自证，用 --verify-own，默认开启）；
    * 校验不过就不写文件，也不改候选状态——宁可不发，也不发半成品。

依赖环境变量（与周更出刊一致）：
    LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
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
NUMBERS_JS = os.path.join(ROOT, 'data', 'numbers.js')
CANDIDATES = os.path.join(ROOT, 'data', 'numbers_candidates.json')
ISSUES_JS = os.path.join(ROOT, 'data', 'issues.js')

REQUIRED_TEXT = ['value', 'title', 'what', 'who', 'caliber', 'action']
TOPICS = ['在场', '权利', '发声', '身体', '劳动', '性别与技术']

SYSTEM = (
    '你是《Wake Up Girls》「数字」栏目的编辑。栏目定位：用证据读性别。\n'
    '写作铁律：\n'
    '1. 只讲一个数字，讲清它的来源与口径，不做道德动员；\n'
    '2. 严格区分「已知 / 推测 / 不知道」，不确定的地方要明说；\n'
    '3. 必须给出「它不能推出什么」至少两条——这是栏目存在的理由；\n'
    '4. 不使用「值得关注」「呼吁」「我们应当」「令人震惊」这类空话；\n'
    '5. 不编造统计数字与链接：不知道就写「待核实」，不要猜。'
)

PROMPT = '''请根据下面的选题，写一条「数字」栏目条目，只输出一个 JSON 对象，不要任何解释文字。

选题：
- seed：{seed}
- 要回答的问题：{question}
- 来源线索：{source_hint}
- 议题分类（从这些里选一个）：{topics}

输出 JSON 的字段与要求：
{{
  "value": "主数字，可含单位或符号，例如 43.1% 或 63 / 160",
  "valueLabel": "对主数字的一句限定说明，12 字以内",
  "title": "标题，24 字以内，陈述句，不喊口号",
  "what": "这个数字是什么，120–260 字，讲清它衡量的是什么、不衡量什么",
  "who": "谁统计的：机构 + 报告名 + 年份，60–160 字。若不确定，写「待核实」并说明缺什么",
  "caliber": "口径：分母是什么、怎么算的、样本范围，60–160 字",
  "cannot": ["不能推出的结论一", "不能推出的结论二", "不能推出的结论三"],
  "action": "谁可以拿它做什么，40–100 字，必须是可执行的动作而非倡议",
  "source": {{"name": "来源名称", "url": "可点开的原始链接；不确定就留空字符串"}},
  "topic": "议题分类"
}}

cannot 必须恰好三条，每条 20–60 字，必须是这个数字真的支撑不了的推论。'''

BANNED = ['值得关注', '令人震惊', '呼吁', '我们应该', '必须重视', '觉醒', '姐妹们']


# ---------- 读现有数据 ----------
def run_node(js):
    r = subprocess.run(['node', '-e', js], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit('node 读取数据失败：' + r.stderr.decode('utf-8', 'replace')[:400])
    return r.stdout.decode('utf-8')


def load_numbers():
    js = ('global.window={};require(%s);console.log(JSON.stringify(window.NUMBERS||[]));'
          % json.dumps(NUMBERS_JS.replace('\\', '/')))
    return json.loads(run_node(js))


def save_numbers(items):
    HEAD = ('/* 「数字」栏目数据 —— 由 tools/generate_number.py 起草追加，人工定稿。\n'
            ' * 字段说明见文件内注释；draft=true 的条目页面会显示「待核查」。\n'
            ' * 手改请保持格式，或直接运行 --check 校验。 */\n'
            'window.NUMBERS = ')
    with open(NUMBERS_JS, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(HEAD + json.dumps(items, ensure_ascii=False, indent=2) + ';\n')


def latest_issue():
    src = open(ISSUES_JS, encoding='utf-8').read()
    ids = re.findall(r'"id"\s*:\s*"(\d{3})"', src)
    return max(ids) if ids else '001'


def load_candidates():
    with open(CANDIDATES, encoding='utf-8') as fh:
        return json.load(fh)


def save_candidates(data):
    with open(CANDIDATES, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


# ---------- 调模型 ----------
def call_llm(prompt):
    import urllib.request
    key = os.environ.get('LLM_API_KEY', '').strip()
    base = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
    model = os.environ.get('LLM_MODEL', 'deepseek-chat')
    if not key:
        return None, '未配置 LLM_API_KEY'
    body = json.dumps({
        'model': model,
        'messages': [{'role': 'system', 'content': SYSTEM},
                     {'role': 'user', 'content': prompt}],
        'temperature': 0.3,
        'max_tokens': 2000,
    }).encode('utf-8')
    req = urllib.request.Request(base + '/chat/completions', data=body, headers={
        'content-type': 'application/json',
        'authorization': 'Bearer ' + key,
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            js = json.loads(r.read().decode('utf-8'))
        return js['choices'][0]['message']['content'], None
    except Exception as exc:                                     # noqa: BLE001
        return None, '模型调用失败：%s' % exc


def parse_json(text):
    if not text:
        return None
    t = re.sub(r'^```(?:json)?|```$', '', text.strip(), flags=re.M).strip()
    i, j = t.find('{'), t.rfind('}')
    if i < 0 or j < 0:
        return None
    try:
        return json.loads(t[i:j + 1])
    except Exception:                                            # noqa: BLE001
        return None


# ---------- 校验 ----------
def validate(item):
    errs = []
    # value / title 本来就是短的（±0.10、63 / 160），只查非空
    short_fields = {'value', 'title', 'valueLabel'}
    for f in REQUIRED_TEXT:
        v = item.get(f)
        if not isinstance(v, str) or not v.strip():
            errs.append('字段 %s 缺失' % f)
        elif f not in short_fields and len(v.strip()) < 10:
            errs.append('字段 %s 过短' % f)
    cannot = item.get('cannot')
    if not isinstance(cannot, list) or len(cannot) < 2:
        errs.append('cannot 至少要有两条')
    else:
        for c in cannot:
            if not isinstance(c, str) or len(c.strip()) < 8:
                errs.append('cannot 有内容过短')
                break
    src = item.get('source') or {}
    url = (src.get('url') or '').strip()
    if url and not url.startswith('http'):
        errs.append('source.url 不是可用链接')
    if not (src.get('name') or '').strip():
        errs.append('source.name 缺失')
    blob = ' '.join([str(item.get(f, '')) for f in REQUIRED_TEXT] +
                    [str(c) for c in (cannot or [])])
    for w in BANNED:
        if w in blob:
            errs.append('出现动员式用语「%s」' % w)
    if item.get('topic') and item['topic'] not in TOPICS:
        errs.append('topic 不在约定分类内：%s' % item['topic'])
    return errs


def entry_from_candidate(c, issue, seq, offline=False):
    own = str(c.get('source_hint', '')).startswith('本站')
    return {
        'id': '%s-%02d' % (issue, seq),
        'issue': issue,
        'date': '',
        'value': c.get('seed', '')[:12] if offline else '',
        'valueLabel': '',
        'title': c.get('question', '')[:24] if offline else '',
        'what': '', 'who': c.get('source_hint', ''), 'caliber': '',
        'cannot': [], 'action': '',
        'source': {'name': c.get('source_hint', ''), 'url': ''},
        'topic': c.get('topic', ''),
        'draft': not own,
    }


# ---------- 主流程 ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--offline', action='store_true')
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--promote', default='')
    ap.add_argument('--candidate', default='')
    args = ap.parse_args()

    items = load_numbers()

    if args.check:
        bad = 0
        for it in items:
            errs = validate(it)
            if errs:
                bad += 1
                print('✗ %s：%s' % (it.get('id'), '；'.join(errs)))
        print('校验 %d 条，%d 条有问题' % (len(items), bad))
        sys.exit(1 if bad else 0)

    if args.promote:
        for it in items:
            if it.get('id') == args.promote:
                it['draft'] = False
                if not args.dry_run:
                    save_numbers(items)
                print('已把 %s 标记为已验证（draft=false）' % args.promote)
                return
        sys.exit('找不到条目 %s' % args.promote)

    data = load_candidates()
    cands = data.get('candidates', [])
    target = None
    if args.candidate:
        target = next((c for c in cands if c.get('key') == args.candidate), None)
    else:
        target = next((c for c in cands if c.get('status') == 'pending'), None)
    if not target:
        print('没有待写的候选选题了。补充 data/numbers_candidates.json 后重试。')
        return

    issue = latest_issue()
    seq = len([i for i in items if str(i.get('issue')) == issue]) + 1
    print('候选 %s ｜ 期号 %s ｜ 序号 %02d' % (target.get('key'), issue, seq))

    if args.offline:
        item = entry_from_candidate(target, issue, seq, offline=True)
        errs = ['离线模式只写骨架，字段留空属正常']
    else:
        prompt = PROMPT.format(seed=target.get('seed', ''), question=target.get('question', ''),
                              source_hint=target.get('source_hint', ''),
                              topics='、'.join(TOPICS))
        text, err = call_llm(prompt)
        if err:
            print('跳过本次起草：%s' % err)
            return
        item = parse_json(text)
        if not item:
            print('跳过：模型输出无法解析为 JSON')
            print((text or '')[:400])
            return
        item['id'] = '%s-%02d' % (issue, seq)
        item['issue'] = issue
        item.setdefault('date', '')
        own = str(target.get('source_hint', '')).startswith('本站')
        item['draft'] = not own
        errs = validate(item)

    print(json.dumps(item, ensure_ascii=False, indent=2)[:1200])
    if errs and not args.offline:
        print('\n✗ 校验未通过，不写入：')
        for e in errs:
            print('  - ' + e)
        return

    if args.dry_run or args.offline:
        print('\n（未写入文件）')
        return

    items.append(item)
    save_numbers(items)
    target['status'] = 'used'
    target['used_by'] = item['id']
    save_candidates(data)
    print('\n✓ 已写入 data/numbers.js：%s（draft=%s）' % (item['id'], item.get('draft')))
    print('  下一页面前请先核对来源；确认无误后运行 --promote %s' % item['id'])

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write('## 数字栏目：新起草一条\n\n- id：%s\n- 标题：%s\n- 主数字：%s\n- 状态：%s\n'
                     % (item['id'], item.get('title', ''), item.get('value', ''),
                        '待核查' if item.get('draft') else '已验证'))


if __name__ == '__main__':
    main()
