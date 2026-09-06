# -*- coding: utf-8 -*-
"""Generate chapter-0 (design derivation) figures.

One single dataset runs through all four figures:
a 5x5 blob with a diagonal tilt (main diagonal heavy, top-left side heavier).
Fig12: 3D surface + 2D heatmap  -> 肉眼发现不均匀
Fig13: 一阶矩(重心) 对倾斜近乎失明 (对照: 纯扭转数据, 重心偏移精确为 0)
Fig14: 二阶矩张量分解  M -> M0 -> D -> (iso, lambda)
Fig15: 主失衡轴 + 偏重侧铺色 -> 最终用户文案

图内不画角标; 图号只体现在文件名 FigNN 上, 与文档题注一一对应。
"""
from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

# ── 贯穿全文的唯一数据集: 5x5 斑块, 主对角(左上-右下)偏重 + 左上侧略重 ───
# 数值特征(脚本实算): 重心偏移 0.50 cell, iso=-0.042, lambda=0.139,
# 主轴沿 (0.71,0.71) 即左上—右下对角线, 两侧均值 2.60 vs 5.20。
V = np.array([
    [9, 6, 4, 2, 2],
    [6, 9, 5, 2, 2],
    [4, 5, 5, 2, 2],
    [2, 2, 2, 5, 3],
    [2, 2, 2, 3, 3.0],
])
# 纯扭转对照(180°旋转对称: 主对角重、反对角轻): 重心偏移精确为 0,
# lambda=0.136 仍很大 —— 用于演示一阶矩的结构性失明。
V_PURE_TWIST = np.array([
    [9, 6, 5, 3, 4],
    [6, 8, 5, 4, 3],
    [5, 5, 6, 5, 5],
    [3, 4, 5, 8, 6],
    [4, 3, 5, 6, 9.0],
])
THRESHOLD = 1.5
TWIST_THRESHOLD = 0.05


def analyze(values):
    """Replicates AnalyzeForceBalance's per-blob math on a full matrix blob."""
    rows, cols = values.shape
    rr, cc = np.mgrid[0:rows, 0:cols]
    mask = values > THRESHOLD
    r = rr[mask].astype(float)
    c = cc[mask].astype(float)
    v = values[mask]

    w_sum = v.sum()
    mu_r = (v * r).sum() / w_sum
    mu_c = (v * c).sum() / w_sum
    geo_r = r.mean()
    geo_c = c.mean()

    # Winsorize at in-blob 95th percentile
    w_cap = np.sort(v)[math.ceil(0.95 * len(v)) - 1]
    w = np.minimum(v, w_cap)

    dr = r - mu_r
    dc = c - mu_c
    m_rr = (w * dr * dr).sum() / w.sum()
    m_cc = (w * dc * dc).sum() / w.sum()
    m_rc = (w * dr * dc).sum() / w.sum()

    gdr = r - geo_r
    gdc = c - geo_c
    n = len(r)
    m0_rr = (gdr * gdr).sum() / n
    m0_cc = (gdc * gdc).sum() / n
    m0_rc = (gdr * gdc).sum() / n

    tr0 = m0_rr + m0_cc
    d_rr = (m_rr - m0_rr) / tr0
    d_cc = (m_cc - m0_cc) / tr0
    d_rc = (m_rc - m0_rc) / tr0

    iso = 0.5 * (d_rr + d_cc)
    a = 0.5 * (d_rr - d_cc)
    b = d_rc
    lam = math.sqrt(a * a + b * b)
    vr, vc = a + lam, b
    nrm = math.hypot(vr, vc)
    ax_r, ax_c = (vr / nrm, vc / nrm) if nrm > 1e-12 else (0.0, 0.0)

    t = (r - geo_r) * ax_r + (c - geo_c) * ax_c
    pos = t[t > 1e-9]
    neg = t[t < -1e-9]
    vpos = v[t > 1e-9]
    vneg = v[t < -1e-9]
    pos_mean = vpos.mean() if pos.size else -1.0
    neg_mean = vneg.mean() if neg.size else -1.0
    sign = 0.0 if (pos_mean < 0 and neg_mean < 0) else (1.0 if pos_mean >= neg_mean else -1.0)

    return dict(
        mu=(mu_r, mu_c), geo=(geo_r, geo_c),
        M=np.array([[m_rr, m_rc], [m_rc, m_cc]]),
        M0=np.array([[m0_rr, m0_rc], [m0_rc, m0_cc]]),
        D=np.array([[d_rr, d_rc], [d_rc, d_cc]]),
        iso=iso, a=a, b=b, lam=lam, axis=(ax_r, ax_c),
        t=t, r=r, c=c, v=v, mask=mask,
        heavy=(sign * ax_r, sign * ax_c),
        pos_mean=pos_mean, neg_mean=neg_mean,
    )


def save_figure(figure, name):
    figure.savefig(ROOT / name, dpi=170, bbox_inches="tight")
    plt.close(figure)


def draw_cells(axis, values, vmin=None, vmax=None):
    axis.imshow(values, cmap="YlOrRd", vmin=vmin or 1.0, vmax=vmax or 9.0,
                interpolation="nearest")
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_xlim(-0.5, values.shape[1] - 0.5)
    axis.set_ylim(values.shape[0] - 0.5, -0.5)


def ellipse_points(center, matrix, scale=2.0, n_pts=120):
    """Ellipse x^T M^{-1} x = scale^2 for symmetric positive matrix."""
    vals, vecs = np.linalg.eigh(matrix)
    vals = np.maximum(vals, 1e-12)
    theta = np.linspace(0, 2 * np.pi, n_pts)
    unit = np.stack([np.cos(theta), np.sin(theta)])          # 2 x N
    pts = vecs @ np.diag(np.sqrt(vals) * scale) @ unit        # 2 x N
    return center[1] + pts[1], center[0] + pts[0]            # x=col, y=row


# ── Fig12: 三维热力图发现不均匀 ─────────────────────────────────────
def fig12():
    res = analyze(V)
    # constrained layout 与 3D 轴不兼容(布局塌缩), 手动留出标题空间
    fig = plt.figure(figsize=(9.6, 4.4))
    fig.subplots_adjust(top=0.84, wspace=0.25)
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    rows, cols = V.shape
    xs, ys = np.meshgrid(np.arange(cols), np.arange(rows))
    ax1.plot_surface(xs, ys, V, cmap="YlOrRd", vmin=1, vmax=9,
                     rstride=1, cstride=1, linewidth=0.6,
                     edgecolor="#7a5c00", alpha=0.95)
    ax1.set_xticks(range(cols))
    ax1.set_yticks(range(rows))
    ax1.set_xlabel("列 c")
    ax1.set_ylabel("行 r")
    ax1.set_zlabel("压力值")
    ax1.view_init(elev=28, azim=-58)
    ax1.set_title("三维压力曲面", fontsize=11)

    ax2 = fig.add_subplot(1, 2, 2)
    draw_cells(ax2, V)
    for (r, c, v) in zip(res["r"], res["c"], res["v"]):
        ax2.text(c, r, f"{v:.0f}", ha="center", va="center", fontsize=9,
                 color="#212121")
    ax2.set_title("2D 视图（数值即权重 $V_i$，行列方向以右图为准）", fontsize=11)
    fig.suptitle("贯穿数据集：沿对角线隆起，左上端更高", fontsize=12)
    save_figure(fig, "Fig12_从三维热力图发现不均匀.png")
    print(f"[fig12] centroid=({res['mu'][0]:.3f},{res['mu'][1]:.3f}) "
          f"geo=({res['geo'][0]:.3f},{res['geo'][1]:.3f})")


# ── Fig13: 一阶矩(重心) 对倾斜失明的两种形态 ─────────────────────────
def fig13():
    res = analyze(V)
    res_pure = analyze(V_PURE_TWIST)

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4), layout="constrained")
    for ax, r in ((axes[0], res), (axes[1], res_pure)):
        draw_cells(ax, V if r is res else V_PURE_TWIST)
        ax.plot(r["geo"][1], r["geo"][0], marker="+", markersize=17,
                markeredgewidth=3, color="white", zorder=8)
        ax.plot(r["mu"][1], r["mu"][0], marker="o", markersize=9,
                markerfacecolor="#ef6c00", markeredgecolor="white",
                markeredgewidth=1.5, zorder=8)
        off = math.hypot(r["mu"][0] - r["geo"][0], r["mu"][1] - r["geo"][1])
        if off > 0.05:
            ax.add_patch(FancyArrowPatch((r["mu"][1], r["mu"][0]),
                                         (r["geo"][1], r["geo"][0]),
                                         arrowstyle="-|>", mutation_scale=16,
                                         linewidth=2.4, color="#ef6c00", zorder=7))

    off = math.hypot(res["mu"][0] - res["geo"][0], res["mu"][1] - res["geo"][1])
    axes[0].set_title(f"倾斜：重心只偏 {off:.2f} cell", fontsize=11)
    axes[0].text(0.02, 0.02, "十字=几何中心，圆点=加权重心",
                 transform=axes[0].transAxes, fontsize=8.5,
                 bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
    axes[1].set_title(f"纯扭转：重心偏移 0.00，λ 仍达 {res_pure['lam']:.2f}", fontsize=11)
    fig.suptitle("一阶矩（重心）对倾斜近乎失明：肉眼的不均匀远大于重心的偏移", fontsize=12)
    save_figure(fig, "Fig13_一阶矩的盲区.png")
    print(f"[fig13] tilt offset={off:.3f}, pure-twist offset=0.000 lambda={res_pure['lam']:.3f}")


# ── Fig14: 二阶矩张量分解 M -> M0 -> D -> (iso, lambda) ──────────────
def matrix_table(axis, matrix, title, highlight=None):
    axis.set_xticks([0, 1])
    axis.set_yticks([0, 1])
    axis.set_xticklabels(["rr", "cc"])
    axis.set_yticklabels(["rr", "cc"])
    axis.tick_params(labelsize=8, pad=2)
    data = [[matrix[0, 0], matrix[0, 1]], [matrix[1, 0], matrix[1, 1]]]
    norm = np.abs(matrix).max() if np.abs(matrix).max() > 1e-12 else 1.0
    axis.imshow(np.abs(matrix) / norm, cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            w = "bold" if highlight and (i, j) in highlight else "normal"
            axis.text(j, i, f"{data[i][j]:+.3f}", ha="center", va="center",
                      fontsize=8, weight=w,
                      color="#c62828" if highlight and (i, j) in highlight else "#212121")
    axis.set_title(title, fontsize=10)


def fig14():
    res = analyze(V)
    fig = plt.figure(figsize=(12.8, 4.0), layout="constrained")
    gs = fig.add_gridspec(1, 5, width_ratios=[1.15, 0.7, 0.7, 0.7, 0.8],
                          wspace=0.7)

    # (a) 椭圆对比: 基线 M0 vs 加权 M
    ax1 = fig.add_subplot(gs[0])
    draw_cells(ax1, V)
    ex0, ey0 = ellipse_points(res["geo"], res["M0"], scale=1.6)
    ex1, ey1 = ellipse_points(res["geo"], res["M"], scale=1.6)
    ax1.plot(ex0, ey0, "--", color="#1565c0", linewidth=2.2,
             label="等权基线 $M_0$")
    ax1.plot(ex1, ey1, "-", color="#c62828", linewidth=2.4,
             label="加权二阶矩 $M$")
    ax1.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax1.set_title("散布椭圆对比", fontsize=11)

    # (b) 三个矩阵 (扁平网格, 避免 constrained 塌缩)
    matrix_table(fig.add_subplot(gs[1]), res["M"], "加权 $M$",
                 highlight={(0, 1), (1, 0)})
    matrix_table(fig.add_subplot(gs[2]), res["M0"], "等权基线 $M_0$")
    matrix_table(fig.add_subplot(gs[3]), res["D"], "$D$（归一化）",
                 highlight={(0, 1), (1, 0)})

    # (c) iso vs lambda
    ax3 = fig.add_subplot(gs[4])
    bars = ax3.bar([0, 1], [abs(res["iso"]), res["lam"]],
                   color=["#90a4ae", "#c62828"], width=0.55)
    ax3.axhline(TWIST_THRESHOLD, color="#ef6c00", linestyle="--", linewidth=1.6)
    ax3.text(0.5, TWIST_THRESHOLD + 0.004, "阈值 0.05", fontsize=8,
             color="#ef6c00", ha="center")
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(["$|iso|$", "$\\lambda$"], fontsize=10)
    ax3.tick_params(axis="y", labelsize=8)
    ax3.set_title("迹分解", fontsize=11)
    for bar, val in zip(bars, [abs(res["iso"]), res["lam"]]):
        ax3.text(bar.get_x() + bar.get_width() / 2, val, f"{val:.3f}",
                 ha="center", va="bottom", fontsize=9, weight="bold")
    ax3.set_ylim(0, max(res["lam"], abs(res["iso"])) * 1.28 + 0.02)

    fig.suptitle("二阶矩登场：减基线、归一化、迹分解，异常集中在交叉项与 λ", fontsize=12)
    save_figure(fig, "Fig14_二阶张量分解.png")
    print(f"[fig14] M={res['M'].round(4).tolist()} M0={res['M0'].round(4).tolist()} "
          f"D={res['D'].round(4).tolist()} iso={res['iso']:.4f} lambda={res['lam']:.4f}")


# ── Fig15: 主失衡轴 + 偏重侧 -> 用户文案 ────────────────────────────
def fig15():
    res = analyze(V)
    geo_r, geo_c = res["geo"]
    ax_r, ax_c = res["axis"]
    heavy_r, heavy_c = res["heavy"]

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4), layout="constrained")
    ax = axes[0]
    draw_cells(ax, V)
    # 偏重侧铺色
    wash = np.zeros((*V.shape, 4))
    for (r, c, t) in zip(res["r"], res["c"], res["t"]):
        if (r - geo_r) * heavy_r + (c - geo_c) * heavy_c > 1e-9:
            wash[int(r), int(c)] = (0.63, 0.16, 0.86, 0.45)
    ax.imshow(wash, interpolation="nearest")
    # 双向主轴
    length = 2.3
    ax.plot([geo_c - ax_c * length, geo_c + ax_c * length],
            [geo_r - ax_r * length, geo_r + ax_r * length],
            linestyle="--", color="#c838ff", linewidth=2.6, zorder=7)
    ax.plot([geo_c - ax_c * length], [geo_r - ax_r * length], marker="|",
            markersize=14, color="#c838ff", zorder=7)
    ax.plot([geo_c + ax_c * length], [geo_r + ax_r * length], marker="|",
            markersize=14, color="#c838ff", zorder=7)
    ax.plot(geo_c, geo_r, marker="+", markersize=17, markeredgewidth=3,
            color="white", zorder=8)
    ax.set_title("紫色虚线=主失衡轴（双向），铺色=偏重侧", fontsize=11)
    ax.text(0.02, 0.02,
            f"轴两侧每 Cell 均值：{res['pos_mean']:.2f} vs {res['neg_mean']:.2f}",
            transform=ax.transAxes, fontsize=8.5,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))

    ax2 = axes[1]
    ax2.axis("off")
    ax2.text(0.03, 0.92, "数学到这里只能给一根双向轴：\n"
                          "偏量张量特征值 $\\pm\\lambda$ 对称，\n"
                          "$+v$ 与 $-v$ 方向异常强度相等，\n"
                          "“哪侧偏重”必须回原始数据做两侧均值比较。",
             fontsize=10.5, va="top",
             bbox=dict(facecolor="#eceff1", edgecolor="#90a4ae", boxstyle="round,pad=0.6"))
    ax2.text(0.03, 0.44,
             f"λ = {res['lam']:.3f} ≥ 0.05  →  触发倾斜提示\n\n"
             "最终翻译成用户文案：\n"
             "“压力沿左上—右下方向失衡，\n"
             "左上侧偏重，可能压头倾斜，\n"
             "请检查是否贴平。”",
             fontsize=11, va="top", color="#1b5e20",
             bbox=dict(facecolor="#e8f5e9", edgecolor="#66bb6a", boxstyle="round,pad=0.6"))
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    fig.suptitle("第三步：主轴 + 两侧均值 → 可执行的倾斜提示（不给第二个箭头）", fontsize=12)
    save_figure(fig, "Fig15_主轴与偏重侧.png")
    print(f"[fig15] axis=({ax_r:.3f},{ax_c:.3f}) heavy=({heavy_r:.3f},{heavy_c:.3f}) "
          f"pos_mean={res['pos_mean']:.3f} neg_mean={res['neg_mean']:.3f}")


if __name__ == "__main__":
    fig12()
    fig13()
    fig14()
    fig15()
    print("done")
