# -*- coding: utf-8 -*-
"""作品库 · 电影节获奖作品自动收录

思路：作品库聚焦「全世界电影/电视节获奖作品」，因为奖项可核查、天然分地区、
而且能直接支撑那句编辑判断（获了什么奖、谁导的、哪国的）。

流程
  1. 用 Wikidata 搜索接口查出各奖项的 QID（不靠记忆猜），并做描述校验
     （排除「训练舰」「电子游戏」这类同名错配）；结果缓存到 data/awards_cache.json
  2. 逐奖项查询：该奖的获奖作品 + 创作者为女性 + 有中文标签
  3. 国家 → 地区分类；去重（标题 / QID）；每地区配额
  4. LLM 起草一句介绍（含奖项事实，不许编造）
  5. 达标（A 有中文维基条目 / B 有配图）的追加进 data/works.js，其余进队列

用法
  python tools/fetch_awards.py                       # 只看不写
  python tools/fetch_awards.py --write               # 写入 data/works.js
  python tools/fetch_awards.py --since 2015 --per-region 3 --write
  python tools/fetch_awards.py --refresh-awards      # 重新查奖项 QID
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_works import (REGION, append_works, js_str, load_queue, load_works,  # noqa: E402
                         norm, save_queue, simplify)

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'data', 'awards_cache.json')
UA = 'WakeUpGirls-awards-bot/1.0 (weekly library update; contact: futureyuan39@gmail.com)'
API = 'https://www.wikidata.org/w/api.php'
SPARQL = 'https://query.wikidata.org/sparql'

SEEDS = [
    ("Palme d'Or", '戛纳金棕榈'), ('Golden Lion', '威尼斯金狮'),
    ('Golden Bear', '柏林金熊'), ('Silver Bear', '柏林银熊'),
    ('Jury Prize', '戛纳评审团奖'), ('Teddy Award', '泰迪熊奖'),
    ('Crystal Bear', '水晶熊奖'), ('Golden Leopard', '洛迦诺金豹'),
    ('Golden Shell', '圣塞巴斯蒂安金贝壳'), ('New Currents Award', '釜山新浪潮'),
    ('Tokyo Grand Prix', '东京大奖'), ('Emmy Award', '艾美奖'),
    ('Golden Globe Award', '金球奖'), ('FIPRESCI Prize', '费比西奖'),
    ('Un Certain Regard', '一种关注'), ("Queer Palm", '酷儿棕榈'),
    ('Best Director Award Cannes', '戛纳最佳导演'), ('Silver Lion', '威尼斯银狮'),
]

# 描述里出现这些词才算「奖项」；出现后者直接排除同名错配
GOOD_HINT = ['award', 'prize', 'film', 'festival', 'television', 'best ']
BAD_HINT = ['video game', 'training ship', 'album', 'song', 'band', 'company']


def api(params):
    params = dict(params, format='json')
    url = API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8'))


def discover_awards(refresh=False):
    if os.path.exists(CACHE) and not refresh:
        with open(CACHE, encoding='utf-8') as fh:
            return json.load(fh)
    out = []
    for seed, zh in SEEDS:
        try:
            js = api({'action': 'wbsearchentities', 'search': seed, 'language': 'en',
                      'type': 'item', 'limit': '6'})
            hits = js.get('search') or []
            hit = {}
            for cand in hits:            # 逐个看描述，避开「训练舰」「电子游戏」这类同名项
                d = (cand.get('description') or '').lower()
                if any(b in d for b in BAD_HINT) or not any(g in d for g in GOOD_HINT):
                    continue
                hit = cand
                break
            if not hit and hits:
                hit = hits[0]
        except Exception as exc:                                  # noqa: BLE001
            print('  ! 搜索 %s 失败：%s' % (seed, exc))
            continue
        qid, desc = hit.get('id'), (hit.get('description') or '').lower()
        if not qid:
            continue
        if any(b in desc for b in BAD_HINT) or not any(g in desc for g in GOOD_HINT):
            print('  × %-26s → %s 描述不符，跳过（%s）' % (seed, qid, desc[:40]))
            continue
        out.append({'seed': seed, 'zh': zh, 'qid': qid,
                    'label': hit.get('label', ''), 'desc': desc[:60]})
        print('  ✓ %-26s → %-12s %s' % (seed, qid, zh))
        time.sleep(0.2)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    return out


def sparql(q, tries=3):
    data = urllib.parse.urlencode({'query': q, 'format': 'json'}).encode('utf-8')
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(SPARQL, data=data, headers={
                'User-Agent': UA, 'Accept': 'application/sparql-results+json',
                'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req, timeout=100) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:                                  # noqa: BLE001
            last = exc
            time.sleep(4 * (i + 1))
    raise last


ONE_AWARD = '''
SELECT DISTINCT ?work ?wzhcn ?wzh ?czhcn ?czh ?countryZh ?artistCountryZh ?img ?article (MIN(?d) AS ?date) WHERE {
  ?work p:P166 ?st .
  ?st ps:P166 wd:%(award)s .
  { ?work wdt:P57 ?c } UNION { ?work wdt:P50 ?c } UNION { ?work wdt:P170 ?c }
  ?c wdt:P21 wd:Q6581072 .
  ?work wdt:P577 ?d .
  FILTER(YEAR(?d) >= %(since)d)
  OPTIONAL { ?work rdfs:label ?wzhcn . FILTER(LANG(?wzhcn) = "zh-cn") }
  OPTIONAL { ?work rdfs:label ?wzh . FILTER(LANG(?wzh) = "zh") }
  OPTIONAL { ?c rdfs:label ?czhcn . FILTER(LANG(?czhcn) = "zh-cn") }
  OPTIONAL { ?c rdfs:label ?czh . FILTER(LANG(?czh) = "zh") }
  OPTIONAL { ?work wdt:P495 ?co . ?co rdfs:label ?countryZh . FILTER(LANG(?countryZh) = "zh") }
  OPTIONAL { ?c wdt:P27 ?ac . ?ac rdfs:label ?artistCountryZh . FILTER(LANG(?artistCountryZh) = "zh") }
  OPTIONAL { ?work wdt:P18 ?img . }
  OPTIONAL { ?article schema:about ?work ; schema:isPartOf <https://zh.wikipedia.org/> . }
}
GROUP BY ?work ?wzhcn ?wzh ?czhcn ?czh ?countryZh ?artistCountryZh ?img ?article
LIMIT 120
'''


def cell(row, key):
    return ((row.get(key) or {}).get('value') or '').strip()


# ---- 骨架核验模式：给一份「我以为是获奖作品」的清单，逐条向 Wikidata 核实 ----
ENRICH = '''
SELECT DISTINCT ?work ?wlabel ?czhcn ?czh ?gender ?countryZh ?img WHERE {
  ?work rdfs:label ?lbl .
  FILTER(LANG(?lbl) = "zh" || LANG(?lbl) = "en")
  FILTER(CONTAINS(LCASE(?lbl), LCASE("%(needle)s")))
  ?work wdt:P577 ?d . FILTER(YEAR(?d) = %(year)d)
  ?work p:P166 ?st . ?st ps:P166 wd:%(award)s .
  { ?work wdt:P57 ?c } UNION { ?work wdt:P50 ?c } UNION { ?work wdt:P170 ?c }
  ?work rdfs:label ?wlabel . FILTER(LANG(?wlabel) = "zh")
  OPTIONAL { ?c rdfs:label ?czhcn . FILTER(LANG(?czhcn) = "zh-cn") }
  OPTIONAL { ?c rdfs:label ?czh . FILTER(LANG(?czh) = "zh") }
  OPTIONAL { ?c wdt:P21 ?gender . }
  OPTIONAL { ?work wdt:P495 ?co . ?co rdfs:label ?countryZh . FILTER(LANG(?countryZh) = "zh") }
  OPTIONAL { ?work wdt:P18 ?img . }
}
LIMIT 5
'''

FEMALE = 'Q6581072'


def enrich(args):
    seed_path = os.path.join(ROOT, 'data', 'awards_seed.json')
    with open(seed_path, encoding='utf-8') as fh:
        seed = json.load(fh)
    awards = discover_awards(False)
    # 奖项键 → 缓存的奖项条目
    keymap = {}
    for a in awards:
        s = a['seed'].lower()
        if 'palme' in s:
            keymap['palme'] = a
        elif 'golden lion' in s:
            keymap['lion'] = a
        elif 'golden bear' in s:
            keymap['bear'] = a
    missing = [k for k in ('palme', 'lion', 'bear') if k not in keymap]
    if missing:
        print('⚠ 奖项清单里缺少：%s（试 --refresh-awards）' % missing)

    works = load_works()
    known_titles = {norm(w.get('title')) for w in works}
    queue = load_queue()

    verified, failed = [], []
    for it in seed.get('items', []):
        aw = keymap.get(it['award'])
        if not aw:
            failed.append((it, '奖项未查到'))
            continue
        try:
            js = sparql(ENRICH % {'needle': it['match'], 'year': it['year'], 'award': aw['qid']})
        except Exception as exc:                                  # noqa: BLE001
            failed.append((it, '查询失败 %s' % exc))
            continue
        rows = js['results']['bindings']
        if not rows:
            failed.append((it, 'Wikidata 里查不到「%s」在 %s 年获该奖' % (it['match'], it['year'])))
            continue
        r = rows[0]
        gender = cell(r, 'gender').rsplit('/', 1)[-1]
        # Wikidata 的 zh 标签常是繁体（法國/美國），地区表是简体，先统一转简体
        title_zh = simplify([it.get('title_zh') or cell(r, 'wlabel')])[0]
        creator = simplify([cell(r, 'czhcn') or cell(r, 'czh')])[0]
        country = simplify([cell(r, 'countryZh')])[0]
        if gender != FEMALE:
            failed.append((it, '创作者性别字段不是女性（%s）' % (gender or '缺失')))
            continue
        rec = {'qid': cell(r, 'work').rsplit('/', 1)[-1], 'kind': 'film',
               'title': title_zh, 'creator': creator,
               'year': it['year'], 'country': country,
               'region': REGION.get(country, ''), 'award': aw['zh'],
               'zhwiki': True, 'img': cell(r, 'img')}
        # 介绍句：有模型就起草；没有就写一句事实（不装编辑腔），并标记「需补写」
        rec['d'] = draft(rec) if os.environ.get('LLM_API_KEY', '').strip() else ''
        if not rec['d']:
            rec['d'] = '由%s执导，%s年获%s。出品国：%s。' % (creator, it['year'], aw['zh'], country or '未知')
            rec['needs_edit'] = True
        if not rec['region']:
            failed.append((it, '国别无法归入地区（%s）' % (country or '无')))
            continue
        if norm(rec['title']) in known_titles:
            failed.append((it, '库里已有《%s》，跳过' % rec['title']))
            continue
        verified.append(rec)

    conv = simplify([v['title'] for v in verified] + [v['creator'] for v in verified])
    for i, v in enumerate(verified):
        v['title'] = conv[i]
        v['creator'] = conv[len(verified) + i]

    print('\n=== 核验结果 ===')
    for v in verified:
        print('  ✓ 《%s》%s（%s）%s｜%s' % (v['title'], v['creator'], v['year'], v['award'], v['qid']))
    for it, why in failed:
        print('  ✗ %-14s %s' % (it['title_zh'], why))
    print('\n通过 %d 条 / 共 %d 条' % (len(verified), len(seed.get('items', []))))

    if not args.write:
        print('（dry-run，未写入；加 --write 落盘）')
        return
    if verified:
        append_with_award(verified)
        print('✓ 已追加 %d 条进 data/works.js（仅写核验通过的）' % len(verified))
    qmap = {i.get('qid'): i for i in queue.get('items', [])}
    for v in verified:
        qmap[v['qid']] = dict(v, status='published')
    queue['items'] = list(qmap.values())[-400:]
    queue['updated'] = datetime.date.today().isoformat()
    save_queue(queue)

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write('## 作品库骨架核验\n\n通过 %d / %d\n\n' % (len(verified), len(seed.get('items', []))))
            for v in verified:
                fh.write('- 《%s》%s（%s）%s\n' % (v['title'], v['creator'], v['year'], v['award']))
            for it, why in failed:
                fh.write('- ✗ %s：%s\n' % (it['title_zh'], why))


def append_with_award(items):
    """追加到 works.js，并写入 works.js 已有的 a（奖项）字段。"""
    from fetch_works import WORKS_JS
    src = open(WORKS_JS, encoding='utf-8').read()
    block = ''
    for it in items:
        tags = ['骨架收录', it['qid']] + (['需补写'] if it.get('needs_edit') else [])
        block += (
            '  { c:%s, title:%s, creator:%s, year:%s, country:%s, region:%s,\n'
            '    d:%s,\n'
            '    tags:[%s], a:%s },\n'
            % (js_str(it['kind']), js_str('《%s》' % it['title']), js_str(it['creator']),
               it['year'], js_str(it['country'] or ''), js_str(it['region']),
               js_str(it.get('d') or ''), ', '.join(js_str(t) for t in tags), js_str(it['award']))
        )
    idx = src.rstrip().rfind('];')
    if idx < 0:
        raise SystemExit('works.js 结构异常')
    head = src[:idx]
    if head.rstrip().endswith('}'):        # 原文件最后一条没有尾逗号
        head = head.rstrip() + ',\n'
    with open(WORKS_JS, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(head + block + src[idx:])
    r = subprocess.run(['node', '--check', WORKS_JS], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('写入后语法错误：' + r.stderr.decode('utf-8', 'replace')[:300])


def draft(item):
    key = os.environ.get('LLM_API_KEY', '').strip()
    if not key:
        return ''
    base = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
    model = os.environ.get('LLM_MODEL', 'deepseek-chat')
    prompt = (
        '为女性创作者作品库写一句中文介绍，30–60 字，一句话。\n'
        '必须包含：她是谁（做了什么）、这部作品获了什么奖。不要形容词堆砌，'
        '不要「值得关注」「惊艳」这类词，不许编造奖项或票房，只用在下面给出的信息。\n'
        '只输出这句话本身。\n\n'
        '作品：《%s》\n创作者：%s（女性）\n首年：%s\n出品/国籍：%s\n所获奖项：%s\n'
        % (item['title'], item['creator'], item['year'], item['country'] or '未知', item['award'])
    )
    body = json.dumps({'model': model,
                       'messages': [{'role': 'user', 'content': prompt}],
                       'temperature': 0.4, 'max_tokens': 300}).encode('utf-8')
    req = urllib.request.Request(base + '/chat/completions', data=body, headers={
        'content-type': 'application/json', 'authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            js = json.loads(r.read().decode('utf-8'))
        txt = js['choices'][0]['message']['content'].strip().strip('“”"\' ')
        txt = ' '.join(txt.split())
        return txt if 10 <= len(txt) <= 130 else ''
    except Exception:                                             # noqa: BLE001
        return ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--since', type=int, default=2015)
    ap.add_argument('--per-region', type=int, default=3)
    ap.add_argument('--refresh-awards', action='store_true')
    ap.add_argument('--enrich', action='store_true', help='按 data/awards_seed.json 逐条核验骨架名单')
    ap.add_argument('--no-llm', action='store_true')
    args = ap.parse_args()

    if args.enrich:
        print('=== 骨架核验（逐条向 Wikidata 求证）===')
        enrich(args)
        return

    print('=== 奖项清单 ===')
    awards = discover_awards(args.refresh_awards)
    print('可用奖项 %d 个\n' % len(awards))

    works = load_works()
    queue = load_queue()
    known_titles = {norm(w.get('title')) for w in works}
    queued = {i.get('qid') for i in queue.get('items', []) if i.get('qid')}

    print('=== 逐奖项查询获奖作品 ===')
    raw, seen, per_award = [], set(), []
    for a in awards:
        try:
            js = sparql(ONE_AWARD % {'award': a['qid'], 'since': args.since})
        except Exception as exc:                                  # noqa: BLE001
            print('  ! %s 查询失败：%s' % (a['zh'], exc))
            continue
        n0 = len(raw)
        for r in js['results']['bindings']:
            qid = cell(r, 'work').rsplit('/', 1)[-1]
            if qid in seen:
                continue
            title = cell(r, 'wzhcn') or cell(r, 'wzh')
            creator = cell(r, 'czhcn') or cell(r, 'czh')
            date = cell(r, 'date')
            country = cell(r, 'countryZh') or cell(r, 'artistCountryZh')
            region = REGION.get(country)
            if not (title and creator and date and region):
                continue
            seen.add(qid)
            raw.append({'qid': qid, 'kind': 'film', 'title': title, 'creator': creator,
                        'year': int(date[:4]), 'country': country, 'region': region,
                        'award': a['zh'], 'awardQid': a['qid'],
                        'zhwiki': bool(cell(r, 'article')), 'img': cell(r, 'img')})
        per_award.append((a['zh'], len(raw) - n0))
        print('  %-14s +%d' % (a['zh'], len(raw) - n0))

    conv = simplify([x['title'] for x in raw] + [x['creator'] for x in raw])
    for i, x in enumerate(raw):
        x['title'] = conv[i]
        x['creator'] = conv[len(raw) + i]
        x['tier'] = 'A' if x['zhwiki'] else ('B' if x['img'] else 'C')

    cands = [x for x in raw if norm(x['title']) not in known_titles and x['qid'] not in queued]
    tier_n = {t: sum(1 for x in cands if x['tier'] == t) for t in ('A', 'B', 'C')}
    print('\n去重后 %d 条 ｜ A %d · B %d · C %d' % (len(cands), tier_n['A'], tier_n['B'], tier_n['C']))

    picked, count = [], {}
    for c in sorted([x for x in cands if x['tier'] in ('A', 'B')],
                    key=lambda x: (-x['year'], x['region'])):
        if count.get(c['region'], 0) >= args.per_region:
            continue
        count[c['region']] = count.get(c['region'], 0) + 1
        picked.append(c)

    print('入选 %d 件（每区上限 %d）：' % (len(picked), args.per_region))
    for c in picked:
        print('  [%s] 《%s》%s（%s）%s｜%s' % (c['region'], c['title'], c['creator'],
                                              c['year'], c['award'], c['qid']))
    all_regions = ['东亚', '东南亚', '南亚', '中东', '非洲', '欧洲', '北美', '拉美', '大洋洲']
    miss = [r for r in all_regions if r not in count]
    if miss:
        print('  无合格候选的地区：%s' % '、'.join(miss))

    ready = []
    for c in picked:
        c['d'] = '' if args.no_llm else draft(c)
        if c['d']:
            ready.append(c)
    if not args.no_llm:
        print('  起草成功 %d / %d' % (len(ready), len(picked)))

    qmap = {i.get('qid'): i for i in queue.get('items', [])}
    for c in picked:
        qmap[c['qid']] = dict(c, status='published' if c in ready else 'needs_writing')
    queue['items'] = list(qmap.values())[-400:]
    queue['updated'] = datetime.date.today().isoformat()

    if not args.write:
        print('\n（dry-run，未写入；加 --write 落盘）')
        return
    save_queue(queue)
    if ready:
        append_works(ready)
        print('\n✓ 已追加 %d 件进 data/works.js' % len(ready))
    else:
        print('\n本次无条目入库')

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write('## 作品库（电影节获奖）\n\n- 获奖候选 %d 件，入选 %d 件，入库 %d 件\n\n'
                     % (len(cands), len(picked), len(ready)))
            fh.write('| 地区 | 作品 | 创作者 | 年份 | 奖项 |\n|---|---|---|---|---|\n')
            for c in picked:
                fh.write('| %s | 《%s》 | %s | %s | %s |\n'
                         % (c['region'], c['title'], c['creator'], c['year'], c['award']))
            if miss:
                fh.write('\n本周无合格候选的地区：%s\n' % '、'.join(miss))


if __name__ == '__main__':
    main()
