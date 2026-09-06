# -*- coding: utf-8 -*-
"""Blog figures: why gradients fail, how to read centroid / twist outputs.

Fig16: gradient field cannot tell the correction direction; twist = saddle.
Fig17: how to read the position channel (centroid + reference + arrow).
Fig18: how to read the twist channel (lambda gauge + axis + heavy side).
"""
from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

V = np.array([
    [9, 6, 4, 2, 2],
    [6, 9, 5, 2, 2],
    [4, 5, 5, 2, 2],
    [2, 2, 2, 5, 3],
    [2, 2, 2, 3, 3.0],
])
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
    vpos = v[t > 1e-9]
    vneg = v[t < -1e-9]
    pos_mean = vpos.mean() if vpos.size else -1.0
    neg_mean = vneg.mean() if vneg.size else -1.0
    sign = 0.0 if (pos_mean < 0 and neg_mean < 0) else (1.0 if pos_mean >= neg_mean else -1.0)

    return dict(mu=(mu_r, mu_c), geo=(geo_r, geo_c),
                iso=iso, lam=lam, axis=(ax_r, ax_c), a=a, b=b,
                t=t, r=r, c=c, v=v,
                heavy=(sign * ax_r, sign * ax_c),
                pos_mean=pos_mean, neg_mean=neg_mean)


def smooth_grid(values, factor=7):
    """Bilinear upsample so surfaces / gradients look continuous."""
    rows, cols = values.shape
    fr = np.linspace(0, rows - 1, rows * factor)
    fc = np.linspace(0, cols - 1, cols * factor)
    out = np.empty((len(fr), len(fc)))
    for i, r in enumerate(fr):
        r0 = min(int(r), rows - 2)
        rt = r - r0
        for j, c in enumerate(fc):
            c0 = min(int(c), cols - 2)
            ct = c - c0
            out[i, j] = ((1 - rt) * (1 - ct) * values[r0, c0]
                         + (1 - rt) * ct * values[r0, c0 + 1]
                         + rt * (1 - ct) * values[r0 + 1, c0]
                         + rt * ct * values[r0 + 1, c0 + 1])
    return out


def draw_cells(axis, values):
    axis.imshow(values, cmap="YlOrRd", vmin=1.0, vmax=9.0, interpolation="nearest")
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_xlim(-0.5, values.shape[1] - 0.5)
    axis.set_ylim(values.shape[0] - 0.5, -0.5)


def save_figure(figure, name):
    figure.savefig(ROOT / name, dpi=170, bbox_inches="tight")
    plt.close(figure)


# ── Fig16: 梯度为什么说不出"该修的方向" ─────────────────────────────
def fig16():
    res = analyze(V)
    fig = plt.figure(figsize=(12.6, 4.3))
    fig.subplots_adjust(top=0.82, wspace=0.28, left=0.04, right=0.97)

    # (a) 3D surface of the tilted dataset
    ax1 = fig.add_subplot(1, 3, 1, projection="3d")
    s = smooth_grid(V, 7)
    rows, cols = s.shape
    xs, ys = np.meshgrid(np.linspace(0, 4, cols), np.linspace(0, 4, rows))
    ax1.plot_surface(xs, ys, s, cmap="YlOrRd", vmin=1, vmax=9,
                     rstride=2, cstride=2, linewidth=0.2, edgecolor="#b08900", alpha=0.95)
    ax1.view_init(elev=26, azim=-58)
    ax1.set_xticks([]); ax1.set_yticks([]); ax1.set_zticks([])
    ax1.set_title("(a) 对角翘曲的压力曲面：一条脊", fontsize=10.5)

    # (b) uphill gradient quiver on the PURE TWIST grid: exact pairwise cancellation
    res_p = analyze(V_PURE_TWIST)
    ax2 = fig.add_subplot(1, 3, 2)
    draw_cells(ax2, V_PURE_TWIST)
    for (r, c, v) in zip(res_p["r"], res_p["c"], res_p["v"]):
        ax2.text(c, r, f"{v:.0f}", ha="center", va="center", fontsize=8, color="#212121")
    grad_r = np.gradient(s, axis=0)
    grad_c = np.gradient(s, axis=1)
    # smoothed pure-twist field for the quiver
    s_p = smooth_grid(V_PURE_TWIST, 7)
    gr_p = np.gradient(s_p, axis=0)
    gc_p = np.gradient(s_p, axis=1)
    sc = 0.55 / (np.hypot(gr_p[::7, ::7], gc_p[::7, ::7]).max() + 1e-9)
    total_r = total_c = 0.0
    for (r, c) in zip(res_p["r"], res_p["c"]):
        gi = int(round(r * 7)); gj = int(round(c * 7))
        gr, gc = gr_p[gi, gj], gc_p[gi, gj]
        if math.hypot(gr, gc) < 1e-6:
            continue
        ax2.add_patch(FancyArrowPatch((c, r), (c + gc * sc, r + gr * sc),
                                      arrowstyle="-|>", mutation_scale=9,
                                      linewidth=1.1, color="#0d47a1", alpha=0.9, zorder=6))
        total_r += gr; total_c += gc
    ax2.set_title("(b) 纯扭转数据的“上坡方向”（梯度）：\n蓝箭头两两相向/相背，逐格相加几乎归零", fontsize=10.5)

    # (c) pure twist surface, 180° rotation symmetric
    ax3 = fig.add_subplot(1, 3, 3, projection="3d")
    s2 = smooth_grid(V_PURE_TWIST, 7)
    rows2, cols2 = s2.shape
    xs2, ys2 = np.meshgrid(np.linspace(0, 4, cols2), np.linspace(0, 4, rows2))
    ax3.plot_surface(xs2, ys2, s2, cmap="YlOrRd", vmin=1, vmax=9,
                     rstride=2, cstride=2, linewidth=0.2, edgecolor="#b08900", alpha=0.95)
    ax3.view_init(elev=26, azim=-58)
    ax3.set_xticks([]); ax3.set_yticks([]); ax3.set_zticks([])
    ax3.set_title("(c) 纯扭转（马鞍面）：\n整体旋转 180° 图形不变", fontsize=10.5)

    fig.suptitle("梯度是局部量，扭转是全局形态：逐点梯度两两抵消，说不出“该往哪修”", fontsize=12)
    save_figure(fig, "Fig16_梯度与扭转的本质.png")
    print(f"[fig16] grad sum = ({total_r:.3f},{total_c:.3f})")


# ── Fig17: 位置通道（重心坐标）怎么读 ───────────────────────────────
def fig17():
    res = analyze(V)
    mu_r, mu_c = res["mu"]
    geo_r, geo_c = res["geo"]
    off = math.hypot(mu_r - geo_r, mu_c - geo_c)

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5), layout="constrained",
                             gridspec_kw={"width_ratios": [1.0, 0.92]})
    ax = axes[0]
    draw_cells(ax, V)
    ax.plot(geo_c, geo_r, marker="+", markersize=18, markeredgewidth=3, color="white", zorder=8)
    ax.plot(mu_c, mu_r, marker="o", markersize=10, markerfacecolor="#ef6c00",
            markeredgecolor="white", markeredgewidth=1.5, zorder=9)
    ax.add_patch(FancyArrowPatch((mu_c, mu_r), (geo_c, geo_r), arrowstyle="-|>",
                                 mutation_scale=17, linewidth=2.6, color="#ef6c00", zorder=7))
    ax.annotate("", xy=(mu_c, mu_r + 0.42), xytext=(geo_c, geo_r + 0.42),
                arrowprops=dict(arrowstyle="<->", color="white", lw=1.4))
    ax.text((mu_c + geo_c) / 2 + 0.15, (mu_r + geo_r) / 2 + 0.5,
            f"偏差 {off:.2f} cell", fontsize=9, color="white",
            bbox=dict(facecolor="#37474f", alpha=0.8, edgecolor="none", pad=2))
    ax.text(0.02, 0.02, "白十字=参考中心　橙点=当前受力中心　橙箭头=建议微调方向",
            transform=ax.transAxes, fontsize=8.5,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
    ax.set_title("画面上你看到的三样东西", fontsize=11)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.text(0.02, 0.97,
             "读法（按顺序）：\n"
             "① 只看橙箭头的方向——它回答“往哪挪”。\n"
             "    箭头从当前受力中心指向参考中心，挪压头，\n"
             "    不是挪传感器、更不是照着紫色轴线推。\n"
             "② 再看偏差数值：以 cell 计（有物理布局时换算 mm），\n"
             "    与“允许偏差”比较，达标就显示“受力中心已对齐”。\n"
             "③ 前提检查：画面上没有倾斜提示时，箭头才可信。\n"
             "    一旦出现“可能压头倾斜”，先停下检查贴平，\n"
             "    此时照箭头挪只会越挪越乱。",
             fontsize=10.5, va="top", linespacing=1.55,
             bbox=dict(facecolor="#eceff1", edgecolor="#90a4ae", boxstyle="round,pad=0.6"))
    ax2.text(0.02, 0.30,
             "两个常见误读：\n"
             "· 箭头长度 ≠ 应移动的距离，它只给方向；\n"
             "· 参考中心是算法选的参考点（已知压头几何 >\n"
             "  稳定接触掩码 > 临时峰值核心），不是精密测出的\n"
             "  压头机械中心。",
             fontsize=10, va="top", linespacing=1.5, color="#4e342e",
             bbox=dict(facecolor="#fbe9e7", edgecolor="#ff8a65", boxstyle="round,pad=0.6"))
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    fig.suptitle("位置通道：重心坐标怎么读（只回答“往哪挪”）", fontsize=12)
    save_figure(fig, "Fig17_重心坐标怎么读.png")
    print(f"[fig17] offset={off:.3f}")


# ── Fig18: 扭转通道怎么读 ───────────────────────────────────────────
def fig18():
    res = analyze(V)
    geo_r, geo_c = res["geo"]
    ax_r, ax_c = res["axis"]
    heavy_r, heavy_c = res["heavy"]
    lam = res["lam"]

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.6), layout="constrained",
                             gridspec_kw={"width_ratios": [1.0, 0.95]})
    ax = axes[0]
    draw_cells(ax, V)
    wash = np.zeros((*V.shape, 4))
    for (r, c, t) in zip(res["r"], res["c"], res["t"]):
        if (r - geo_r) * heavy_r + (c - geo_c) * heavy_c > 1e-9:
            wash[int(r), int(c)] = (0.63, 0.16, 0.86, 0.45)
    ax.imshow(wash, interpolation="nearest")
    length = 2.35
    ax.plot([geo_c - ax_c * length, geo_c + ax_c * length],
            [geo_r - ax_r * length, geo_r + ax_r * length],
            linestyle="--", color="#c838ff", linewidth=2.6, zorder=7)
    for sgn in (-1, 1):
        ax.plot([geo_c + sgn * ax_c * length], [geo_r + sgn * ax_r * length],
                marker="|", markersize=14, color="#c838ff", zorder=7)
    ax.text(0.02, 0.02, "紫色双向虚线=主失衡轴　紫色铺色=偏重侧",
            transform=ax.transAxes, fontsize=8.5,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=1.5))
    # simulated message bar
    ax.annotate("压力沿左上—右下方向失衡，左上侧偏重，\n可能压头倾斜，请检查是否贴平",
                xy=(0.98, 0.02), xycoords="axes fraction", ha="right", va="bottom",
                fontsize=9.5, color="white",
                bbox=dict(facecolor="#c62828", edgecolor="none", pad=4))
    ax.set_title("画面元素：轴 + 铺色 + 一句话", fontsize=11)

    ax2 = axes[1]
    ax2.axis("off")
    # lambda gauge
    gy = 0.88
    ax2.plot([0.05, 0.95], [gy, gy], color="#cfd8dc", linewidth=10, solid_capstyle="butt")
    frac = min(lam / 0.25, 1.0)
    ax2.plot([0.05, 0.05 + frac * 0.9], [gy, gy], color="#c62828", linewidth=10,
             solid_capstyle="butt")
    thr_x = 0.05 + (TWIST_THRESHOLD / 0.25) * 0.9
    ax2.plot([thr_x, thr_x], [gy - 0.045, gy + 0.045], color="#ef6c00",
             linewidth=2.4, linestyle="--")
    ax2.text(thr_x, gy + 0.055, f"触发阈值 {TWIST_THRESHOLD}", fontsize=9,
             color="#ef6c00", ha="center")
    ax2.text(0.05, gy - 0.075, "0", fontsize=9, color="#607d8b")
    ax2.text(0.95, gy - 0.075, "0.25", fontsize=9, color="#607d8b", ha="right")
    ax2.text(0.05 + frac * 0.9, gy + 0.055, f"λ = {lam:.3f}", fontsize=10,
             color="#c62828", ha="left", weight="bold")
    ax2.text(0.5, gy + 0.13, "失衡强度 λ（无量纲，只用来触发提示和定轴向）",
             fontsize=10, ha="center")

    ax2.text(0.02, 0.66,
             "文案的三种形态（为什么是三种，见正文）：\n"
             "① 两侧每格均值差得开 → “沿左上—右下方向失衡，左上侧偏重”\n"
             "    （轴向 + 偏重侧 + 铺色，信息最全）；\n"
             "② 重压正好压在轴线上，两侧相当 → “沿该方向集中”，\n"
             "    不指认偏重侧、不铺色；\n"
             "③ 两侧没有可比数据 / 主轴退化 → “方向不确定”，\n"
             "    只保留“检查贴平”的建议。",
             fontsize=10, va="top", linespacing=1.55,
             bbox=dict(facecolor="#ede7f6", edgecolor="#9575cd", boxstyle="round,pad=0.6"))
    ax2.text(0.02, 0.235,
             "最容易犯的错：把紫色轴线当成箭头。\n"
             "轴是双向的——数学上“左上重右下轻”和“左下重右上轻”\n"
             "给出同一根轴，哪侧偏重要靠两侧均值比出来。\n"
             "所以：箭头=动作（挪），轴线/颜色=问题（检查贴平）。",
             fontsize=10, va="top", linespacing=1.5, color="#4a148c",
             bbox=dict(facecolor="#f3e5f5", edgecolor="#ce93d8", boxstyle="round,pad=0.6"))
    ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    fig.suptitle("扭转通道怎么读：λ 管报不报，轴向管说哪条线，铺色管哪侧重", fontsize=12)
    save_figure(fig, "Fig18_扭转怎么读.png")
    print(f"[fig18] lam={lam:.3f} pos={res['pos_mean']:.2f} neg={res['neg_mean']:.2f}")


# ── Fig19: 重心的核 vs 人眼的朝向滤波器 ───────────────────────────
def fig19():
    fig = plt.figure(figsize=(11.6, 4.4))
    fig.subplots_adjust(top=0.80, wspace=0.30, left=0.04, right=0.97)

    # (a) the kernel of the first moment: distinct patterns, same centroid
    res_p = analyze(V_PURE_TWIST)
    a, b = res_p["a"], res_p["b"]

    uni = np.full((3, 3), 5.0)
    tw1 = np.array([[9, 4, 3], [4, 5, 4], [3, 4, 9.0]])   # main-diag heavy
    tw2 = np.array([[3, 4, 9], [4, 5, 4], [9, 4, 3.0]])   # anti-diag heavy
    one = np.array([[5, 5, 5], [5, 7, 5], [5, 5, 5.0]])   # 180-symmetric core bump
    panels = [(uni, "均匀"), (tw1, "主对角翘曲"), (tw2, "反对角翘曲"), (one, "中心加重")]
    for k, (vals, name) in enumerate(panels):
        axk = fig.add_subplot(2, 5, k + 1)
        axk.imshow(vals, cmap="YlOrRd", vmin=1, vmax=9, interpolation="nearest")
        axk.set_xticks([]); axk.set_yticks([])
        v = vals.flatten()
        rr, cc = np.mgrid[0:3, 0:3]
        mu_r = (v * rr.flatten()).sum() / v.sum()
        mu_c = (v * cc.flatten()).sum() / v.sum()
        axk.plot(mu_c, mu_r, marker="o", markersize=7, markerfacecolor="#1e88e5",
                 markeredgecolor="white", markeredgewidth=1.2)
        axk.set_title(name, fontsize=9.5)
        if k == 0:
            axk.set_ylabel("重心全在中心", fontsize=9.5)

    # what the centroid "sees": one collapsed point
    axc = fig.add_subplot(2, 5, 5)
    axc.axis("off")
    axc.plot(0.5, 0.5, marker="o", markersize=16, markerfacecolor="#1e88e5",
             markeredgecolor="white", markeredgewidth=1.5)
    axc.text(0.5, 0.28, "重心的视角：\n左边四个分布\n压成同一个点", fontsize=9,
             ha="center", va="top", color="#1565c0")
    axc.set_xlim(0, 1); axc.set_ylim(0, 1)

    # (b) oriented response |q(theta)| of the pure-twist field; peaks = principal axis
    ax2 = fig.add_subplot(2, 1, 2)
    thetas = np.linspace(0, 180, 361)
    qs = []
    for th in thetas:
        ur, uc = math.sin(math.radians(th)), math.cos(math.radians(th))
        qs.append(a * (ur * ur - uc * uc) + 2 * b * ur * uc)
    qs = np.abs(np.array(qs))
    ax2.plot(thetas, qs, color="#6a1b9a", linewidth=2.2)
    ax2.fill_between(thetas, qs, color="#6a1b9a", alpha=0.12)
    ax2.axhline(res_p["lam"], color="#c62828", linestyle="--", linewidth=1.4)
    ax2.text(2, res_p["lam"] + 0.004, f"峰值 = λ = {res_p['lam']:.3f}", fontsize=9,
             color="#c62828")
    ax2.set_xticks([0, 45, 90, 135, 180])
    ax2.set_xlabel("滤波器朝向 θ（度，0°=水平向右）", fontsize=10)
    ax2.set_ylabel("响应 |q(θ)|", fontsize=10)
    ax2.tick_params(labelsize=9)
    ax2.set_title("人眼那套朝向滤波器看到的东西：把扭转数据喂给各个朝向的“脊探测器”，\n"
                  "响应在 45° 和 135° 达到峰值 λ——峰值朝向就是主失衡轴，峰值幅度就是失衡强度",
                  fontsize=10.5)

    fig.suptitle("重心的核（上）：不同分布坍缩成同一点；朝向响应（下）：看见脊 = 找到响应峰值", fontsize=12)
    save_figure(fig, "Fig19_重心看不见而人眼看得见.png")
    print(f"[fig19] pure-twist a={a:.4f} b={b:.4f} lam={res_p['lam']:.4f}")


if __name__ == "__main__":
    fig16()
    fig17()
    fig18()
    fig19()
    print("done")
