# -*- coding: utf-8 -*-
"""Generate the simplified figures used by the revised balance-analysis document."""
from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def save_figure(figure, name):
    figure.savefig(ROOT / name, dpi=170, bbox_inches="tight")
    plt.close(figure)


def draw_cells(axis, values, mask=None, vmin=None, vmax=None):
    values = np.asarray(values, dtype=float)
    if mask is None:
        mask = np.ones(values.shape, dtype=bool)
    else:
        mask = np.asarray(mask, dtype=bool)
    visible = np.where(mask, values, np.nan)
    axis.imshow(visible, cmap="YlOrRd", vmin=vmin, vmax=vmax, interpolation="nearest")
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_xlim(-0.5, values.shape[1] - 0.5)
    axis.set_ylim(values.shape[0] - 0.5, -0.5)


def draw_true_boundary(axis, mask, color="#e53935", linewidth=2.5):
    mask = np.asarray(mask, dtype=bool)
    rows, cols = mask.shape
    for row in range(rows):
        for col in range(cols):
            if not mask[row, col]:
                continue
            edges = [
                ((col - 0.5, row - 0.5), (col + 0.5, row - 0.5), row == 0 or not mask[row - 1, col]),
                ((col + 0.5, row - 0.5), (col + 0.5, row + 0.5), col == cols - 1 or not mask[row, col + 1]),
                ((col + 0.5, row + 0.5), (col - 0.5, row + 0.5), row == rows - 1 or not mask[row + 1, col]),
                ((col - 0.5, row + 0.5), (col - 0.5, row - 0.5), col == 0 or not mask[row, col - 1]),
            ]
            for start, end, visible in edges:
                if visible:
                    axis.plot([start[0], end[0]], [start[1], end[1]], color=color,
                              linewidth=linewidth, solid_capstyle="round", zorder=6)


def add_center_markers(axis, target, current, arrow_color="#ef6c00"):
    axis.plot(target[1], target[0], marker="+", markersize=17, markeredgewidth=3,
              color="white", zorder=8)
    axis.plot(current[1], current[0], marker="o", markersize=9, markerfacecolor=arrow_color,
              markeredgecolor="white", markeredgewidth=1.5, zorder=8)
    axis.add_patch(FancyArrowPatch((current[1], current[0]), (target[1], target[0]),
                                   arrowstyle="-|>", mutation_scale=16, linewidth=2.4,
                                   color=arrow_color, zorder=7))


def fig_user_view():
    values = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 3, 4, 5, 6, 5, 0],
        [0, 3, 6, 8, 8, 5, 0],
        [0, 2, 4, 7, 8, 4, 0],
        [0, 2, 3, 5, 6, 3, 0],
        [0, 1, 2, 3, 3, 2, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ], dtype=float)
    mask = values > 0
    figure = plt.figure(figsize=(12.0, 6.3))
    grid_axis = figure.add_axes([0.04, 0.12, 0.46, 0.78])
    draw_cells(grid_axis, values, mask, 0, 9)
    mean_value = values[mask].mean()
    deviation = values[mask] - mean_value
    spread = values[mask].std()
    for row, col in zip(*np.where(mask)):
        if values[row, col] > mean_value + 0.65 * spread:
            grid_axis.add_patch(Rectangle((col - 0.5, row - 0.5), 1, 1,
                                          facecolor="#ef5350", alpha=0.38, edgecolor="none", zorder=4))
        elif values[row, col] < mean_value - 0.65 * spread:
            grid_axis.add_patch(Rectangle((col - 0.5, row - 0.5), 1, 1,
                                          facecolor="#42a5f5", alpha=0.38, edgecolor="none", zorder=4))
    draw_true_boundary(grid_axis, mask)
    target = (2.45, 3.0)
    current = (2.85, 4.25)
    add_center_markers(grid_axis, target, current)
    grid_axis.text(target[1] - 0.18, target[0] - 0.42, "目标", color="white", fontsize=10,
                   ha="right", va="bottom", weight="bold", zorder=9,
                   bbox=dict(facecolor="black", alpha=0.65, pad=2, edgecolor="none"))
    grid_axis.text(current[1] + 0.18, current[0] + 0.40, "当前", color="white", fontsize=10,
                   ha="left", va="top", weight="bold", zorder=9,
                   bbox=dict(facecolor="black", alpha=0.65, pad=2, edgecolor="none"))
    grid_axis.set_title("同一个独立受力区域", fontsize=14, pad=12)

    figure.text(0.56, 0.958, "用户只需要按三层信息阅读", fontsize=15, weight="bold",
                color="#263238", va="center")
    cards = [
        (0.71, "1", "先看箭头", "橙点是当前受力中心，白十字是目标位置。\n把压头向箭头方向微调。", "#fff3e0"),
        (0.47, "2", "再看颜色", "红色表示这一块相对偏重，蓝色表示相对偏轻。\n颜色不是绝对安全等级。", "#e3f2fd"),
        (0.23, "3", "最后看提示", "出现“可能倾斜”时会标出失衡方向\n（左上—右下式双向轴），此时不要平移，\n先检查压头是否贴平。", "#f3e5f5"),
    ]
    for y, number, title, text, color in cards:
        figure.add_artist(FancyBboxPatch((0.56, y), 0.39, 0.18,
                                         boxstyle="round,pad=0.012,rounding_size=0.02",
                                         transform=figure.transFigure, facecolor=color,
                                         edgecolor="#90a4ae", linewidth=1.0))
        figure.text(0.585, y + 0.122, number, fontsize=17, weight="bold", color="#455a64",
                    ha="center", va="center")
        figure.text(0.615, y + 0.135, title, fontsize=12, weight="bold", color="#263238",
                    ha="left", va="center")
        figure.text(0.615, y + 0.056, text, fontsize=10, color="#37474f",
                    ha="left", va="center", linespacing=1.3)
    figure.text(0.57, 0.115, "红色轮廓 = 一个独立受力区域；不是把整个外接矩形当成受力区域。",
                fontsize=10.5, color="#b71c1c")
    figure.text(0.04, 0.035, "示意图：箭头表示位置调整方向；倾斜提示不提供第二个“推动方向”。",
                fontsize=10, color="#546e7a")
    save_figure(figure, "Fig08_用户如何读图.png")


def fig_blind_spot():
    uniform = np.full((3, 3), 5.0)
    twisted = np.array([[10.0, 4.0, 4.0], [4.0, 7.0, 4.0], [4.0, 4.0, 10.0]])
    shifted = np.array([[8.0, 8.0, 4.0], [8.0, 8.0, 4.0], [4.0, 4.0, 4.0]])
    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.7))
    cases = [
        (uniform, "A  正常均匀", "中心重合\n无额外提示", "#2e7d32"),
        (twisted, "B  对角失衡", "中心仍重合\n箭头为零，但标出失衡方向", "#7b1fa2"),
        (shifted, "C  单侧偏重", "中心偏移\n箭头给出调整方向", "#ef6c00"),
    ]
    for axis, (matrix, title, note, color) in zip(axes, cases):
        draw_cells(axis, matrix, np.ones_like(matrix, dtype=bool), 0, 10)
        for row in range(3):
            for col in range(3):
                axis.text(col, row, f"{matrix[row, col]:.0f}", ha="center", va="center",
                          fontsize=13, color="#263238", zorder=4)
        positions = np.argwhere(matrix > 0)
        geometric = positions.mean(axis=0)
        weighted = (positions * matrix[matrix > 0, None]).sum(axis=0) / matrix.sum()
        axis.plot(geometric[1], geometric[0], marker="+", markersize=16, markeredgewidth=3,
                  color="white", zorder=7)
        axis.plot(weighted[1], weighted[0], marker="o", markersize=10, markerfacecolor=color,
                  markeredgecolor="white", markeredgewidth=1.5, zorder=8)
        if title.startswith("B"):
            axis.set_xlim(-1.25, 3.25)
            axis.set_ylim(3.25, -1.25)
            axis.plot([-0.45, 2.45], [-0.45, 2.45], color="#7b1fa2", linestyle="--", linewidth=2)
            axis.text(-0.62, -0.62, "左上", fontsize=10.5, color="#6a1b9a",
                      ha="right", va="top", weight="bold")
            axis.text(2.62, 2.62, "右下", fontsize=10.5, color="#6a1b9a",
                      ha="left", va="bottom", weight="bold")
        elif title.startswith("C"):
            axis.add_patch(FancyArrowPatch((weighted[1], weighted[0]), (geometric[1], geometric[0]),
                                           arrowstyle="-|>", mutation_scale=17, linewidth=2.5,
                                           color=color, zorder=8))
        axis.set_title(title, fontsize=12, pad=10)
        axis.set_xlabel(note, fontsize=10, color=color, labelpad=10)
    figure.suptitle("为什么不能只看一个重心箭头", fontsize=15, weight="bold")
    figure.text(0.5, 0.02,
                "A 与 B 的箭头都可能为零，但含义不同：B 的方向信息是“沿哪条轴失衡”，用双向轴 + 方位命名表达，不用箭头。",
                ha="center", fontsize=11, color="#37474f")
    figure.tight_layout(rect=(0, 0.08, 1, 0.90))
    save_figure(figure, "Fig09_为什么需要第二个提示.png")


def add_flow_box(axis, x, y, width, height, title, subtitle, color):
    axis.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.015,rounding_size=0.02",
                                  facecolor=color, edgecolor="#546e7a", linewidth=1.2))
    axis.text(x + width / 2, y + height * 0.62, title, ha="center", va="center",
              fontsize=11, weight="bold", color="#263238")
    axis.text(x + width / 2, y + height * 0.30, subtitle, ha="center", va="center",
              fontsize=9, color="#455a64", linespacing=1.2)


def add_flow_arrow(axis, start, end):
    axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                   linewidth=1.7, color="#607d8b"))


def fig_flow():
    figure, axis = plt.subplots(figsize=(13.2, 5.8))
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")

    # 第一行：输入 → 有效区域 → 逐区域分析
    add_flow_box(axis, 0.03, 0.70, 0.17, 0.18, "当前显示数据", "同一单位\n未做颜色裁剪", "#e3f2fd")
    add_flow_box(axis, 0.255, 0.70, 0.17, 0.18, "有效区域", "阈值 + 有效掩码\n连通区域", "#e8f5e9")
    add_flow_box(axis, 0.48, 0.70, 0.17, 0.18, "逐区域分析", "每个区域独立\n保留真实边界", "#fff3e0")
    add_flow_arrow(axis, (0.20, 0.79), (0.255, 0.79))
    add_flow_arrow(axis, (0.425, 0.79), (0.48, 0.79))

    # 第二行：三类结果横排，从“逐区域分析”向下扇出（发散扇形，无交叉）
    add_flow_box(axis, 0.08, 0.42, 0.24, 0.16, "位置偏移", "当前中心 → 目标中心\n单头箭头", "#fff8e1")
    add_flow_box(axis, 0.385, 0.42, 0.24, 0.16, "倾斜风险", "分布形状/方向异常\n检查压头", "#f3e5f5")
    add_flow_box(axis, 0.69, 0.42, 0.24, 0.16, "可信度", "饱和、面积\n数据有效性", "#eceff1")
    add_flow_arrow(axis, (0.51, 0.70), (0.20, 0.58))
    add_flow_arrow(axis, (0.565, 0.70), (0.505, 0.58))
    add_flow_arrow(axis, (0.62, 0.70), (0.81, 0.58))

    # 第三行：三类结果垂直下落到加宽的“用户提示”条（无交叉）
    add_flow_box(axis, 0.14, 0.14, 0.72, 0.14, "用户提示", "只给可执行结论，不显示数学术语", "#ffebee")
    for x_drop in (0.20, 0.505, 0.81):
        add_flow_arrow(axis, (x_drop, 0.42), (x_drop, 0.28))

    axis.text(0.5, 0.96, "推荐处理顺序：先统一数据口径，再分区域，最后生成两类提示和可信度状态",
              ha="center", va="center", fontsize=14, weight="bold", color="#263238")
    axis.text(0.5, 0.055,
              "明确非目标：不判断传感器制造均匀度，不测量压头精确姿态，不在饱和后猜测真实力值。",
              ha="center", va="center", fontsize=10.5, color="#b71c1c")
    save_figure(figure, "Fig10_推荐数据流.png")


def fig_contour():
    mask = np.array([
        [False, True, True, False, False, False],
        [False, True, True, True, True, False],
        [False, True, True, False, True, False],
        [False, False, True, False, True, False],
        [False, False, True, True, True, False],
        [False, False, False, False, False, False],
    ])
    values = np.where(mask, 4.0, np.nan)
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 5.0))
    for axis in axes:
        axis.imshow(values, cmap="Oranges", vmin=0, vmax=5, interpolation="nearest")
        axis.set_xticks([])
        axis.set_yticks([])
        axis.set_xlim(-0.5, 5.5)
        axis.set_ylim(5.5, -0.5)
    draw_true_boundary(axes[0], mask, "#e53935", 2.8)
    axes[0].set_title("应显示：真实连通边界", fontsize=13, color="#2e7d32", pad=12)
    axes[0].text(2.6, 5.95, "空洞和外部区域不属于受力斑块", ha="center", fontsize=10, color="#455a64")
    axes[1].add_patch(Rectangle((0.5, -0.5), 4, 5, fill=False, edgecolor="#e53935",
                                linewidth=2.8, linestyle="--"))
    axes[1].plot([0.3, 4.8], [0.2, 4.7], color="#b71c1c", linewidth=3)
    axes[1].plot([0.3, 4.8], [4.7, 0.2], color="#b71c1c", linewidth=3)
    axes[1].set_title("不能显示：整个外接矩形", fontsize=13, color="#b71c1c", pad=12)
    axes[1].text(2.5, 5.95, "会把空白区域误标成受力区域", ha="center", fontsize=10, color="#455a64")
    figure.suptitle("“连通斑块”必须按真实 Cell 边界绘制", fontsize=15, weight="bold")
    figure.tight_layout(rect=(0, 0.05, 1, 0.91))
    save_figure(figure, "Fig11_真实斑块边界.png")


if __name__ == "__main__":
    fig_user_view()
    fig_blind_spot()
    fig_flow()
    fig_contour()
    print("generated revised balance figures in", ROOT)
