"""打印站点冒烟测试结果（tools/site-smoke.html 产出）。
用法：python tools/site_smoke_summary.py
"""
import json
import pathlib
import sys

p = pathlib.Path(__file__).resolve().parent / "mobile-report.json"
if not p.exists():
    sys.exit("未找到报告：先运行冒烟测试页")

d = json.loads(p.read_text(encoding="utf-8"))
if d.get("kind") != "smoke":
    sys.exit("报告不是冒烟测试结果（可能是移动端检测的报告，请重跑）")

fails = 0
for pg in d.get("pages", []):
    g = pg.get("globals") or {}
    bad = [c for c in pg.get("checks", []) if not c["ok"]]
    ok = g.get("appJs") and g.get("data") and not bad and not pg.get("errors")
    if not ok:
        fails += 1
    flag = "✓" if ok else "✗"
    print(f"{flag} {pg['page']:24s} app.js={'on' if g.get('appJs') else 'OFF'} "
          f"数据={'on' if g.get('data') else 'OFF'} 断言 {len(pg.get('checks', [])) - len(bad)}/{len(pg.get('checks', []))}")
    for c in bad:
        print(f"      ✗ {c['what']}: 期望 ≥{c['want']}，实际 {c['got']}  ({c['sel']})")
    for e in pg.get("errors", []):
        print(f"      ! {e}")

print("=" * 60)
print("冒烟测试：", "全部通过 ✅" if fails == 0 else f"{fails} 个页面未通过 ❌")
sys.exit(0 if fails == 0 else 1)
