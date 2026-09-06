# -*- coding: utf-8 -*-
"""QA check: detect text-text overlaps and out-of-canvas text in chapter0 figures."""
import importlib.util
import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

spec = importlib.util.spec_from_file_location(
    "c0", r"Document\Update\Dev-Version\v2.2\v2.2.2 - 均匀度测试的完整需求\figures\scripts\chapter0_figures.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# keep figures open so we can inspect them
m.plt.close = lambda *a, **k: None

m.fig12()
m.fig13()
m.fig14()
m.fig15()


def collect_texts(fig):
    texts = []
    for ax in fig.get_axes():
        texts.extend(t for t in ax.texts if t.get_visible() and t.get_text().strip())
        for name in ("title", "_left_title", "_right_title"):
            t = getattr(ax, name, None)
            if t is not None and t.get_text().strip():
                texts.append(t)
        if ax.get_legend() is not None:
            texts.extend(ax.get_legend().get_texts())
        if getattr(ax, "axison", True):  # axis("off") panels don't draw ticks
            texts.extend(ax.get_xticklabels() + ax.get_yticklabels())
    texts.extend(t for t in fig.texts if t.get_visible() and t.get_text().strip())
    return texts


def overlap_area(a, b):
    x0 = max(a.x0, b.x0)
    x1 = min(a.x1, b.x1)
    y0 = max(a.y0, b.y0)
    y1 = min(a.y1, b.y1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


for num in plt.get_fignums():
    fig = plt.figure(num)
    renderer = fig.canvas.get_renderer()
    fig.canvas.draw()
    fb = fig.bbox
    texts = collect_texts(fig)
    boxes = []
    for t in texts:
        try:
            boxes.append((t, t.get_window_extent(renderer)))
        except Exception:
            pass
    problems = []
    for (ta, ba), (tb, bb) in itertools.combinations(boxes, 2):
        area = overlap_area(ba, bb)
        if area > 4.0:  # px^2 tolerance
            problems.append(
                f"OVERLAP {area:7.0f}px2 | '{ta.get_text()[:24]}' x '{tb.get_text()[:24]}'")
    for t, b in boxes:
        if b.x0 < fb.x0 - 1 or b.x1 > fb.x1 + 1 or b.y0 < fb.y0 - 1 or b.y1 > fb.y1 + 1:
            problems.append(f"OUTCANVAS       | '{t.get_text()[:36]}' bbox={b.frozen()}")
    print(f"figure {num}: {len(texts)} texts, {len(problems)} problems")
    for p in problems:
        print("   ", p)
