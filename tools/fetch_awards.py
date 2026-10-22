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
                      'type': 'item', 'limit': '1'})
            hit = (js.get('search') or [{}])[0]
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
    ap.add_argument('--no-llm', action='store_true')
    args = ap.parse_args()

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
