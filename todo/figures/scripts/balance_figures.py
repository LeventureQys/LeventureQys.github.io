# -*- coding: utf-8 -*-
"""受力平衡分析算法配图与数值验证脚本。

复刻 src/domain/balance/force_balance_analyzer.cpp 的核心算法
（连通域、一阶重心、峰值核心参照、winsorize-p95 二阶张量、饱和占比），
对文档中引用的反例做数值验证，并生成 Fig01–Fig06。

运行:  python balance_figures.py   （在 figures/scripts 目录下；另输出 Fig04–Fig06，见函数 fig04/fig05/fig06）
输出:  ../Fig01_算法数据流.png  ../Fig02_一阶对称盲区与二阶检出.png
       ../Fig03_偏差张量分解.png
"""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch, FancyArrow

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False


# ----------------------------------------------------------------------
# 算法复刻（与 C++ 逐条对应）
# ----------------------------------------------------------------------
def second_order(cells, values):
    n = len(cells)
    if n < 9:
        return None
    # winsorize 到斑块内 95 分位（与 C++ nth_element 同义）
    w_cap = np.percentile(values, 95)  # C++: ceil(0.95n)-1 处的次序统计量
    idx95 = min(n - 1, math.ceil(0.95 * n) - 1)
    w_cap = np.sort(values)[idx95]
    w = np.minimum(values, w_cap)
    cells = np.asarray(cells, float)
    mu_r = np.sum(w * cells[:, 0]) / np.sum(w)
    mu_c = np.sum(w * cells[:, 1]) / np.sum(w)
    geo_r = cells[:, 0].mean()
    geo_c = cells[:, 1].mean()
    dr, dc = cells[:, 0] - mu_r, cells[:, 1] - mu_c
    m_rr = np.sum(w * dr * dr) / np.sum(w)
    m_cc = np.sum(w * dc * dc) / np.sum(w)
    m_rc = np.sum(w * dr * dc) / np.sum(w)
    d0r, d0c = cells[:, 0] - geo_r, cells[:, 1] - geo_c
    m0_rr = np.mean(d0r * d0r)
    m0_cc = np.mean(d0c * d0c)
    m0_rc = np.mean(d0r * d0c)
    tr0 = m0_rr + m0_cc
    if tr0 <= 1e-12:
        return None
    d_rr = (m_rr - m0_rr) / tr0
    d_cc = (m_cc - m0_cc) / tr0
    d_rc = (m_rc - m0_rc) / tr0
    iso = 0.5 * (d_rr + d_cc)
    a, b = 0.5 * (d_rr - d_cc), d_rc
    lam = math.hypot(a, b)
    axis = (0.0, 0.0)
    if lam > 1e-12:
        vr, vc = a + lam, b
        nrm = math.hypot(vr, vc)
        axis = (vr / nrm, vc / nrm)
    return dict(iso=iso, lam=lam, axis=axis,
                mu_rc_raw=m_rc, d_rc=d_rc)


def first_order(mat):
    """全斑一阶重心与几何中心（旧版理论重心）。"""
    pos = np.argwhere(mat > 0)
    w = mat[mat > 0]
    mu = (pos * w[:, None]).sum(0) / w.sum()
    geo = pos.mean(0)
    return mu, geo


# ----------------------------------------------------------------------
# Fig01 算法数据流（坐标规划，无碰撞）
# ----------------------------------------------------------------------
def fig01():
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.set_xlim(0, 115)
    ax.set_ylim(0, 56)
    ax.axis("off")

    def box(x, y, w, h, text, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                                    fc=fc, ec="#444444", lw=1.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=9.5)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrow(x1, y1, x2 - x1, y2 - y1, width=0.25,
                                head_width=1.6, head_length=1.4,
                                length_includes_head=True, fc="#444444",
                                ec="none"))

    BLUE, GREEN, ORANGE, GREY = "#dce9f7", "#e2f2dd", "#fdecd4", "#eeeeee"
    box(2, 24, 16, 8, "raw_data_double_\n（显示裁剪前）", BLUE)
    box(24, 24, 17, 8, "阈值 + 8 邻接 BFS\n连通斑块", BLUE)
    box(47, 24, 17, 8, "按面积排序\n保留前 max_blob_count", BLUE)
    # 四个并行分支
    box(71, 44, 18, 8, "一阶加权重心\n（实际重心）", GREEN)
    box(71, 32, 18, 8, "峰值核心参照\n（理论重心，抗漂移）", ORANGE)
    box(71, 20, 18, 8, "二阶惯性张量 D\n（面积 ≥ 9 cell）", ORANGE)
    box(71, 8, 18, 8, "饱和占比\n（0.98 × ceiling）", GREY)
    box(95, 26, 17, 8, "EMA 平滑\n（仅一阶重心点，\nα = 1 / smooth_frames）", GREY)
    box(2, 6, 14, 8, "DrawBalanceOverlay\n箭头 / 双头箭头 / 提示", "#f7d9dc")

    arrow(18, 28, 24, 28)
    arrow(41, 28, 47, 28)
    arrow(64, 28, 71, 48)   # 上分支
    arrow(64, 28, 71, 36)
    arrow(64, 28, 71, 24)
    arrow(64, 28, 71, 12)   # 下分支
    arrow(89, 48, 102, 34)
    arrow(89, 36, 101, 32)
    arrow(89, 24, 101, 30)
    arrow(89, 12, 102, 27)
    # 平滑盒 → 绘制盒：走底部空白绕行，避开所有盒子    ax.plot([103.5, 103.5, 9, 9], [26, 2, 2, 6], color="#444444", lw=1.6)
    arrow(9, 2, 9, 5.6)
    ax.text(56, 3.2, "平滑后的重心 / 偏差 / 二阶结论交给 overlay 绘制", fontsize=8.5,
            ha="center", color="#555555")
    fig.savefig("../Fig01_算法数据流.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# Fig02 一阶对称盲区 vs 二阶检出
# ----------------------------------------------------------------------
def fig02():
    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.6))
    # 左：2x2 反例（概念演示，实际 <9 cell 跳过二阶）
    ax = axes[0]
    m2 = np.array([[6.0, 4.0], [4.0, 6.0]])
    ax.imshow(m2, cmap="Blues", vmin=0, vmax=8)
    for r in range(2):
        for c in range(2):
            ax.text(c, r, f"{m2[r, c]:.0f}", ha="center", va="center",
                    fontsize=14, color="#222222")
    mu, geo = first_order(m2)
    ax.plot(mu[1], mu[0], "o", ms=14, mfc="none", mec="red", mew=2.5)
    ax.plot(geo[1], geo[0], "x", ms=14, mec="white", mew=3)
    ax.set_title("(a) 2×2 反例：重心重合，箭头 = 0\n红圈=实际重心，白叉=几何中心", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    # 右：3x3 对角失衡（面积 9 = 最小可分析斑块）
    ax = axes[1]
    m3 = np.full((3, 3), 4.0)   # 背景有基础压力，保证 9 cell 全进斑块
    for i in range(3):
        m3[i, i] = 10.0
    m3[1, 1] = 7.0
    ax.imshow(m3, cmap="Blues", vmin=0, vmax=10)
    for r in range(3):
        for c in range(3):
            ax.text(c, r, f"{m3[r, c]:.0f}", ha="center", va="center",
                    fontsize=13, color="#222222")
    mu, geo = first_order(m3)
    ax.plot(mu[1], mu[0], "o", ms=15, mfc="none", mec="red", mew=2.5)
    ax.plot(geo[1], geo[0], "x", ms=15, mec="white", mew=3)
    cells = list(np.argwhere(m3 > 0))
    vals = [m3[tuple(p)] for p in cells]
    so = second_order(cells, vals)
    ax.set_title(f"(b) 3×3 压歪：重心仍重合，二阶检出\nλ = {so['lam']:.3f}（阈值 0.05），"
                 f"主失衡轴沿对角线", fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    # 第三格：3x3 均匀真平衡 —— 与 (b) 箭头同为 0，一阶无法区分
    ax = axes[2]
    mu3 = np.full((3, 3), 5.0)
    ax.imshow(mu3, cmap="Blues", vmin=0, vmax=10)
    for r in range(3):
        for c in range(3):
            ax.text(c, r, f"{mu3[r, c]:.0f}", ha="center", va="center",
                    fontsize=13, color="#222222")
    mu, geo = first_order(mu3)
    ax.plot(mu[1], mu[0], "o", ms=15, mfc="none", mec="red", mew=2.5)
    ax.plot(geo[1], geo[0], "x", ms=15, mec="white", mew=3)
    so_u = second_order(list(np.argwhere(mu3 > 0)),
                        [mu3[tuple(p)] for p in np.argwhere(mu3 > 0)])
    ax.set_title(f"(c) 3×3 真平衡：均匀分布\n箭头同样 = 0，但 λ = {so_u['lam']:.3f} ≈ 0",
                 fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig("../Fig02_一阶对称盲区与二阶检出.png", dpi=160)
    plt.close(fig)
    print("3x3 例:", {k: (round(v, 4) if isinstance(v, float) else v)
                      for k, v in so.items()})
    return so


# ----------------------------------------------------------------------
# Fig03 偏差张量分解：iso 与 dev
# ----------------------------------------------------------------------
def fig03():
    n = 7
    def uniform():
        return np.full((n, n), 6.0)
    def center_heavy():
        m = np.full((n, n), 3.0)
        m[2:5, 2:5] = 9.0
        return m
    def ring():
        m = np.full((n, n), 8.0)
        m[2:5, 2:5] = 2.0
        m[3, 3] = 2.0
        return m
    def diagonal():
        m = np.full((n, n), 3.0)
        for i in range(n):
            m[i, i] += 6.0
        return m

    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
    for ax, (m, name) in zip(axes, [
            (uniform(), "理想均匀\niso ≈ 0，λ ≈ 0"),
            (center_heavy(), "中心集中\niso < 0（力向重心收缩）"),
            (ring(), "环状接触\niso > 0（力向边缘发散）"),
            (diagonal(), "对角偏斜\niso ≈ 0，λ 大（主失衡轴）")]):
        cells = list(np.argwhere(m > 0))
        vals = [m[tuple(p)] for p in cells]
        so = second_order(cells, vals)
        ax.imshow(m, cmap="YlOrRd", vmin=0, vmax=10)
        ax.set_xticks([]); ax.set_yticks([])
        title = name.split("\n")[0]
        ax.set_title(title, fontsize=11)
        ax.set_xlabel(f"iso = {so['iso']:+.3f}\nλ = {so['lam']:.3f}",
                      fontsize=9)
        if so["lam"] > 0.05:
            ar, ac = so["axis"]
            cy = np.argwhere(m > 0)[:, 0].mean()
            cx = np.argwhere(m > 0)[:, 1].mean()
            L = 2.6
            ax.plot([cx - ac * L, cx + ac * L], [cy - ar * L, cy + ar * L],
                    color="#7a00cc", lw=1.5, ls="--")
        print(name.replace("\n", " "), "-> iso=%.4f lam=%.4f" % (so["iso"], so["lam"]))
    fig.suptitle("偏差张量 D 的两个独立成分：各向同性 iso（收缩/发散）与无迹偏斜 λ（方向性失衡）", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("../Fig03_偏差张量分解.png", dpi=160)
    plt.close(fig)


# ----------------------------------------------------------------------
# 公共小工具：峰值核心参照（与 C++ L185 同义：f<=0 时全 cell 进核心集）
# ----------------------------------------------------------------------
def peak_core_center(mat, frac=0.5):
    pos = np.argwhere(mat > 0)
    vals = mat[mat > 0]
    thr = frac * vals.max()
    core = pos[vals >= thr] if frac > 0 else pos
    if len(core) == 0:
        core = pos
    return core.mean(0), core


# ----------------------------------------------------------------------
# Fig04 UI 呈现语义图：一次 overlay 里所有视觉元素的含义
# ----------------------------------------------------------------------
def fig04():
    n = 9
    rng = np.random.default_rng(7)
    # 构造一个"既压偏又对角失衡"的斑块：对角加重 + 整体左上偏
    m = np.zeros((n, n))
    m[1:8, 1:8] = 4.0 + rng.normal(0, 0.4, (7, 7))
    for i in range(1, 8):
        m[i, i] += 5.0           # 主对角加重 → twist
    m[1:4, 1:4] += 2.5           # 左上再加重 → 实际重心向左上偏
    m = np.maximum(m, 0.3)

    cells = list(np.argwhere(m > 0))
    vals = [m[tuple(p)] for p in cells]
    so = second_order(cells, vals)
    mu, _ = first_order(m)
    core_mu, _ = peak_core_center(m)

    mean_v, sd_v = float(np.mean(vals)), float(np.std(vals))

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    ax.imshow(m, cmap="Greys", vmin=0, vmax=m.max())
    ax.set_xticks([]); ax.set_yticks([])

    # 红/蓝半透明 cell：偏离均值 ±0.7σ
    for (r, c), v in zip(cells, vals):
        if v > mean_v + 0.7 * sd_v:
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fc="red",
                                   alpha=0.30, ec="none"))
        elif v < mean_v - 0.7 * sd_v:
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fc="blue",
                                   alpha=0.30, ec="none"))
    # 斑块红框
    ax.add_patch(Rectangle((0.5, 0.5), 7, 7, fill=False, ec="red", lw=2.2))
    # 白十字"目标" = 峰值核心参照中心
    ax.plot(core_mu[1], core_mu[0], "+", ms=17, mec="white",
            markeredgewidth=3, zorder=6)
    # 橙点"当前" = 加权重心 + 箭头
    ax.plot(mu[1], mu[0], "o", ms=11, mfc="darkorange", mec="white",
            mew=1.5, zorder=6)
    ar, ac = so["axis"]
    ax.add_patch(FancyArrow(mu[1], mu[0], core_mu[1] - mu[1],
                            core_mu[0] - mu[0], width=0.07,
                            head_width=0.42, head_length=0.36,
                            length_includes_head=True, fc="darkorange",
                            ec="none", zorder=7))
    # 紫色主失衡轴（虚线）+ 偏重侧铺底
    cy, cx = np.asarray(cells)[:, 0].mean(), np.asarray(cells)[:, 1].mean()
    L = 3.4
    ax.plot([cx - ac * L, cx + ac * L], [cy - ar * L, cy + ar * L],
            color="#7a00cc", lw=1.8, ls="--", zorder=5)
    proj = [(p[0] - cy) * ar + (p[1] - cx) * ac for p in cells]
    for (r, c), pr in zip(cells, proj):
        if pr < 0:  # 主轴负侧 = 本例偏重侧
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, fc="#7a00cc",
                                   alpha=0.14, ec="none"))

    # 编号标记（画在网格空白处，不与数据元素重叠）+ 右侧图例表
    def badge(x, y, k):
        ax.add_patch(plt.Circle((x, y), 0.38, fc="white", ec="#333",
                                lw=1.2, zorder=8))
        ax.text(x, y, str(k), ha="center", va="center", fontsize=10,
                zorder=9, color="#333")

    badge(8.1, 1.0, 1)   # 红框
    badge(8.1, 2.2, 2)   # 红/蓝 cell
    badge(core_mu[1] + 0.9, core_mu[0] - 0.9, 3)   # 白十字
    badge(mu[1] + 0.9, mu[0] + 0.9, 4)             # 橙点+箭头
    badge(cx + ac * L * 0.8 + 0.7, cy + ar * L * 0.8 + 0.7, 5)  # 紫轴/铺底
    badge(4.5, 8.3, 6)   # 饱和提示（顶部）
    ax.text(4.5, 7.55, "（顶部提示条见右图例 ⑥）", fontsize=8.5,
            ha="center", va="center", color="#a33")

    legend_lines = [
        "① 红框：一个独立接触斑块（8 邻接连通域）",
        "② 红 cell：压力明显偏大（> 均值 + 0.7σ）；蓝 cell：偏小（< −0.7σ）",
        "③ 白十字“目标”：力应集中的位置（峰值核心参照中心）",
        "④ 橙点“当前”+ 箭头：力实际集中位置；向箭头方向调整施力",
        "    （偏差 x mm/cell）；落入合格圈则箭头变绿显示“已平衡”",
        "⑤ 紫虚线 = 主失衡轴，铺底一侧 = 偏重侧；“左上侧压力偏大，",
        "    压头可能倾斜”（twist：手推修不好，检查压头平面度）",
        "⑥ “力值接近上限，读数可能不准”（饱和 cell 占比 > 30%）",
    ]
    fig.text(0.685, 0.86, "视觉元素图例", fontsize=11.5, ha="left",
             weight="bold")
    for i, line in enumerate(legend_lines):
        fig.text(0.685, 0.80 - i * 0.062, line, fontsize=9.5, ha="left",
                 va="top", color="#333")
    ax.set_title("受力平衡 overlay 视觉语言一览（同一斑块的完整呈现）",
                 fontsize=12)
    ax.set_xlim(-0.8, 9.3)
    ax.set_ylim(8.9, -0.9)
    fig.subplots_adjust(left=0.03, right=0.66, top=0.92, bottom=0.04)
    fig.savefig("../Fig06_UI呈现语义.png", dpi=160)
    plt.close(fig)
    print("Fig06 例(UI呈现): mu=(%.3f,%.3f) core=(%.3f,%.3f) lam=%.3f iso=%+.3f"
          % (mu[0], mu[1], core_mu[0], core_mu[1], so["lam"], so["iso"]))


# ----------------------------------------------------------------------
# Fig05 峰值核心参照抗漂移：参照中心随压力的漂移对照
# ----------------------------------------------------------------------
def fig05():
    # 基础场：右下高斯峰 + 向左上衰减的裙边 → 加力时斑块向左上扩张
    n = 15
    r, c = np.mgrid[0:n, 0:n]
    base = 8.0 * np.exp(-(((r - 9) ** 2) + (c - 9) ** 2) / 22.0) + 0.05
    enter = 5.0   # enter_threshold

    ks = np.linspace(1.0, 4.0, 31)
    geo_drift, core_drift = [], []
    core_ref = None
    for k in ks:
        m = base * k
        m = np.where(m > enter, m, 0.0)   # 越过进入阈值才进斑块
        pos = np.argwhere(m > 0)
        geo = pos.mean(0)
        core_mu, _ = peak_core_center(m)
        if core_ref is None:
            core_ref = core_mu
        geo_drift.append(np.hypot(*(geo - geo_drift_geo0(ks, base, enter))))
        core_drift.append(np.hypot(*(core_mu - core_ref)))
    geo_drift = np.array(geo_drift)
    core_drift = np.array(core_drift)

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.1),
                             gridspec_kw={"width_ratios": [1.15, 1, 1]})
    # (a) 漂移曲线
    ax = axes[0]
    ax.plot(ks, geo_drift, "o-", ms=3.5, color="#c33", lw=1.8,
            label="全斑块几何中心（首版参照）")
    ax.plot(ks, core_drift, "s-", ms=3.5, color="#2a7de1", lw=1.8,
            label="峰值核心参照（v2.2.2）")
    ax.set_xlabel("整体压力放大倍数 k")
    ax.set_ylabel("参照中心移动距离（cell）")
    ax.set_title("(a) 参照中心随压力的漂移", fontsize=10.5)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(alpha=0.3)
    # (b)(c) 小/大压力下的斑块与核心集
    for ax, k, tag in [(axes[1], 1.0, "(b) k = 1（轻压）"),
                       (axes[2], 4.0, "(c) k = 4（重压）")]:
        m = np.where(base * k > enter, base * k, 0.0)
        ax.imshow(m, cmap="Blues", vmin=0, vmax=base.max() * 4)
        _, core = peak_core_center(m)
        for p in core:
            ax.add_patch(Rectangle((p[1] - 0.5, p[0] - 0.5), 1, 1,
                                   fill=False, ec="#2a7de1", lw=1.6))
        mu, geo = first_order(m)
        ax.plot(geo[1], geo[0], "x", ms=12, mec="red", mew=2.4)
        cmu, _ = peak_core_center(m)
        ax.plot(cmu[1], cmu[0], "s", ms=9, mfc="none", mec="#2a7de1", mew=2.2)
        area = int((m > 0).sum())
        ax.set_title(f"{tag}  面积 {area} cell\n红叉=全斑块中心，蓝框=核心集/蓝方块=核心中心", fontsize=9.5)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("加力 → 边缘低值 cell 不断越过阈值加入斑块：全斑块几何中心被“拖”着走，峰值核心参照不动", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("../Fig05_峰值核心抗漂移.png", dpi=160)
    plt.close(fig)
    print("Fig05: 几何中心最大漂移 %.3f cell, 峰值核心最大漂移 %.3f cell"
          % (geo_drift.max(), core_drift.max()))


def geo_drift_geo0(ks, base, enter):
    """首版全斑块几何中心在 k=1 时的位置（供漂移距离计算）。"""
    m = np.where(base * ks[0] > enter, base * ks[0], 0.0)
    return np.argwhere(m > 0).mean(0)


# ----------------------------------------------------------------------
# Fig06 箭头可信性（最速下降）与 EMA 平滑
# ----------------------------------------------------------------------
def fig06():
    n = 9
    m = np.zeros((n, n))
    m[1:8, 1:8] = 4.0
    m[2:5, 2:5] += 3.0       # 力集中在左上 → 实际重心偏左上
    cells = list(np.argwhere(m > 0))
    vals = [m[tuple(p)] for p in cells]
    mu, _ = first_order(m)
    core_mu, _ = peak_core_center(m)
    d = core_mu - mu          # 箭头 = 理论 − 实际
    dn = d / np.linalg.norm(d)

    def loss(shift):
        """L = Σ vᵢ·|pᵢ − (理论重心−shift)|²：压头沿 −d 平移 shift 后的目标重心。"""
        tgt = core_mu - dn * shift
        return sum(v * ((p[0] - tgt[0]) ** 2 + (p[1] - tgt[1]) ** 2)
                   for p, v in zip(cells, vals))

    ts = np.linspace(-2.5, 6.0, 60)
    L_arrow = [loss(t) for t in ts]
    perp = np.array([-dn[1], dn[0]])
    L_perp = [sum(v * ((p[0] - (core_mu - perp * t)[0]) ** 2 +
                       (p[1] - (core_mu - perp * t)[1]) ** 2)
              for p, v in zip(cells, vals)) for t in ts]

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))
    # (a) 箭头 = 最速下降方向
    ax = axes[0]
    ax.imshow(m, cmap="YlOrRd", vmin=0, vmax=m.max())
    ax.plot(core_mu[1], core_mu[0], "+", ms=16, mec="white", mew=3, zorder=5)
    ax.plot(mu[1], mu[0], "o", ms=10, mfc="darkorange", mec="white", zorder=5)
    ax.add_patch(FancyArrow(mu[1], mu[0], d[1], d[0], width=0.08,
                            head_width=0.45, head_length=0.4,
                            length_includes_head=True, fc="darkorange",
                            ec="none", zorder=6))
    ax.set_title("(a) 箭头 = 失衡损失 L 对“平移压头”的最速下降方向\n白十字=理论（核心参照），橙点=实际（加权重心）",
                 fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    # (b) L 沿箭头方向 vs 垂直方向
    ax = axes[1]
    ax.plot(ts, L_arrow, "-", color="#2a7de1", lw=2.2, label="沿箭头方向平移压头")
    ax.plot(ts, L_perp, "--", color="#c33", lw=1.8, label="垂直箭头方向平移")
    ax.axvline(0, color="#999", lw=0.8)
    ax.set_xlabel("沿该方向平移量（cell）")
    ax.set_ylabel("失衡损失 L")
    ax.set_title("(b) L 沿箭头方向下降最快（梯度方向的可视化验证）", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("../Fig04_箭头最速下降验证.png", dpi=160)
    plt.close(fig)

    # (c) EMA 平滑
    rng = np.random.default_rng(3)
    frames = 60
    true_c = np.column_stack([np.full(frames, 3.5) + 1.2 * np.sin(np.linspace(0, 3, frames)) * 0,
                               np.full(frames, 3.2)])
    true_c[:, 0] += np.linspace(0, 0.6, frames)     # 缓慢真实移动
    obs = true_c + rng.normal(0, [0.35, 0.35], (frames, 2))
    alpha = 1.0 / 5.0
    ema = np.zeros_like(obs)
    ema[0] = obs[0]
    for i in range(1, frames):
        ema[i] = (1 - alpha) * ema[i - 1] + alpha * obs[i]
    # 第 40 帧 blob 数变化 → 缓冲清空 → 跳变
    ema[40:] = 0
    ema[40] = obs[40]
    for i in range(41, frames):
        ema[i] = (1 - alpha) * ema[i - 1] + alpha * obs[i]

    fig, ax = plt.subplots(figsize=(9.0, 3.9))
    ax.plot(obs[:, 1], obs[:, 0], "x", ms=5, color="#bbb", label="原始重心（逐帧抖动）")
    ax.plot(ema[:, 1], ema[:, 0], "-", color="#2a7de1", lw=2.2,
            label="EMA 平滑后（α = 1/5）")
    ax.axvline(obs[40, 1], color="#c33", lw=1.0, ls=":")
    ax.annotate("blob 数变化 → 平滑缓冲清空\n（此处一次跳变，属已知代价）",
                xy=(obs[40, 1], ema[40, 0]), xytext=(obs[40, 1] - 2.6, 3.5),
                fontsize=9, arrowprops=dict(arrowstyle="->", color="#c33"))
    ax.set_xlabel("列（c）"); ax.set_ylabel("行（r）")
    ax.set_title("EMA 只平滑两个重心点：抖动被压掉，代价是数帧滞后与 blob 数变化时的一次跳变", fontsize=11)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("../Fig07_EMA平滑.png", dpi=160)
    plt.close(fig)
    rms_raw = float(np.sqrt(((obs - true_c) ** 2).sum(1).mean()))
    rms_ema = float(np.sqrt(((ema - true_c) ** 2).sum(1).mean()))
    print("Fig04: L 沿箭头方向最小点 shift=%.2f cell; Fig07: EMA 后重心 RMS 误差 %.3f → %.3f cell"
          % (ts[int(np.argmin(L_arrow))], rms_raw, rms_ema))


if __name__ == "__main__":
    # 2x2 原始交叉矩验证（文档 §2.3 引用值 μrc = +0.05）
    m2 = np.array([[6.0, 4.0], [4.0, 6.0]])
    cells = list(np.argwhere(m2 > 0))
    so2 = second_order(cells, [m2[tuple(p)] for p in cells])  # n<9 → None
    w = m2.flatten(); pos = np.argwhere(m2 > 0).astype(float)
    mu = (pos * w[:, None]).sum(0) / w.sum()
    m_rc = np.sum(w * (pos[:, 0] - mu[0]) * (pos[:, 1] - mu[1])) / w.sum()
    print("2x2: 实际重心 =", mu, "加权交叉矩 μrc =", round(m_rc, 4),
          "(二阶分析 n<9 跳过:", so2, ")")
    fig01()
    fig02()
    fig03()
    fig04()
    fig05()
    fig06()
