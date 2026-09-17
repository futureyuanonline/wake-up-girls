"""移动端改造：给所有页面补 head 元信息 + 移动端下拉菜单入口。
可重复执行（幂等）。用法：python tools/patch_mobile.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD_VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
NEW_VIEWPORT = (
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />\n'
    '  <meta name="theme-color" content="#F4F1EB" />\n'
    '  <meta name="format-detection" content="telephone=no" />'
)

NAV_CTA = (
    '\n          <a class="menu-cta" data-nav="subscribe" href="subscribe.html" '
    'data-i18n="nav.cta">订阅周刊</a>\n        </nav>'
)

changed = []
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = p.read_text(encoding="utf-8")
    orig = s
    s = s.replace(OLD_VIEWPORT, NEW_VIEWPORT)
    if 'class="menu-cta"' not in s:
        s = s.replace("</nav>", NAV_CTA, 1)
    if s != orig:
        p.write_text(s, encoding="utf-8")
        changed.append(p.name)

print("已更新：", ", ".join(changed) if changed else "（无变化）")

# 自检
bad = []
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = p.read_text(encoding="utf-8")
    if "viewport-fit=cover" not in s:
        bad.append(f"{p.name}: viewport")
    if 'class="menu-cta"' not in s:
        bad.append(f"{p.name}: menu-cta")
    if 'name="theme-color"' not in s:
        bad.append(f"{p.name}: theme-color")
print("自检：", "全部通过" if not bad else "问题 -> " + "; ".join(bad))

# 确认 9 页 header 仍完全一致
hs = set()
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = p.read_text(encoding="utf-8")
    i = s.find('<header class="site">')
    j = s.find("</header>", i)
    hs.add(s[i:j])
print("header 一致性：", "9 页完全相同" if len(hs) == 1 else f"有 {len(hs)} 种，请检查")
