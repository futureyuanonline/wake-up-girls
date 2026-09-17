# -*- coding: utf-8 -*-
"""每周全球女性议题候选采集器 v3
   核心：按 10 个地区、用当地语言的 Google News RSS（when:7d）分别抓取，
        合并去重后按地区配额输出 —— 保证「全球视角」而非单一国内视角。
   用法：python tools/fetch_news.py
   产出：drafts/week-YYYY-MM-DD.md / .json"""
import urllib.request, urllib.parse, re, json, io, os, time, html
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, 'drafts')
os.makedirs(OUTDIR, exist_ok=True)
CST = timezone(timedelta(hours=8))

# 地区 → [(查询词, hl, gl, ceid), ...]  用当地语言保证覆盖面
REGIONS = {
    '全球':   [('women rights OR gender equality', 'en-US', 'US', 'US:en'),
               ('women girls violence OR education', 'en-US', 'US', 'US:en')],
    '东亚':   [('女性 权益 OR 性别平等', 'zh-CN', 'CN', 'CN:zh-Hans'),
               ('女性 差別 OR ジェンダー', 'ja', 'JP', 'JP:ja'),
               ('여성 차별 OR 성평등', 'ko', 'KR', 'KR:ko')],
    '东南亚': [('perempuan hak OR kesetaraan gender', 'id-ID', 'ID', 'ID:id'),
               ('women rights OR gender equality', 'en-PH', 'PH', 'PH:en')],
    '南亚':   [('women rights OR gender equality', 'en-IN', 'IN', 'IN:en'),
               ('women rights', 'en-PK', 'PK', 'PK:en')],
    '中东':   [('حقوق المرأة OR المساواة', 'ar', 'EG', 'EG:ar'),
               ('women rights', 'en-AE', 'AE', 'AE:en')],
    '非洲':   [('women rights OR gender equality', 'en-NG', 'NG', 'NG:en'),
               ('women rights', 'en-KE', 'KE', 'KE:en'),
               ('women rights', 'en-ZA', 'ZA', 'ZA:en')],
    '欧洲':   [('women rights OR gender equality', 'en-GB', 'GB', 'GB:en'),
               ('derechos mujeres OR igualdad', 'es', 'ES', 'ES:es'),
               ('droits des femmes OR égalité', 'fr', 'FR', 'FR:fr')],
    '北美':   [('women rights OR gender equality', 'en-US', 'US', 'US:en'),
               ('women rights', 'en-CA', 'CA', 'CA:en')],
    '拉美':   [('derechos de las mujeres OR género', 'es-419', 'MX', 'MX:es-419'),
               ('direitos das mulheres', 'pt-BR', 'BR', 'BR:pt-419')],
    '大洋洲': [('women rights OR gender equality', 'en-AU', 'AU', 'AU:en'),
               ('women rights', 'en-NZ', 'NZ', 'NZ:en')],
}

GENDER_KW = ['women', 'woman', 'girl', 'gender', 'female', 'feminist', 'feminism', 'mother', 'maternal',
             'wife', 'widow', 'sexism', 'misogyny', 'abortion', 'reproductive', 'child marriage', 'femicide',
             'harassment', 'survivor', 'suffrage', 'equal pay', 'maternity', 'rape', 'bride',
             '女性', '妇女', '性别', '女孩', '母亲', '女权', '여성', 'ジェンダー', '女性差別',
             'mujer', 'mujeres', 'género', 'violencia', 'mulher', 'mulheres',
             'المرأة', 'النساء', 'حقوق', 'femme', 'femmes', 'égalité']
EXCLUDE_KW = ['cricket', 'ipl', 'scorecard', 'vs ', 'olympic', 'stock', 'shares', 'currency',
              'quarterly', 'earnings', 'recipe', 'horoscope', 'football transfer']

def fetch_google_news(query, hl, gl, ceid, timeout=20):
    url = ('https://news.google.com/rss/search?q=%s&hl=%s&gl=%s&ceid=%s'
           % (urllib.parse.quote(query), hl, gl, ceid))
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': hl})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', 'ignore')
    except Exception as e:
        print('    [fail] %s %s -> %s' % (gl, query[:24], type(e).__name__))
        return ''

def clean(s):
    s = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()

def parse_date(raw):
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw.strip())
        if dt:
            return dt.astimezone(CST)
    except Exception:
        pass
    try:
        return datetime.fromisoformat(raw.strip().replace('Z', '+00:00')).astimezone(CST)
    except Exception:
        return None

def parse_feed(xml, region, edition):
    out = []
    for m in re.finditer(r'<item\b.*?</item>', xml, re.S | re.I):
        blk = m.group(0)
        t = re.search(r'<title[^>]*>(.*?)</title>', blk, re.S | re.I)
        l = re.search(r'<link[^>]*>(.*?)</link>', blk, re.S | re.I)
        d = re.search(r'<pubDate[^>]*>(.*?)</pubDate>', blk, re.S | re.I)
        s = re.search(r'<source[^>]*>(.*?)</source>', blk, re.S | re.I)
        if not (t and l):
            continue
        title = clean(t.group(1))
        # Google News 标题格式："标题 - 媒体名"
        publisher = clean(s.group(1)) if s else ''
        if ' - ' in title:
            parts = title.rsplit(' - ', 1)
            if not publisher and len(parts[1]) < 30:
                title, publisher = parts[0], parts[1]
        dt = parse_date(clean(d.group(1)) if d else '')
        low = title.lower()
        out.append({
            'region': region, 'edition': edition, 'title': title,
            'url': clean(l.group(1)), 'source': publisher or 'Google News',
            'date': dt.strftime('%Y-%m-%d') if dt else '',
            'ts': dt.timestamp() if dt else 0,
            'gender': any(k in low or k in title for k in GENDER_KW),
            'excluded': any(k in low for k in EXCLUDE_KW),
        })
    return out

def load_seen():
    seen = set()
    p = os.path.join(ROOT, 'data', 'issues.js')
    if os.path.exists(p):
        seen.update(re.findall(r'url:\s*"([^"]+)"', io.open(p, encoding='utf-8').read()))
    return seen

def main():
    print('采集全球女性议题候选（v3 · 按地区 × 当地语言）…')
    seen = load_seen()
    all_items = []
    for region, queries in REGIONS.items():
        before = len(all_items)
        for q, hl, gl, ceid in queries:
            xml = fetch_google_news(q, hl, gl, ceid)
            if xml:
                all_items.extend(parse_feed(xml, region, '%s:%s' % (gl, hl)))
            time.sleep(0.6)
        print('  %-6s +%d 条' % (region, len(all_items) - before))

    # 去重
    uniq, titles = [], set()
    for it in all_items:
        key = re.sub(r'\W+', '', it['title'])[:50].lower()
        if it['url'] in seen or key in titles:
            continue
        titles.add(key)
        uniq.append(it)

    now = datetime.now(CST)
    fresh = [x for x in uniq if x['ts'] and (now.timestamp() - x['ts']) <= 8 * 86400]
    rel = [x for x in fresh if x['gender'] and not x['excluded']]
    rel.sort(key=lambda x: -x['ts'])

    # 每地区最多 3 条
    per, picks = {}, []
    for it in rel:
        r = it['region']
        per.setdefault(r, 0)
        if per[r] >= 3:
            continue
        per[r] += 1
        picks.append(it)
    picks.sort(key=lambda x: (x['region'], -x['ts']))

    today = now.strftime('%Y-%m-%d')
    io.open(os.path.join(OUTDIR, 'week-%s.json' % today), 'w', encoding='utf-8', newline='').write(
        json.dumps({'generated': today, 'window_days': 8, 'picks': picks}, ensure_ascii=False, indent=1))

    L = ['# 全球女性议题候选 · %s（近 8 天）' % today, '',
         '共 **%d** 条，覆盖 **%d** 个地区' % (len(picks), len(per)), '']
    cur = None
    for it in picks:
        if it['region'] != cur:
            cur = it['region']
            L += ['', '## %s' % cur]
        L.append('- **%s** — %s（%s）' % (it['title'], it['source'], it['date']))
        L.append('  %s' % it['url'])
    L += ['', '> 从上面挑 12–15 条（保证 7 个以上地区），写入 data/issues.js 新一期；',
          '> 正文由人工/AI 撰写，复核后发布。', '']
    io.open(os.path.join(OUTDIR, 'week-%s.md' % today), 'w', encoding='utf-8', newline='').write('\n'.join(L))

    print()
    print('相关候选: %d 条 | 地区: %s' % (len(picks), json.dumps(per, ensure_ascii=False)))
    print('产出: drafts/week-%s.md' % today)

if __name__ == '__main__':
    main()
