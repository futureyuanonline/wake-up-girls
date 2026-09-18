# -*- coding: utf-8 -*-
"""图片优化：封面与海报转 WebP 并按显示尺寸缩放（对外公开前做，显著降低首屏体积）

对外公开后作品库页要加载上百张图，原图 26MB 在手机上很慢。显示尺寸最大约 260px（详情页）
到 240px（检索页卡片），按 2 倍屏留到 520px 宽足够。

用法：python tools/optimize_images.py [--dry-run]
"""
import pathlib
import re
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET_W = 520          # 最大宽度（2 倍屏）
QUALITY = 82
DRY = '--dry-run' in sys.argv


def convert(jpg: pathlib.Path) -> tuple:
    """转成同目录同名 .webp，返回 (原字节, 新字节)。"""
    webp = jpg.with_suffix('.webp')
    if webp.exists() and webp.stat().st_mtime >= jpg.stat().st_mtime and not DRY:
        return jpg.stat().st_size, webp.stat().st_size
    im = Image.open(jpg).convert('RGB')
    if im.width > TARGET_W:
        im = im.resize((TARGET_W, round(im.height * TARGET_W / im.width)), Image.LANCZOS)
    if not DRY:
        im.save(webp, 'WEBP', quality=QUALITY, method=6)
    return jpg.stat().st_size, (webp.stat().st_size if webp.exists() else 0)


def process(data_file: str, img_dir: str, label: str):
    df = ROOT / data_file
    s = df.read_text(encoding='utf-8')
    paths = re.findall(r'"(assets/img/' + img_dir + r'/[^"]+\.jpg)"', s)
    if not paths:
        print(f'  {label}: 未找到条目'); return
    old_total = new_total = 0
    missing = []
    for p in paths:
        jpg = ROOT / p
        if not jpg.exists():
            missing.append(p); continue
        o, n = convert(jpg)
        old_total += o; new_total += n
    # 数据文件里改成 .webp
    new_s = re.sub(r'"(assets/img/' + img_dir + r'/([^"]+))\.jpg"', r'"\1.webp"', s)
    if not DRY:
        df.write_text(new_s, encoding='utf-8')
    print(f'  {label}: {len(paths)} 张  {old_total/1024/1024:.1f} MB → {new_total/1024/1024:.1f} MB'
          f'（{new_total/max(old_total,1)*100:.0f}%）' + (f'  缺失 {len(missing)}' if missing else ''))


def delete_originals():
    """确认 webp 都在之后，删除原 jpg（仓库体积减半；历史仍在 git 里）"""
    removed = 0
    for d in ('covers', 'posters'):
        for jpg in sorted((ROOT / 'assets/img' / d).glob('*.jpg')):
            if jpg.with_suffix('.webp').exists():
                jpg.unlink(); removed += 1
    print(f'  已删除原 jpg：{removed} 个')


if __name__ == '__main__':
    print('图片优化' + ('（试运行，不写文件）' if DRY else ''))
    process('data/posters.js', 'posters', '原创海报 posters')
    process('data/covers.js', 'covers', '真实封面 covers')
    if not DRY:
        delete_originals()
        p = ROOT / 'assets/img'
        for d in ('posters', 'covers'):
            fs = list((p / d).glob('*.webp'))
            print(f'  {d}: {len(fs)} 个 webp，共 {sum(f.stat().st_size for f in fs)/1024/1024:.1f} MB')
