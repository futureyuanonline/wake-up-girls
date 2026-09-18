"""给全站页脚加「图片来源与免责声明」。可重复执行（幂等）。
用法：python tools/patch_legal_notice.py
说明：必须用 Python 而非 PowerShell 读写——PS 5.1 会把 UTF-8 中文文件按 GBK 处理而写坏。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ANCHOR = '      <div class="f-bottom">'
NOTICE = (
    '      <p class="f-legal">'
    '<span data-i18n="footer.images">'
    '图片来源：作品封面与部分配图来自豆瓣、维基共享资源等公开渠道，版权归原作者及权利方所有；'
    '本站仅用于作品介绍与资讯检索，不作商业用途。如涉侵权或异议请联系：'
    '</span> '
    '<a href="mailto:futureyuan39@gmail.com">futureyuan39@gmail.com</a></p>\n'
)

changed, skipped, bad = [], [], []
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = p.read_text(encoding="utf-8")
    if "f-legal" in s:
        skipped.append(p.name)
        continue
    if ANCHOR not in s:
        bad.append(p.name)
        continue
    s = s.replace(ANCHOR, NOTICE + ANCHOR, 1)
    p.write_text(s, encoding="utf-8")
    changed.append(p.name)

print("已插入：", ", ".join(changed) if changed else "（无）")
print("已存在跳过：", ", ".join(skipped) if skipped else "（无）")
if bad:
    print("⚠️ 找不到页脚锚点：", ", ".join(bad))

# 自检
issues = []
for p in sorted(ROOT.glob("*.html")):
    if p.name.startswith("_"):
        continue
    s = p.read_text(encoding="utf-8")
    if "f-legal" not in s:
        issues.append(f"{p.name}: 缺声明")
    if s.count('data-i18n="footer.images"') != 1:
        issues.append(f"{p.name}: footer.images 键数量异常")
    if 'mailto:futureyuan39@gmail.com' not in s:
        issues.append(f"{p.name}: 缺联系邮箱")
print("自检：", "全部通过 ✓" if not issues else "问题 -> " + "; ".join(issues))
