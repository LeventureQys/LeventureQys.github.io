# -*- coding: utf-8 -*-
"""碰撞检测：重画各图的注释/文本/图例/标题，检查其窗口边界框是否相交。

不重算数据，只 hook fig04/fig05/fig06 的绘制过程，在 savefig 前抓取
所有 Text/Annotation/Legend 的窗口 extent，两两求交。
"""
import itertools
import importlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import balance_figures as bf

_orig_savefig = matplotlib.figure.Figure.savefig


def check(fig, name):
    fig.canvas.draw()
    items = []
    for t in fig.texts:
        items.append(("suptitle/text", t.get_window_extent()))
    for ax in fig.axes:
        if ax.get_legend():
            items.append(("legend", ax.get_legend().get_window_extent()))
        for t in ax.texts:
            try:
                items.append((t.get_text()[:14], t.get_window_extent()))
            except Exception:
                pass
        if ax.get_title():
            items.append(("title:" + ax.get_title()[:12],
                          ax.title.get_window_extent()))
    bad = []
    for (n1, b1), (n2, b2) in itertools.combinations(items, 2):
        ix = max(0, min(b1.x1, b2.x1) - max(b1.x0, b2.x0))
        iy = max(0, min(b1.y1, b2.y1) - max(b1.y0, b2.y0))
        if ix > 2 and iy > 2:  # 容差 2px
            bad.append((n1, n2, round(ix), round(iy)))
    print(f"[{name}] 文本元素 {len(items)} 个, 重叠对 {len(bad)} 个")
    for b in bad:
        print("   重叠:", b)


def patched_savefig(self, fname, *a, **k):
    check(self, str(fname).split("/")[-1])
    return _orig_savefig(self, fname, *a, **k)


matplotlib.figure.Figure.savefig = patched_savefig
for fn in (bf.fig01, bf.fig02, bf.fig03, bf.fig04, bf.fig05, bf.fig06):
    fn()
print("碰撞检测完成")
