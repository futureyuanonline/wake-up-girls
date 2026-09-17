"""汇总 mobile-report.json（移动端检测报告）。用法：python tools/_mtest_summary.py"""
import json
import pathlib
import sys

p = pathlib.Path(__file__).resolve().parent / "mobile-report.json"
if not p.exists():
    sys.exit("no report yet")
d = json.loads(p.read_text(encoding="utf-8"))
print("检测视口宽度:", d["width"], "| 页面数:", len(d["pages"]))
print("=" * 72)
bad = 0
for pg in d["pages"]:
    if "error" in pg:
        print("##", pg["page"], "ERROR", pg["error"])
        bad += 1
        continue
    over = pg["scrollW"] > d["width"] + 1
    bad += 1 if over else 0
    print(f"## {pg['page']:14s} scrollW={pg['scrollW']:4d} clientW={pg['clientWidth']:4d} "
          f"{'*** 横向溢出 ***' if over else 'ok'}")
    for o in pg.get("overflow", [])[:6]:
        print("      溢出:", o)
    h = pg.get("header") or {}
    n = pg.get("nav") or {}
    if h:
        print(f"      顶栏: navH={n.get('h')} navScrollW={n.get('scrollW')}/{n.get('clientW')} "
              f"ctaVisible={h.get('ctaVisible')} langRight={h.get('langRight')} burgerRight={h.get('burgerRight')} menu={h.get('menuDisplay')}")
    g = {k: v for k, v in (pg.get("grids") or {}).items() if v}
    if g:
        print("      网格:", g)
    if pg.get("type"):
        t = pg["type"]
        print(f"      正文: {t['font']}/{t['lineHeight']} align={t['align']} w={t['width']}")
    if pg.get("h1"):
        print("      标题:", pg["h1"])
    st = pg.get("smallTargets") or []
    print(f"      触控：AA不达标(<24px)={pg.get('aaFail', 0)} · 24–44px={pg.get('aaaSmall', 0)}"
          f"（整卡可点的卡片内链接已按整卡计算）")
    for s in st[:6]:
        print("        ·", s)
print("=" * 72)
print("横向溢出页面数:", bad, "→", "全部通过 ✅" if bad == 0 else "仍需修复 ❌")
