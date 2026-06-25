---
author: "Leventure"
title: "GTCRN 演进路径：v4 → v5 → 落地"
date: "2026-06-18"
description: "从 464KB 到 412KB，记录 GTCRN 模型在架构精简、质量优化、极限压缩、嵌入式 C 部署全过程的踩坑与经验"
tags: ["GTCRN", "模型优化", "嵌入式", "C", "DSP", "噪声抑制"]
categories: ["音频算法"]
series: ["GTCRN"]
ShowToc: true
TocOpen: true
---

# GTCRN 演进路径：v4 → v5 → 落地

记录噪声抑制模型从架构精简开始，经历质量优化、极限压缩，到最终在嵌入式 C 端落地的全过程。

---

## 前言

v4.1 把 464 KB 的推理管线交到了 C 端手里。这个数字已经够小——能在大多数嵌入式芯片上跑起来，RTF 不到 0.04。但我们还想要更多。

不是「把模型再做小一点」这么简单。键盘敲击声和风扇底噪的压制效果已经不错了，如果裁剪的过程中把这两个能力丢掉，小就没有意义。换句话说，**压缩是手段，质量是底线**。每次下手之前，先问一句：压完之后，瞬态噪声还能不能盖住？听感会不会变差？

v5 这条线走了四个月。它从 v4.1 的 464 KB 跑到了最终的 412 KB，中间踩了不少坑。这份文档把踩过的坑、走通的路、放弃的岔路都记下来。

时间线：2026-03（v4.1 交付） → 2026-06（v5.6 C 端落地）

---

## 版本总览

| 版本 | 改了什么 | 参数 | 关键指标 | 内存 | 结论 |
|------|---------|------|----------|------|------|
| v4.1 | INT8 混合精度 C 推理 | 87K | PESQ 2.037 | 464 KB | 基线，已交付 |
| v5.1 | 架构定型 (4层, CH=20) | 55.6K | PESQ 2.462 | ~466 KB | 可靠起点 |
| v5.2 | 多模块 all-in | 73.9K | PESQ ~1.20 | ~538 KB | 失败，复盘后放弃 |
| v5.3 | 网络优化，单模块消融 | 61.6K | [5,10) PESQ 1.92 | ~466 KB | n4 被接受 |
| v5.4 | 宽度裁剪 CH→16 | 41.2K | [5,10) PESQ 1.46 | ~400 KB | 失败，暂停 |
| v5.5 | 极限压缩 (INT4/INT8) | — | PESQ drop < 0.05 | ~314-349 KB (投) | 过门，主线收敛 |
| v5.6 | C 端落地：GTC6/INT4/hidden INT8 | 60.3K | DNSMOS SIG +0.86 | 412 KB | **交付** |

---

## 网络结构 (v5.3-n4 最终)

```
输入 spec (B, 513, T, 2)
    │
    ▼
ERB_48k.bm(): 513 → 219
    │
    ▼
in_conv: Conv2d(2→3)
    │
    ▼
┌─ CausalEncoder ───────────────────────────┐
│  DSConv: 219→110                  ← skip1 │
│  DSConv: 110→55                   ← skip2 │
│  CausalGTConv×4 (d=1,2,4,2)      ← skip3-6│
│  SubbandAttention                         │
└───────────────────────────────────────────┘
    │
    ▼
CausalDPGRNN × 2
    │  intra: 双向GRU (频率轴)
    │  inter: 单向GRU (时间轴)
    │
    ▼
┌─ CausalDecoder ───────────────────────────┐
│  SkipResidualFusion + CausalGTConv×4      │
│  Fuse + DSDeconv: 55→110                  │
│  SkipResidualFusion + DSDeconv: 110→219   │
└───────────────────────────────────────────┘
    │
    ▼
out_conv → ERB_48k.bs() → CRM → 输出
```

相比 v4，decoder 的 skip 连接从简单的 `x + skip` 换成了带门控和残差分支的融合模块。

### SkipResidualFusion

```
x, skip → concat → Conv1×1 → SiLU → Conv1×1 → Tanh → δ
                old = x + skip
                out = old + δ_scale × δ
```

门控参数 `δ_scale` 由训练学习，初始化为零。意思是：模块刚加载时完全等价于 `x + skip`，模型自主决定要加多少「修正项」。

---

## v4.1 → v5.1：架构定型（Stage 1）

### 问题

v4.1 是 v4 的 INT8 导出版。它的架构参数是四个月前确定的：CH=20，4 层 GTConv，dilation = [1,2,4,2]。训练脚本、checkpoint、导出流水线全部基于 v4。

到了要开始 v5 的时候，第一件事是：**现在的架构到底行不行？能不能作为后面所有实验的起点？**

### 方案

没有重新训练。v4 的 KD checkpoint 还在本地，直接用。验证了两件事：

1. v4 架构和 v5.1 架构完全一致（CH=20, 4层, dilation=[1,2,4,2]）
2. state_dict 加载 0 missing, 0 unexpected，前向输出差异 = 0.0

### 结果

在旧 5 片段测试集上：

| 指标 | v5.1 (v4 KD) | v4.1 QAT INT8 | v3 Teacher |
|------|:------:|:------:|:------:|
| PESQ | **2.462** | 2.305 | 2.667 |
| SI-SNRi | +5.3 dB | +3.4 dB | +5.9 dB |
| DNS OVR | 2.363 | 2.444 | 2.412 |

PESQ 2.462——保留了 v3 教师模型的 92.3% 质量，参数量从 145K 砍到 55.6K。比 v3.2 (CH=24) 更好，参数量少了 30%。

这个基线够稳。后面所有实验都从这里出发。

---

## v5.1 → v5.2 → v5.3：质量优化（Stage 2）

### v5.2：all-in 翻车

**想做什么**

从 PLAN 里挑了三个看着最有用的改进，一起塞进 v5.1：

1. FreqAwareCausalTRA——TRA 加频带分组感知
2. StreamingSubbandAttention——逐帧能量计算
3. GatedSkipFusion——decoder skip 加门控融合

三个模块同时在 checkpoint 热启动时替换掉了 v5.1 的旧结构。

**发生了什么**

热启动就坏了。旧的 TRA 权重和 SubbandAttn 权重无法加载到新结构里，新模块随机初始化。模型一上来就是乱的，KD loss 量级严重不匹配——频谱 MSE 的数值比 task loss 大了 400 倍，KD 把训练信号完全淹没了。

救援训练 10 个 epoch 后，PESQ 仍然趴在 1.2，回不到 v5.1 的 2.46。

**根因**

不是模块本身不可行，是改法不对。三个模块同时上，每个都破坏了热启动的等价性。出了事找不到是谁惹的。

**教训**

网络优化的实验一定只改一个因素。每改一个，Phase 0（加载权重后不做任何训练）就必须接近 baseline。Phase 0 不通过，绝不让它进入下一轮。

### v5.3：单模块消融

**实验矩阵**

从 v5.1 重新出发。每次只改一个因素，每个候选必须先过 Phase 0：

| 实验 | 改动 | Phase 0 要求 | 结果 |
|------|------|-------------|------|
| n0 | 无网络改动，只换评估脚本 | PESQ 接近 2.462 | 通过 |
| n1 | Loss 优化 | 网络不变 | 待评估 |
| n2 | TRA 频带感知残差 | zero/small init, 保留旧 TRA | 待评估 |
| n3 | SubbandAttention delta | 保留旧输出 | 待评估 |
| n4 | Skip residual fusion | `δ_scale` 初始化为 0, 保留 `x+skip` | **通过，被接受** |

n4 的 SkipResidualFusion 通过了：Phase 0 等价于 `x + skip`，训练后模型自主学会在 decoder 端引入 0.1%~0.5% 量级的修正。`[5,10)` PESQ 达到 1.9202。

**为什么只接受了 n4**

时间窗口里只跑完了 n0 和 n4。n1/n2/n3 没有执行，但实验框架留下来了——将来做消融的时候可以直接用。

---

## v5.3 → v5.4：宽度裁剪（Stage 3）

### 想法

v5.3-n4 已经把网络质量提到 CH=20 下的上限。接下来裁通道，CH=20 → CH=16，用知识蒸馏从 n4 teacher 迁移。

### 实际

CH16 首轮失败。`[5,10)` PESQ 从 1.92 跌到 1.46，drop = 0.46。far beyond 允许的 0.10 上限。

| 模型 | Params | 整段 PESQ | [5,10) PESQ | 判定 |
|------|------:|:------:|:------:|------|
| v5.3 n4 teacher | 61,608 | 1.9929 | 1.9202 | teacher |
| v5.4 CH16 best | 41,212 | 1.5767 | 1.4638 | **失败** |

### 分析

CH16 drop 太大了，不是 KD 参数能调回来的。CH20→16 裁掉了 33% 的通道，信息瓶颈比预期紧得多。

### 现状

CH16 不继续。CH18 fallback 留了配置但没跑。这个决定后来被证明是对的——因为 v5.5 发现，真正的内存大头不在通道数，在状态和缓存的精度。那边的压缩空间反而更大、代价更小。

---

## v5.4 → v5.5：极限压缩（Stage 4）

### 思路变了

前面的压缩都是「砍参数量」。v5.5 换了一个方向：**不动网络结构，压内存**。

DPGRNN 的跨帧隐藏状态、GTConv 的历史缓存、GRU 的输入权重——这些都是运行时开销，不改模型本身的结构。

### 实验线

做实验有一个铁规则：**任何会动的状态**（GRU hidden、cache），必须过漂移测试。重复同一段内容，跑上百遍，看输出之间是不是在「漂」——也就是差异随着时间持续放大。

| 杠杆 | 省多少 | 漂移 | PESQ | 判定 |
|------|------:|------|------|------|
| DPGRNN hidden → INT8 | ~4 KB | BOUNDED | +0.0001 | ✅ |
| GTConv cache → INT4 (cache-only) | ~39 KB | n/a | +0.0195 | ✅ |
| intra-GRU `weight_ih` → INT8 | ~42 KB | BOUNDED (16/16) | +0.0000 | ✅ |
| inter-GRU `weight_ih` → INT8 | ~14 KB | **GROWING (5/16)** | — | ❌ |
| GRU `weight_hh` → INT8 | ~42 KB | — | — | ❌ 未启动 |

两条被拒绝的杠杆卡在同一个地方：**跨帧 GRU 路径不能量化**。

intra-GRU 走的是频率轴——同一时刻的不同频带。这个可以安全地 INT8。

inter-GRU 走的是时间轴——不同时刻的同一频带。把输入权重从 FP32 压到 INT8 之后，5/16 个测试样本的重复输出开始失控。差异不是一次性的，是逐帧累积的：第一遍和第二遍差 0.1%，第一百遍差 5%。

GRU 的反馈环把量化误差放大了。inter-GRU 像是一个有反馈的放大器——输入那一点点量化噪声被循环送回来，每次通过 `weight_hh` 和 sigmoid/tanh 非线性，噪声被重新塑形、放大。几十帧之后，状态就跑偏了。

`weight_hh` 更不敢碰。那是 GRU 的核心——状态转移矩阵。inter 的 `weight_ih` 都已经漂了，`weight_hh` 的风险只高不低。

### 收敛点

**v5.5.3-rescued**：hidden INT8 + cache INT4 + intra-GRU `weight_ih` INT8。inter-GRU 和所有 `weight_hh` 保持 FP32。

到这个点上，v5.5 的使命完成了。它锁定了三件事：

1. 哪些能压：hidden, cache, intra-GRU input
2. 哪些不能压：inter-GRU input, 任何 recurrent weight
3. 内存投影像约 314~349 KB

继续往下追 `<300 KB` 的唯一路径是碰 inter/recurrent GRU，但这违背了「长流稳定性优先」的原则。不再追了。

---

## v5.5 → v5.6：C 端落地

### 定义

v5.6 不是新的压缩或训练。它是把 v5.5 求出的三条结论，在 C 代码里一笔一画地兑现。

v5.5 在 Python 里做的是「仿真」——hook 住 cache 和 hidden，假量化后跑前向，看 PESQ 掉没掉。v5.6 要做的，是让这些量化的位宽真正变成结构体里的 `int8_t` 和 `uint8_t`（packed INT4），让 `memory_report` 打出来的数字不再是估算，而是 C 编译器算出来的 `sizeof`。

### 落地清单

| 项 | 文件 | 内容 |
|-----|------|------|
| GTConv cache INT4 | `gtcrn_layers.c` | packed nibble + per-channel/frame scale，当前帧 FP32，历史帧读时反量化 |
| DPGRNN hidden INT8 | `gtcrn_stream.c` | inter hidden 以 INT8 存储 + per-layer/frequency scale，GRU 计算前反量化到 FP32 scratch |
| intra-GRU `weight_ih` INT8 | `gtcrn_layers.c` + `gtcrn_model.c` | 权重以 INT8+per-row scale 存储/加载，GRU step 里反量化后计算 |
| inter-GRU `weight_ih` FP32 | `gtcrn_model.c` | 保持 FP32，不量化 |
| SkipResidualFusion C 实现 | `gtcrn_layers.c` | 逐像素 conv1×1 + SiLU + Tanh + δ_scale |
| GTC6 权重格式 | `gtcrn_model.c` + `export_gtc6_weights.py` | magic `GTC6`，在 GTC5 主体后追加 5 组 skip fusion tensor；兼容旧 GTC5 加载 |

### 权重文件

导出命令：

```
python export_gtc6_weights.py \
    v5_3_n4_skip_fusion_.../best_model_002.tar \
    Streaming/weights/gtcrn_v56_gtc6_n4.bin
```

产物：`Streaming/weights/gtcrn_v56_gtc6_n4.bin`（276.07 KB，GTC6 v1）。

### 内存实测

`memory_report` 的输出不是估算。下面是 C 编译器算出来的真实数字：

```
GRAND TOTAL:  421,728 bytes  (411.84 KB)
  Core (weights):    241,440 bytes  (235.78 KB)
  State:              79,416 bytes  ( 77.55 KB)
  Workspace:          80,216 bytes  ( 78.34 KB)
  STFT:               20,552 bytes  ( 20.07 KB)
```

拆开看几个关键玩家的真实大小：

| 组件 | 存储格式 | 实测 |
|------|---------|------|
| GTConv INT4 cache ×8 | packed nibble + scale | 45.00 KB |
| DPGRNN inter hidden ×2 | INT8 + per-row scale | 5.16 KB |
| SkipResidualFusion ×5 | FP32 权重 | 23.46 KB |
| intra-GRU `weight_ih` INT8 | INT8 + per-row scale | 在 DPGRNN 权重内 |
| ERB filter | INT8 + global scale | 32.07 KB |

### C/Python 一致

如果 C 端实现的算子和 Python reference 差得远，再漂亮的 PESQ 数字也说明不了什么。v5.6 做了一整轮的逐帧频谱对比。

关键的一组数字：

| 配置 | 输出频谱 rel-RMSE | 说明 |
|------|:------:|------|
| FP32 cache debug (全 FP32) | 0.0068 | 算子本身基本对齐 |
| INT4 cache only | 0.0118 | cache 仿真补上后大幅改善 |
| INT4 + hidden INT8 | 0.0220 | hidden 仿真补上 |
| INT4 + intra `weight_ih` INT8 | 0.0106 | intra GRU 基本对齐 |
| 完整 v5.6 | 0.0188 | 最终残差 < 2% |

残差的主要放大点定位到了 decoder GTConv 到 mask formation 这一段。INT4 cache 的逐帧累积误差在 decoder 的几层 GTConv 之间有微小的累加效应。

### 验证结果

在 3 个独立测试片段 + 30 秒主文件 + 120 秒漂移测试上跑了完整评估：

| 验证项 | 结果 | 判定 |
|--------|------|:--:|
| PESQ (3 clips, C 输出) | mean=2.00, max=2.66 | ✅ |
| DNSMOS SIG gain (noisy1) | +0.86 (3.14→4.00) | ✅ |
| 长流漂移 (120s, 30 repeats) | 初始 ~20dB → 稳定 ~17.4dB, BOUNDED | ✅ |
| 瞬态 DNSMOS BAK | ≥3.40 (主要片段) | ✅ |
| RTF | 0.14 (7 倍实时) | ✅ |
| C/Python 频谱一致 | rel-RMSE=0.0188 | ⚠️ 可接受 |
| `memory_report` | 411.84 KB | ✅ |

漂移测试的关键判断是 **BOUNDED vs GROWING**。

在 120 秒、30 次重复的测试中：前几个重复段的 SNR 从 ~20 dB 降到 ~17.4 dB——这正常，因为第一帧从零状态启动，后续帧有了历史缓存。之后 18 个重复段，SNR 纹丝不动——17.36 dB 到 17.48 dB 之间微小震荡，没有持续下降的趋势。

BOUNDED。hidden INT8 的量化没有在 GRU 的反馈环里滚雪球。

---

## 演进路线图

```
v4.1 (INT8 混合精度, 464 KB, PESQ 2.037)
  │ 交付基线
  ▼
v5.1 (架构定型, ~466 KB FP32, PESQ 2.462)
  │ 从 v4 KD checkpoint 直接复用
  │
  ├─ v5.2 (all-in 质量改进) ─────── ❌ PESQ 1.20, 失败复盘
  │
  ▼
v5.3 (单模块消融)
  │
  ├─ n2/n3 ─────────── ⚪ 未跑
  ├─ n4 SkipResidualFusion ─── ✅ 被接受
  ▼
v5.4 (宽度裁剪 CH16) ─────────── ❌ PESQ drop 0.46, 失败暂停
  │
  ▼
v5.5 (极限压缩, 不动结构)
  │
  ├─ hidden INT8 ───── ✅ BOUNDED
  ├─ cache INT4 ────── ✅ 听感过关
  ├─ intra-GRU `weight_ih` INT8 ─ ✅ BOUNDED (16/16)
  ├─ inter-GRU `weight_ih` INT8 ─ ❌ GROWING (5/16)
  └─ GRU `weight_hh` INT8 ────── ❌ 未启动
  │
  │ 主线收敛: v5.5.3-rescued
  ▼
v5.6 (C 端落地)
  │
  ├─ GTC6 权重格式 + loader
  ├─ INT4 cache / INT8 hidden / INT8 intra-GRU IH
  ├─ SkipResidualFusion C 实现
  ├─ memory_report 实测: 411.84 KB
  ├─ C/Python parity: rel-RMSE 0.0188
  └─ 验证通过: PESQ, DNSMOS, drift BOUNDED, RTF 0.14
```

---

## 已拒绝的路径

有些路试了，有些路没试就决定不走了。都记在这里免得后来人再踩。

| 尝试 | 失败原因 | 替代方案 |
|------|---------|---------|
| CH→16 宽度裁剪 | `[5,10)` PESQ drop 0.46，远超 0.10 上限 | 不裁了；缓存压缩省得更多 |
| inter-GRU `weight_ih` INT8 | 5/16 样本漂移 GROWING | 保持 FP32 |
| GRU `weight_hh` INT8 | inter 都已经漂了，recurrent 风险更高 | 不启动 |
| v5.2 多模块 all-in | 热启动等价性破坏，无法归因 | 改为单模块消融 |

---

## 还没完成的

1. **decoder 端量化残差精确定位**。C/Python 频谱 gap 在 2%，主要是在 decoder GTConv → mask 这一段。如果在某个应用里对精度要求极高，可以对 frame 85 做逐层 dump 找残差放大的那一层。

2. **INT4 cache 的 scale 下界保护**。当信号非常弱时，INT4 的 absmax/7 scale 会把很小的值全量化成 0。一个 `1e-4` 量级的 min_scale 就能解决，但还没加到代码里。

3. **唱歌场景优化**。当前模型训练目标是键盘/风扇等办公噪声，对唱歌尾音的衰减保护不足。最快见效的方案是 decoder 加 3 帧 lookahead（30ms）+ SubbandAttention 最小值保护。

---

## 文件索引

```
archived_models/v5_quality_optimization/
├── PLAN.md                          # 主计划 (部分偏旧)
├── V5_2_FAILURE_AND_V5_3_PLAN.md    # v5.2 失败复盘
├── V5_6_C_DEPLOYMENT_REPORT.md      # v5.6 落地报告
├── V5_6_VALIDATION_REPORT.md        # v5.6 验证报告
├── version_plan.md                  # 版本定义
├── s1_arch_opt/                     # v5.1 代码
├── s2_quality/                      # v5.2 代码 (失败)
├── v5_3_network_optimization/       # v5.3-n4 模型 + checkpoint
├── v5_4_width_compression/          # v5.4 CH16 实验 (失败)
├── v5_5_extreme_compression/        # v5.5 PTQ 仿真 + 漂移验证
│   └── v5.5.3/
└── v5_6_c_deployment/               # v5.6 C 端落地
    ├── PLAN.md                      # 落地计划
    ├── export_gtc6_weights.py       # GTC6 导出
    ├── run_v56_python_reference.py  # C/Python parity 工具
    └── Streaming_baseline_v41/      # 转换前 v4.1 快照 (参考)

Streaming/                           # 当前活跃 C 代码 (v5.6)
├── include/gtcrn_types.h            # v5.6 压缩开关
├── src/gtcrn_layers.c               # INT4 cache / SkipFusion / GRU IH INT8
├── src/gtcrn_stream.c               # hidden INT8 / stage dump
├── src/gtcrn_model.c                # GTC6 loader
├── demo/memory_report.c             # 内存报告
├── demo/v56_spec_dump.c             # 频谱 dump 工具
└── weights/gtcrn_v56_gtc6_n4.bin    # GTC6 权重 (276 KB)
```
