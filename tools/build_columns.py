# -*- coding: utf-8 -*-
"""生成 / 维护专栏归类数据 data/columns.js

5 个专栏：在场 · 权利 · 发声 · 身体 · 劳动
每个专栏 = 封面 + 说明 + 相关新闻（周报条目 id）+ 相关作品（作品库下标）

────────────────────────────────────────────────────────────
设计原则（为什么这么写）
────────────────────────────────────────────────────────────
旧版是「每次整份重写」，一旦主理人手工调整过归类，跑一次就被冲掉——
而它现在被接进了周更流水线，等于每周都会冲一次。
所以这一版把「机器分类」和「人的判断」分开存：

    news / works            最终列表（页面只读这个）
    autoNews / autoWorks    机器关键词分类的结果（每次运行重算）
    manualNewsAdd / manualNewsDel / manualWorksAdd / manualWorksDel
                            主理人的手工意志（加了什么、删了什么）

每次运行按这个规则合并：

    manualAdd = 旧 manualAdd ∪ (旧 news  − 旧 autoNews)     ← 人加的
    manualDel = 旧 manualDel ∪ (旧 autoNews − 旧 news)      ← 人删的
    news      = (新 auto ∪ manualAdd) − manualDel

于是：反复运行结果一致（幂等）；人加的不会被删、人删的不会被自动加回来；
只有「新一期里从没出现过的新条目」才会被机器自动归栏。
另外：手工改过的说明文字（intro / sub / img）会被原样保留。

用法：
    python tools/build_columns.py            # 增量更新，保留手工编辑
    python tools/build_columns.py --reset    # 丢弃手工编辑，完全按关键词重算
"""
import json
import os
import pathlib
import subprocess
import sys

# Windows 控制台默认 GBK，输出「✓」会抛 UnicodeEncodeError（文件其实已写好，
# 报错会让人误判为失败），统一改成 UTF-8 输出。
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLUMNS_JS = ROOT / 'data' / 'columns.js'

# ── 规则：关键词 → 专栏（顺序即优先级，先匹配到的胜出）──
RULES = [
    ('身体', ['堕胎', '生育', '孕', '孕期', '产妇', '医疗', '健康', '身体', '照护', '护理',
              '性暴力', '性骚扰', '妇科', '避孕', '月经', '死亡', '自杀', '药物']),
    ('权利', ['法案', '立法', '法律', '诉讼', '法院', '判决', '禁令', '违宪', '政策', '预算',
              '委员会', '条例', '权利', '权益', '协议', '公约', '制裁', '司法']),
    ('劳动', ['薪酬', '工资', '职场', '就业', '劳动', '晋升', '招聘', '工作', '经济', '贫困',
              '创业', '职业', '加班', '同工同酬']),
    ('发声', ['联合国', '国际', '全球', '峰会', '报告', '呼吁', '声明', '论坛', '理事会',
              '组织', '机构', '评述', '排名', '指数']),
    ('在场', ['社会', '公共空间', '街头', '游行', '抗议', '行动', '运动', '暴力', '杀害',
              '失踪', '家庭', '社区', '媒体', '文化', '艺术', '画廊', '博物馆', '展览',
              '电影', '体育', '比赛', '球队', '奥运', '亚运']),
]

COLS = [
    {'id': 'body', 'name': '身体', 'en': 'BODY', 'img': 'assets/img/body-choice.png',
     'sub': '身体自主与健康'},
    {'id': 'rights', 'name': '权利', 'en': 'RIGHTS', 'img': 'assets/img/womens-rights.png',
     'sub': '权益与法律'},
    {'id': 'voice', 'name': '发声', 'en': 'VOICE', 'img': 'assets/img/podium.png',
     'sub': '国际治理与领导力'},
    {'id': 'presence', 'name': '在场', 'en': 'PRESENCE', 'img': 'assets/img/women-power.png',
     'sub': '女性与公共空间'},
    {'id': 'labour', 'name': '劳动', 'en': 'LABOUR', 'img': 'assets/img/workplace.png',
     'sub': '职场与经济'},
]

# ── 专栏说明（AI 生成初稿，主理人可随时改；改过之后本脚本不再覆盖）──
INTROS = {
    '身体': '谁的身体、谁来决定、谁来承担后果——这三问贯穿本栏。避孕与堕胎、孕产医疗与死亡、'
            '照护劳动与健康可及性，在这里不是"女性议题"，而是公共卫生与法律的具体后果。',
    '权利': '把权利从口号拉回到条文：哪一部法律、哪一次判决、哪一笔预算，实际改变了女性能不能'
            '上学、工作、离婚、报警、拥有财产。本栏追踪立法与司法的具体动作，而不是表态。',
    '发声': '国际机构、峰会和报告怎么说，决定了资源与注意力流向哪里。本栏收录全球治理层面'
            '关于性别平等的承诺、排名与落差——以及承诺与行动之间的那段距离。',
    '在场': '女性在公共空间里如何被看见、被对待、被记录。从街头与社区到体育场与美术馆，'
            '本栏关注"在场"这件事本身：谁有资格出现，出现时被如何讲述。',
    '劳动': '无偿照护是劳动的影子，生育是职业的中断点，薪酬差距是结果而不是原因。'
            '本栏追踪工作、报酬与经济的结构性安排，以及女性在其中的位置。',
}


def node_json(expr):
    """在 node 里读 data/issues.js + data/works.js，取值后以 JSON 返回。"""
    script = 'global.window={};require(%s);require(%s);console.log(JSON.stringify(%s));' % (
        json.dumps(str(ROOT / 'data' / 'issues.js').replace('\\', '/')),
        json.dumps(str(ROOT / 'data' / 'works.js').replace('\\', '/')),
        expr)
    r = subprocess.run(['node', '-e', script], capture_output=True, cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit('读取数据失败：' + r.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(r.stdout.decode('utf-8'))


def read_existing():
    """读取现有 data/columns.js（用 node 解析，容忍手工加的注释/格式）。"""
    if not COLUMNS_JS.exists():
        return []
    js = ('global.window={};eval(require("fs").readFileSync(%s,"utf8"));'
          'console.log(JSON.stringify(window.COLUMNS||[]));'
          % json.dumps(str(COLUMNS_JS).replace('\\', '/')))
    r = subprocess.run(['node', '-e', js], capture_output=True, cwd=str(ROOT))
    if r.returncode != 0:
        print('⚠ 现有 columns.js 解析失败，本次按全新生成（手工编辑无法保留）：'
              + r.stderr.decode('utf-8', 'replace')[:200])
        return []
    try:
        return json.loads(r.stdout.decode('utf-8'))
    except Exception as exc:                                    # noqa: BLE001
        print('⚠ 现有数据解析失败（%s），本次按全新生成' % exc)
        return []


def pick(text):
    for name, kws in RULES:
        for k in kws:
            if k in text:
                return name
    return None


def news_key(i):
    """新闻 id 排序：按「期号-序号」。"""
    parts = str(i).split('-')
    try:
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return (999, 999)


def merge(old, key_add, key_del, old_final, old_auto, new_auto, sort_key):
    """合并「机器结果」与「手工意志」，返回 (最终列表, 人加的, 人删的)。

    old_auto 缺失（旧格式文件）时，把当前最终列表当作机器结果——
    这样第一次升级不会把已有的 66 条全部误判成「手工添加」。
    """
    old_final, old_auto = set(old_final), set(old_auto)
    manual_add = set(old.get(key_add) or []) | (old_final - old_auto)
    manual_del = set(old.get(key_del) or []) | (old_auto - old_final)
    final = (set(new_auto) | manual_add) - manual_del
    return (sorted(final, key=sort_key),
            sorted(manual_add, key=sort_key),
            sorted(manual_del, key=sort_key))


def main():
    reset = '--reset' in sys.argv
    existing = [] if reset else read_existing()
    old_by_id = {c.get('id'): c for c in existing if isinstance(c, dict)}

    issues = node_json(
        '(window.ISSUES||[]).map(function(i){return {id:i.id,date:i.date,period:i.period,'
        'items:i.sections.reduce(function(a,s){return a.concat(s.items.map(function(it){'
        'return {id:it.id,t:it.t,d:it.d||"",why:it.why||"",cat:s.cat};}))},[])}})')
    works = node_json('(window.WORKS||[]).map(function(w){return {title:w.title,c:w.c,'
                      'creator:w.creator,tags:w.tags||[],d:w.d||"",region:w.region||""}})')

    # ── 机器分类：只算「新条目」，不碰判断 ──
    auto_news = {c['name']: [] for c in COLS}
    unmatched_news = []
    for iss in issues:
        for it in iss['items']:
            col = pick(it['t'] + it['d'] + it['why'] + it['cat'])
            (auto_news[col] if col else unmatched_news).append(it['id'])

    auto_works = {c['name']: [] for c in COLS}
    unmatched_works = []
    for i, w in enumerate(works):
        col = pick(w['title'] + ' ' + ' '.join(w['tags']) + ' ' + w['d'])
        (auto_works[col] if col else unmatched_works).append(i)

    for name in auto_news:
        auto_news[name].sort(key=news_key)
        auto_works[name].sort()

    live_news_ids = {it['id'] for iss in issues for it in iss['items']}

    out, report = [], []
    for c in COLS:
        name, cid = c['name'], c['id']
        o = old_by_id.get(cid, {}) or {}
        old_news = o.get('news') or []
        old_works = o.get('works') or []
        # 旧格式没有 autoNews/autoWorks 字段 → 当作「当前内容就是机器给的」
        old_auto_news = o.get('autoNews')
        old_auto_works = o.get('autoWorks')
        if old_auto_news is None:
            old_auto_news = old_news
        if old_auto_works is None:
            old_auto_works = old_works

        news, m_add, m_del = merge(o, 'manualNewsAdd', 'manualNewsDel',
                                   old_news, old_auto_news, auto_news[name], news_key)
        wks, w_add, w_del = merge(o, 'manualWorksAdd', 'manualWorksDel',
                                  old_works, old_auto_works, auto_works[name], None)

        # 手工改过的展示字段一律保留
        intro = o.get('intro') or INTROS[name]
        sub = o.get('sub') or c['sub']
        img = o.get('img') or c['img']

        out.append({
            'id': cid, 'name': name, 'en': c['en'], 'img': img, 'sub': sub,
            'intro': intro,
            'news': news,
            'works': wks,
            'autoNews': auto_news[name],
            'autoWorks': auto_works[name],
            'manualNewsAdd': m_add,
            'manualNewsDel': m_del,
            'manualWorksAdd': w_add,
            'manualWorksDel': w_del,
        })
        added = len(set(news) - set(old_news))
        gone = len(set(old_news) - set(news))
        report.append((name, c['en'], len(news), len(wks), added, gone,
                       len(m_add), len(m_del)))

    HEAD = '''/* 专栏（议题档案）—— 由 tools/build_columns.py 维护
 *
 * 页面只读 news / works 两个字段（最终列表）。
 * 其余字段是给脚本用的，请不要手工删除：
 *   autoNews / autoWorks                     机器关键词分类的结果（每次运行重算）
 *   manualNewsAdd / manualNewsDel            主理人手工加的 / 删的（会被永久尊重）
 *   manualWorksAdd / manualWorksDel          同上（作品）
 *
 * 想手工调整归类：直接改 news / works 即可——去掉一条就永远不会被自动加回来，
 * 加一条就永远不会被自动删掉。改完不用跑脚本，提交上线就行。
 * 想推倒重来（丢弃全部手工编辑）：python tools/build_columns.py --reset
 */
window.COLUMNS = '''

    COLUMNS_JS.write_text(HEAD + json.dumps(out, ensure_ascii=False, indent=2) + ';\n',
                          encoding='utf-8', newline='\n')

    # ── 运行报告 ──
    lines = []
    lines.append('已更新 data/columns.js' + ('（--reset：已丢弃手工编辑）' if reset else ''))
    lines.append('')
    lines.append('%-6s %-9s %6s %6s %8s %8s %8s' %
                 ('专栏', '封面', '新闻', '作品', '本次新增', '本次移除', '手工加/删'))
    for name, en, n, w, added, gone, ma, md in report:
        lines.append('%-6s %-9s %6d %6d %8d %8d %8s' %
                     (name, en, n, w, added, gone, '%d/%d' % (ma, md)))
    total_news = sum(r[2] for r in report)
    total_add = sum(r[4] for r in report)
    lines.append('')
    lines.append('合计：%d 条新闻进入专栏（本次新增 %d 条）' % (total_news, total_add))
    stale = sorted({i for r in out for i in r['news']} - live_news_ids, key=news_key)
    if stale:
        lines.append('⚠ 已不在周报里的旧条目 %d 条（保留在专栏中，需要的话可手工删）：%s'
                     % (len(stale), ', '.join(stale[:10])))
    lines.append('未归类新闻 %d 条%s' % (len(unmatched_news),
                 ('：' + ', '.join(sorted(unmatched_news, key=news_key)[:8])) if unmatched_news else ''))
    lines.append('未归类作品 %d 件' % len(unmatched_works))
    if any(r[4] for r in report):
        lines.append('')
        lines.append('本次新增条目（机器归类，可在文件里手工挪栏）：')
        for name, en, n, w, added, gone, ma, md in report:
            if added:
                lines.append('  %s：+%d' % (name, added))
    text = '\n'.join(lines)
    print(text)

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write('## 专栏归类\n\n```\n' + text + '\n```\n')

    r = subprocess.run(['node', '--check', str(COLUMNS_JS)], capture_output=True)
    print('columns.js 语法：' + ('✓' if r.returncode == 0
                              else '✗ ' + r.stderr.decode('utf-8', 'replace')[:200]))


if __name__ == '__main__':
    main()
