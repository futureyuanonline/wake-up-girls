# -*- coding: utf-8 -*-
"""作品库：每周自动拉取「各地区新兴的女性创作者作品」，生成候选并入库

流程
  1. Wikidata SPARQL：按类型（电影 / 图书 / 艺术）查女性创作者、起始年之后首发的作品；
     * 排除重映：只要有任何早于 SINCE 的出版日期就剔除（否则老片修复版会混进来）
     * 质量门槛：必须有中文维基条目（有 zh 标签 + zhwiki 页面）
  2. 国家 → 本站地区分类（欧洲 / 北美 / 东亚 / 南亚 / 中东 / 非洲 / 拉美 / 大洋洲）
  3. 去重：与现有 data/works.js（标题 + 创作者）比对，与队列（QID）比对
  4. 每地区配额（默认 2 件），保证地理分布不退化
  5. 用 LLM 起草那一句编辑判断 d（30–60 字，事实句，不吹）；起草失败就不入库
  6. 达标条目追加进 data/works.js（保持原文件的 JS 风格），其余写入 data/works_queue.json 待下周

用法
  python tools/fetch_works.py                 # 只看不写（默认 dry-run）
  python tools/fetch_works.py --write         # 真的追加进 data/works.js
  python tools/fetch_works.py --since 2025 --per-region 2 --write
  python tools/fetch_works.py --no-llm        # 不起草 d，只更新队列

环境变量（与周更一致）：LLM_API_KEY / LLM_BASE_URL / LLM_MODEL
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKS_JS = os.path.join(ROOT, 'data', 'works.js')
QUEUE = os.path.join(ROOT, 'data', 'works_queue.json')

ENDPOINT = 'https://query.wikidata.org/sparql'
UA = 'WakeUpGirls-works-bot/1.0 (weekly library update; contact: futureyuan39@gmail.com)'

KINDS = [
    # (类型, 创作者属性, Wikidata 类型, 是否要求有中文维基条目)
    # 电影的中文条目覆盖较好，用严格门槛；图书/艺术作品几乎没有中文条目，
    # 硬卡会全军覆没，所以放宽为「有图即可」，其余进队列等人工判断。
    ('film', 'P57', 'Q11424', True),      # 电影：导演
    ('book', 'P50', 'Q571', False),       # 图书：作者
    ('art', 'P170', 'Q838948', False),    # 艺术作品：创作者
]

WIKI_TRIPLE = '?article schema:about ?work ; schema:isPartOf <https://zh.wikipedia.org/> .'

# 国家（中文名）→ 本站地区分类
REGION = {
    '中国': '东亚', '中国大陆': '东亚', '香港': '东亚', '澳门': '东亚', '台湾': '东亚',
    '日本': '东亚', '韩国': '东亚', '朝鲜': '东亚', '蒙古': '东亚',
    '印度': '南亚', '巴基斯坦': '南亚', '孟加拉国': '南亚', '斯里兰卡': '南亚', '尼泊尔': '南亚',
    '越南': '东南亚', '泰国': '东南亚', '印尼': '东南亚', '印度尼西亚': '东南亚', '菲律宾': '东南亚',
    '马来西亚': '东南亚', '新加坡': '东南亚', '柬埔寨': '东南亚', '缅甸': '东南亚',
    '伊朗': '中东', '土耳其': '中东', '以色列': '中东', '黎巴嫩': '中东', '叙利亚': '中东',
    '伊拉克': '中东', '沙特阿拉伯': '中东', '阿联酋': '中东', '埃及': '中东',
    '尼日利亚': '非洲', '南非': '非洲', '肯尼亚': '非洲', '埃塞俄比亚': '非洲', '加纳': '非洲',
    '摩洛哥': '非洲', '突尼斯': '非洲', '阿尔及利亚': '非洲', '塞内加尔': '非洲',
    '巴西': '拉美', '阿根廷': '拉美', '墨西哥': '拉美', '智利': '拉美', '哥伦比亚': '拉美',
    '秘鲁': '拉美', '委内瑞拉': '拉美', '古巴': '拉美', '乌拉圭': '拉美',
    '美国': '北美', '加拿大': '北美',
    '英国': '欧洲', '法国': '欧洲', '德国': '欧洲', '意大利': '欧洲', '西班牙': '欧洲',
    '葡萄牙': '欧洲', '荷兰': '欧洲', '比利时': '欧洲', '瑞士': '欧洲', '奥地利': '欧洲',
    '瑞典': '欧洲', '挪威': '欧洲', '丹麦': '欧洲', '芬兰': '欧洲', '冰岛': '欧洲',
    '波兰': '欧洲', '捷克': '欧洲', '匈牙利': '欧洲', '罗马尼亚': '欧洲', '希腊': '欧洲',
    '爱尔兰': '欧洲', '俄罗斯': '欧洲', '乌克兰': '欧洲', '塞尔维亚': '欧洲', '克罗地亚': '欧洲',
    '澳大利亚': '大洋洲', '新西兰': '大洋洲',
    # 补齐容易漏的国家（Wikidata 里常见，之前因缺表被当成“无法归类”）
    '波斯尼亚和黑塞哥维那': '欧洲', '波黑': '欧洲', '北马其顿': '欧洲', '保加利亚': '欧洲',
    '斯洛伐克': '欧洲', '斯洛文尼亚': '欧洲', '立陶宛': '欧洲', '拉脱维亚': '欧洲',
    '爱沙尼亚': '欧洲', '阿尔巴尼亚': '欧洲', '摩尔多瓦': '欧洲', '白俄罗斯': '欧洲',
    '格鲁吉亚': '欧洲', '亚美尼亚': '欧洲', '阿塞拜疆': '欧洲', '卢森堡': '欧洲',
    '马耳他': '欧洲', '塞浦路斯': '欧洲', '科索沃': '欧洲', '黑山': '欧洲',
    '乌拉圭': '拉美', '厄瓜多尔': '拉美', '玻利维亚': '拉美', '巴拉圭': '拉美',
    '哥斯达黎加': '拉美', '危地马拉': '拉美', '多米尼加': '拉美', '巴拿马': '拉美',
    '约旦': '中东', '卡塔尔': '中东', '科威特': '中东', '阿曼': '中东', '巴林': '中东',
    '也门': '中东', '阿富汗': '南亚', '不丹': '南亚', '马尔代夫': '南亚',
    '乌干达': '非洲', '坦桑尼亚': '非洲', '津巴布韦': '非洲', '莫桑比克': '非洲',
    '安哥拉': '非洲', '喀麦隆': '非洲', '科特迪瓦': '非洲', '布基纳法索': '非洲',
    '马里': '非洲', '卢旺达': '非洲', '苏丹': '非洲', '利比亚': '非洲',
    '老挝': '东南亚', '文莱': '东南亚', '东帝汶': '东南亚',
    '哈萨克斯坦': '中东', '乌兹别克斯坦': '中东',
    '古巴': '拉美', '波多黎各': '拉美', '海地': '拉美',
}

SPARQL = '''
SELECT DISTINCT ?work ?wzhcn ?wzh ?czhcn ?czh ?countryZh ?artistCountryZh ?img ?article (MIN(?d) AS ?date) WHERE {
  ?work wdt:P31 wd:%(qtype)s .
  ?work wdt:%(prop)s ?c .
  ?work wdt:P577 ?d .
  FILTER(YEAR(?d) >= %(since)d)
  FILTER NOT EXISTS { ?work wdt:P577 ?old . FILTER(YEAR(?old) < %(since)d) }
  ?c wdt:P21 wd:Q6581072 .
  %(wiki)s
  OPTIONAL { ?work rdfs:label ?wzhcn . FILTER(LANG(?wzhcn) = "zh-cn") }
  OPTIONAL { ?work rdfs:label ?wzh . FILTER(LANG(?wzh) = "zh") }
  OPTIONAL { ?c rdfs:label ?czhcn . FILTER(LANG(?czhcn) = "zh-cn") }
  OPTIONAL { ?c rdfs:label ?czh . FILTER(LANG(?czh) = "zh") }
  OPTIONAL { ?work wdt:P495 ?country . ?country rdfs:label ?countryZh . FILTER(LANG(?countryZh) = "zh") }
  OPTIONAL { ?c wdt:P27 ?ac . ?ac rdfs:label ?artistCountryZh . FILTER(LANG(?artistCountryZh) = "zh") }
  OPTIONAL { ?work wdt:P18 ?img . }
}
GROUP BY ?work ?wzhcn ?wzh ?czhcn ?czh ?countryZh ?artistCountryZh ?img ?article
LIMIT 300
'''


def sparql(q, tries=3):
    """WDQS 常对复杂查询返回 504/429，必须重试；失败退避后降级返回空。"""
    import time
    data = urllib.parse.urlencode({'query': q, 'format': 'json'}).encode('utf-8')
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(ENDPOINT, data=data, headers={
                'User-Agent': UA, 'Accept': 'application/sparql-results+json',
                'Content-Type': 'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as exc:                                  # noqa: BLE001
            last = exc
            time.sleep(3 * (i + 1))
    raise last


def cell(row, key):
    return ((row.get(key) or {}).get('value') or '').strip()


def norm(s):
    return re.sub(r'[《》〈〉「」『』（）()\s·・\-—–:：,，.。]', '', str(s or '')).lower()


def load_works():
    js = ('global.window={};require(%s);console.log(JSON.stringify(window.WORKS||[]));'
          % json.dumps(WORKS_JS.replace('\\', '/')))
    r = subprocess.run(['node', '-e', js], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit('读取 works.js 失败：' + r.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(r.stdout.decode('utf-8'))


def load_queue():
    if not os.path.exists(QUEUE):
        return {'updated': '', 'items': []}
    with open(QUEUE, encoding='utf-8') as fh:
        return json.load(fh)


def save_queue(q):
    with open(QUEUE, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(q, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


def draft_sentence(item):
    """让模型写那一句编辑判断；失败返回空串（宁可本周不收，也不写套话）。"""
    key = os.environ.get('LLM_API_KEY', '').strip()
    if not key:
        return ''
    base = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1').rstrip('/')
    model = os.environ.get('LLM_MODEL', 'deepseek-chat')
    prompt = (
        '为作品库写一句中文介绍，30–60 字，一句话，不要形容词堆砌，不要「值得关注」「令人震撼」，'
        '不要编造奖项或票房。只输出这句话本身。\n\n'
        '作品：《%s》\n创作者：%s（女性）\n类型：%s\n首年：%s\n出品/国籍：%s\n'
        % (item['title'], item['creator'], {'film': '电影', 'book': '图书', 'art': '艺术作品'}[item['kind']],
           item['year'], item['country'] or '未知')
    )
    body = json.dumps({'model': model,
                       'messages': [{'role': 'user', 'content': prompt}],
                       'temperature': 0.4, 'max_tokens': 300}).encode('utf-8')
    req = urllib.request.Request(base + '/chat/completions', data=body, headers={
        'content-type': 'application/json', 'authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            js = json.loads(r.read().decode('utf-8'))
        txt = js['choices'][0]['message']['content'].strip()
        txt = txt.strip('“”"\' ').replace('\n', ' ')
        # 超长按标点截断，不整条丢弃（之前 120 字上限会把正常长句判失败）
        if len(txt) > 110:
            cut = max(txt.rfind('。', 0, 110), txt.rfind('；', 0, 110), txt.rfind('，', 0, 110))
            txt = txt[:cut + 1] if cut > 40 else txt[:109] + '。'
        return txt if len(txt) >= 10 else ''
    except Exception:                                             # noqa: BLE001
        return ''


def simplify(texts):
    """繁→简（复用仓库里的 opencc-js）；不可用则原样返回。"""
    if not texts:
        return []
    js = ("try{const {Converter}=require('opencc-js');const c=Converter({from:'tw',to:'cn'});"
          "console.log(JSON.stringify(%s.map(function(s){return c(String(s))})))}"
          "catch(e){console.log('null')}" % json.dumps(texts, ensure_ascii=False))
    try:
        r = subprocess.run(['node', '-e', js], capture_output=True, cwd=ROOT)
        out = json.loads(r.stdout.decode('utf-8'))
        if isinstance(out, list) and len(out) == len(texts):
            return out
    except Exception:                                             # noqa: BLE001
        pass
    return list(texts)


def js_str(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'


def append_works(items):
    """把条目按原文件的 JS 风格追加到 data/works.js 末尾（最后一个 ]; 之前）。"""
    src = open(WORKS_JS, encoding='utf-8').read()
    block = ''
    for it in items:
        tags = ['自动收录', it['qid']]
        block += (
            '  { c:%s, title:%s, creator:%s, year:%s, country:%s, region:%s,\n'
            '    d:%s,\n'
            '    tags:[%s] },\n'
            % (js_str(it['kind']), js_str('《%s》' % it['title']), js_str(it['creator']),
               it['year'], js_str(it['country'] or ''), js_str(it['region']),
               js_str(it['d']),
               ', '.join(js_str(t) for t in tags))
        )
    idx = src.rstrip().rfind('];')
    if idx < 0:
        raise SystemExit('works.js 结构异常：找不到结尾的 ];')
    head = src[:idx]
    # 原文件最后一条可能没有尾逗号，直接插入会变成 "} {" → 语法错误
    if head.rstrip().endswith('}'):
        head = head.rstrip() + ',\n'
    new = head + block + src[idx:]
    with open(WORKS_JS, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(new)
    r = subprocess.run(['node', '--check', WORKS_JS], capture_output=True)
    if r.returncode != 0:
        raise SystemExit('写入后语法错误，已中止（请检查）：' + r.stderr.decode('utf-8', 'replace')[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='真的写进 data/works.js')
    ap.add_argument('--since', type=int, default=2024)
    ap.add_argument('--per-region', type=int, default=2)
    ap.add_argument('--no-llm', action='store_true')
    args = ap.parse_args()

    works = load_works()
    queue = load_queue()
    # 去重以「标题」为主键：库里创作者常带英文原名（如「梅尔·图琪（May el-Toukhy）」），
    # 和 Wikidata 的纯中文名对不上，用创作者比对会漏判、导致重复入库。
    known_titles = {norm(w.get('title')) for w in works}
    known = known_titles
    queued = {i.get('qid') for i in queue.get('items', []) if i.get('qid')}

    raw, seen = [], set()
    for kind, prop, qtype, strict in KINDS:
        for yr in range(args.since, datetime.date.today().year + 1):
            q = SPARQL % {'prop': prop, 'qtype': qtype, 'since': yr,
                          'wiki': WIKI_TRIPLE if strict else ''}
            try:
                js = sparql(q)
            except Exception as exc:                              # noqa: BLE001
                print('  ! %s/%d 查询失败：%s' % (kind, yr, exc))
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
                raw.append({'qid': qid, 'kind': kind, 'title': title, 'creator': creator,
                            'year': int(date[:4]), 'country': country, 'region': region,
                            'zhwiki': bool(cell(r, 'article')), 'img': cell(r, 'img')})
            print('  %s/%d：+%d 条' % (kind, yr, len(raw) - n0))

    # 统一繁转简，再分级：A 有中文维基条目 ｜ B 有配图 ｜ C 仅结构化字段
    texts = [x['title'] for x in raw] + [x['creator'] for x in raw]
    conv = simplify(texts)
    for i, x in enumerate(raw):
        x['title'] = conv[i]
        x['creator'] = conv[len(raw) + i]
        x['tier'] = 'A' if x['zhwiki'] else ('B' if x['img'] else 'C')

    cands = [x for x in raw
             if norm(x['title']) not in known and x['qid'] not in queued]
    tier_n = {t: sum(1 for x in cands if x['tier'] == t) for t in ('A', 'B', 'C')}
    print('  去重后 %d 条 ｜ A(有中文条目) %d · B(有图) %d · C(仅字段，只进队列) %d'
          % (len(cands), tier_n['A'], tier_n['B'], tier_n['C']))

    # 每地区配额（只让 A/B 级入库）
    picked, count = [], {}
    for c in sorted([x for x in cands if x['tier'] in ('A', 'B')],
                    key=lambda x: (-x['year'], x['region'])):
        if count.get(c['region'], 0) >= args.per_region:
            continue
        count[c['region']] = count.get(c['region'], 0) + 1
        picked.append(c)
    all_regions = ['东亚', '东南亚', '南亚', '中东', '非洲', '欧洲', '北美', '拉美', '大洋洲']
    missing = [r for r in all_regions if r not in count]
    if missing:
        print('  本周无合格候选的地区：%s（缺失本身也是信息）' % '、'.join(missing))

    print('\n按地区配额入选 %d 件（每区上限 %d）：' % (len(picked), args.per_region))
    for c in picked:
        print('  [%s/%s] %s — %s（%s）%s' % (c['kind'], c['region'], c['title'][:26],
                                            c['creator'][:16], c['year'], c['qid']))

    # 起草 d
    ready = []
    for c in picked:
        if args.no_llm:
            c['d'] = ''
        else:
            c['d'] = draft_sentence(c)
        if c['d']:
            ready.append(c)
        else:
            c['status'] = 'needs_writing'
    if not args.no_llm and picked:
        print('  起草成功 %d / %d（没有草稿句的不入库，进队列）' % (len(ready), len(picked)))

    # 更新队列（全部候选都记下来，避免下周重复）
    qmap = {i.get('qid'): i for i in queue.get('items', [])}
    for c in picked:
        qmap[c['qid']] = dict(c, status=('published' if c in ready else c.get('status', 'needs_writing')))
    queue['items'] = list(qmap.values())[-300:]
    queue['updated'] = datetime.date.today().isoformat()
    if args.write:
        save_queue(queue)

    if not args.write:
        print('\n（dry-run，未写入任何文件；加 --write 才落盘）')
        return

    if ready:
        append_works(ready)
        print('\n✓ 已追加 %d 件进 data/works.js' % len(ready))
    else:
        print('\n本次没有写入新条目（草稿句未就绪或暂无合格候选）')

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write('## 作品库自动更新\n\n- 候选 %d 件，入选 %d 件，入库 %d 件\n'
                     % (len(cands), len(picked), len(ready)))
            for c in picked:
                fh.write('- [%s] %s — %s（%s）%s\n' % (c['region'], c['title'],
                                                       c['creator'], c['year'],
                                                       '入库' if c in ready else '待写'))


if __name__ == '__main__':
    main()
