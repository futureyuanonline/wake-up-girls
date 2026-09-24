# -*- coding: utf-8 -*-
"""生成专栏归类数据 data/columns.js（初稿，供主理人过一遍修改）

5 个专栏（投票栏暂不做）：
  在场 · 权利 · 发声 · 身体 · 劳动
每个专栏包含：封面图、说明文字、相关新闻 id 列表、相关作品索引列表

用法：python tools/build_columns.py
"""
import json
import os
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent

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


def node_json(expr):
    script = 'global.window={};require(%s);require(%s);console.log(JSON.stringify(%s));' % (
        json.dumps(str(ROOT / 'data' / 'issues.js').replace('\\', '/')),
        json.dumps(str(ROOT / 'data' / 'works.js').replace('\\', '/')),
        expr)
    r = subprocess.run(['node', '-e', script], capture_output=True, cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit('读取数据失败：' + r.stderr.decode('utf-8', 'replace')[:300])
    return json.loads(r.stdout.decode('utf-8'))


def pick(text):
    for name, kws in RULES:
        for k in kws:
            if k in text:
                return name
    return None


issues = node_json('(window.ISSUES||[]).map(function(i){return {id:i.id,items:i.sections.reduce('
                   'function(a,s){return a.concat(s.items.map(function(it){return {id:it.id,t:it.t,'
                   'd:it.d||"",why:it.why||"",cat:s.cat};}))},[])}})')
works = node_json('(window.WORKS||[]).map(function(w){return {title:w.title,c:w.c,'
                  'creator:w.creator,tags:w.tags||[],d:w.d||"",region:w.region||""}})')

news_by_col = {c['name']: [] for c in COLS}
unmatched_news = []
for iss in issues:
    for it in iss['items']:
        col = pick(it['t'] + it['d'] + it['why'] + it['cat'])
        if col:
            news_by_col[col].append(it['id'])
        else:
            unmatched_news.append(it['id'])

works_by_col = {c['name']: [] for c in COLS}
unmatched_works = []
for i, w in enumerate(works):
    col = pick(w['title'] + ' ' + ' '.join(w['tags']) + ' ' + w['d'])
    if col:
        works_by_col[col].append(i)
    else:
        unmatched_works.append(i)

# ── 专栏说明（AI 生成初稿，主理人可随时改）──
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

out = []
for c in COLS:
    name = c['name']
    out.append({
        'id': c['id'], 'name': name, 'en': c['en'], 'img': c['img'], 'sub': c['sub'],
        'intro': INTROS[name],
        'news': news_by_col[name],
        'works': works_by_col[name],
    })

HEAD = '''/* 专栏（议题档案）—— 由 tools/build_columns.py 生成初稿，主理人可手工调整
 *
 * 结构：每个专栏 = 封面图 + 说明 + 相关新闻（周报条目 id）+ 相关作品（作品库索引）
 * 说明：news 填 data/issues.js 里的条目 id；works 填作品库里的下标（对应 work.html?i=）
 * 归类规则目前是按关键词初筛，需要主理人过一遍：把不属于本栏的删掉、漏掉的补上。
 */
window.COLUMNS = '''

body = json.dumps(out, ensure_ascii=False, indent=2)
p = ROOT / 'data' / 'columns.js'
p.write_text(HEAD + body + ';\n', encoding='utf-8', newline='\n')

print('已生成 data/columns.js\n')
print('%-6s %-6s %-8s %-8s' % ('专栏', '封面', '新闻', '作品'))
for o in out:
    print('%-6s %-6s %8d %8d' % (o['name'], o['en'], len(o['news']), len(o['works'])))
print()
print('未归类新闻 %d 条：%s' % (len(unmatched_news), ', '.join(unmatched_news[:8])))
print('未归类作品 %d 件' % len(unmatched_works))
print()
print('提示：归到「身体」的作品偏多（关键词"身体/性"过宽），建议主理人过一遍')
r = subprocess.run(['node', '--check', str(p)], capture_output=True)
print('columns.js 语法:', '✓' if r.returncode == 0 else '✗ ' + r.stderr.decode('utf-8', 'replace')[:200])
