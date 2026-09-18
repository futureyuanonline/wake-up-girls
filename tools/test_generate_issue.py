# -*- coding: utf-8 -*-
"""出刊脚本的离线回归测试（不需要 API Key、不花钱、不动真实数据）

为什么要它：2026-09-18 云端跑失败过一次——`write_why_sheet()` 里引用了一个不存在的变量 `issue`，
LLM 成稿和校验都通过了，却在最后写清单时抛 NameError，整个任务失败。
静态检查（ast）会把 for/except 里的变量误报，靠不住；**真正跑一遍**才拦得住。

用法：python tools/test_generate_issue.py
"""
import importlib.util
import json
import shutil
import sys
import tempfile
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILS = []


def check(name, cond, detail=''):
    print(('  ✓ ' if cond else '  ✗ ') + name + ('' if cond else '  → ' + str(detail)))
    if not cond:
        FAILS.append(name)


def load_generator(root):
    spec = importlib.util.spec_from_file_location('gi_test', ROOT / 'tools' / 'generate_issue.py')
    m = importlib.util.module_from_spec(spec)
    sys.modules['gi_test'] = m
    spec.loader.exec_module(m)
    m.ROOT = str(root)
    m.API_KEY = 'test-key-not-used'
    return m


def fake_candidates(n=10):
    regions = ['东亚', '东南亚', '南亚', '中东', '非洲', '欧洲', '北美', '拉美', '大洋洲', '全球']
    return [{'title': '候选 %d' % i, 'region': regions[i % len(regions)], 'src': 'Test Source',
             'url': 'https://example.com/%d' % i, 'summary': '候选摘要'} for i in range(n)]


def fake_issue(n_items=8):
    cats = ['国际', '政策与法律', '社会', '文化']
    regions = ['东亚', '东南亚', '非洲', '欧洲']
    sections = []
    for ci in range(4):
        items = []
        for k in range(n_items // 4):
            idx = ci * (n_items // 4) + k
            items.append({
                't': '测试标题 %d' % idx,
                'd': '测试摘要 %d，四十到七十字之间的一段中文摘要文本。' % idx,
                'body': ['第一段事实。' * 4, '第二段背景。' * 4, '第三段意义。' * 4],
                'why_candidates': ['事实角度 %d' % idx, '结构角度 %d' % idx, '与你我关系 %d' % idx],
                'en': {'t': 'Test %d' % idx, 'd': 'Test summary.', 'body': ['a', 'b']},
                'src': 'Test Source', 'url': 'https://example.com/%d' % idx, 'region': regions[ci],
            })
        sections.append({'cat': cats[ci], 'en_cat': 'Cat', 'items': items})
    return {
        'title': '测试期标题', 'summary': '测试期摘要，六十到九十字。',
        'en': {'title': 'Test Issue', 'summary': 'Summary.'},
        'watch': {'name': '测试人物', 'name_en': 'Test Person', 'role': '研究者', 'role_en': 'Researcher',
                  'region': '东亚', 'why': '她做了某件具体的事，事实陈述。', 'why_en': 'She did something.',
                  'url': 'https://example.com/person', 'img': ''},
        'picks': {'film': '《芭比》', 'book': '《小妇人》', 'art': '弗里达·卡罗'},
        'sections': sections,
    }


def setup_tmp():
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='wug-test-'))
    (tmp / 'data').mkdir()
    (tmp / 'drafts').mkdir()
    shutil.copy(ROOT / 'data' / 'issues.js', tmp / 'data' / 'issues.js')
    shutil.copy(ROOT / 'data' / 'works.js', tmp / 'data' / 'works.js')
    (tmp / 'drafts' / 'week-test.json').write_text(
        json.dumps({'picks': fake_candidates()}, ensure_ascii=False), encoding='utf-8')
    return tmp


print('【1】作品库解析（picks 的候选池）')
tmp = setup_tmp()
gi = load_generator(tmp)
hint = gi.load_works_hint()
check('load_works_hint 返回非空', len(hint) > 200, len(hint))
for t in ('电影：', '图书：', '艺术：'):
    check('  含「%s」分组' % t, t in hint)

print('\n【2】正常路径：跑完整 main()（LLM 用假数据替代）')
gi.call_llm = lambda prompt: json.dumps(fake_issue(), ensure_ascii=False)
try:
    gi.main()
    ok = True
    err = ''
except SystemExit as e:
    ok = False
    err = 'SystemExit: %s' % e
except Exception as e:
    ok = False
    err = '%s: %s' % (type(e).__name__, e)
check('main() 无异常完成', ok, err)

if ok:
    js = (tmp / 'data' / 'issues.js').read_text(encoding='utf-8')
    check('新一期已写入 issues.js', '测试期标题' in js)
    check('watch 已写入', '测试人物' in js)
    check('picks 已写入', '《芭比》' in js)
    check('why 取了第一句备选', '事实角度 0' in js)
    sheets = list((tmp / 'drafts').glob('why-*.md'))
    check('备选句清单已生成', len(sheets) == 1, sheets)
    if sheets:
        sheet = sheets[0].read_text(encoding='utf-8')
        check('  清单含每条 3 句备选', sheet.count('结构角度') == 8, sheet.count('结构角度'))
        check('  清单含 WOMEN TO WATCH 区块', 'WOMEN TO WATCH' in sheet)
        check('  清单含她的作品区块', '她的作品' in sheet)

print('\n【3】校验：坏数据必须被拒绝')
gi2 = load_generator(setup_tmp())
bad = fake_issue()
bad['watch'] = {'name': '', 'role': '', 'why': ''}
check('watch 缺字段 → 报错', len(gi2.validate(bad)) > 0, gi2.validate(bad)[:2] if gi2.validate(bad) else '未报错')
bad2 = fake_issue()
bad2['sections'][0]['items'][0].pop('why_candidates')
errs2 = gi2.validate(bad2)
check('缺 why_candidates → 报错', any('备选句不足' in e for e in errs2), errs2[:2] if errs2 else '未报错')
bad3 = fake_issue(); bad3['sections'] = bad3['sections'][:1]
check('分类不足 → 报错', any('分类不足' in e for e in gi2.validate(bad3)))
bad4 = fake_issue()
for it in bad4['sections'][0]['items']:
    it['url'] = 'ftp://bad'
check('链接异常 → 报错', any('链接异常' in e for e in gi2.validate(bad4)))

print('\n【4】推理模型 token 陷阱：空正文 / 被截断必须明确报错')
import io as _io
import contextlib
import urllib.request as _urlreq


class FakeResp:
    def __init__(self, payload):
        self._p = json.dumps(payload).encode('utf-8')

    def read(self):
        return self._p

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def run_call_llm(payload):
    gi3 = load_generator(setup_tmp())
    orig = _urlreq.urlopen
    _urlreq.urlopen = lambda *a, **k: FakeResp(payload)
    buf = _io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            return gi3.call_llm('x'), None
    except SystemExit as e:
        return None, str(e)
    finally:
        _urlreq.urlopen = orig


_, err_len = run_call_llm({'model': 'm', 'choices': [{'finish_reason': 'length', 'message': {'content': '半截'}}], 'usage': {}})
check('finish_reason=length → 报错', err_len is not None and '截断' in err_len, err_len)
_, err_empty = run_call_llm({'model': 'm', 'choices': [{'finish_reason': 'stop', 'message': {'content': '', 'reasoning_content': '想了很多'}}], 'usage': {'completion_tokens_details': {'reasoning_tokens': 12000}}})
check('正文为空 → 报错', err_empty is not None and '空正文' in err_empty, err_empty)
out_ok, err_ok = run_call_llm({'model': 'm', 'choices': [{'finish_reason': 'stop', 'message': {'content': '{"ok":1}'}}], 'usage': {}})
check('正常返回 → 不报错且取到 content', err_ok is None and out_ok == '{"ok":1}', (out_ok, err_ok))

shutil.rmtree(tmp, ignore_errors=True)

print('\n' + '=' * 56)
if FAILS:
    print('测试未通过 %d 项：%s' % (len(FAILS), '；'.join(FAILS)))
    sys.exit(1)
print('全部通过 ✅  出刊脚本可安全上云')
