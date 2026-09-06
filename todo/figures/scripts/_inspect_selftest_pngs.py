# -*- coding: utf-8 -*-
"""检查 balance selftest 保存的截图内容."""
from pathlib import Path
from PIL import Image

base = Path("build-app/Release")
for name in ["balance_selftest_plain.png", "balance_selftest_plain_off.png",
             "balance_selftest_layout.png", "balance_selftest_layout_off.png"]:
    p = base / name
    if not p.exists():
        print(f"{name}: MISSING")
        continue
    img = Image.open(p).convert("RGB")
    colors = img.getcolors(maxcolors=1 << 24)
    purple = sum(cnt for cnt, (r, g, b) in colors if b > g + 15 and b > 45 and r > 90)
    dark = sum(cnt for cnt, (r, g, b) in colors if r + g + b < 30)
    top = sorted(colors, reverse=True)[:4]
    print(f"{name}: size={img.size} distinct={len(colors)} purple_px={purple} "
          f"dark_px={dark} top={[c[1] for c in top]}")
