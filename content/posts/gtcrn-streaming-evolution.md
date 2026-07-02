---
author: "Konpaku Youran"
title: "GTCRN 轻量化的流式方案的演进思路"
date: "2026-02-13"
slug: gtcrn-streaming-evolution
description: "GTCRN-> GTCRN Light ->Causal Streaming GTCRN Light"
tags: ["算法", "机器学习","GTCRN"]
categories: ["音频算法"]
ShowToc: true
TocOpen: true
---

# GTCRN 演进路径

记录 v1 → v2 → v3 → v3.1/v3.2 → v4 → v4.1 的改动和原因。

## 版本概览

| 版本 | 改动点 | 参数量 | 质量指标 | 内存 | 实时 |
|------|--------|--------|----------|------|------|
| v1 baseline | 基线 | 139K | DNSMOS 3.15 | — | × |
| v2 transient | 换损失函数 | 139K | DNSMOS 3.15 | — | × |
| v3 causal | 因果化改造 | 145K | DNSMOS 2.98 | — | √ |
| v3.1 precision | KD + QAT 压缩 | 41.6K | PESQ 2.041 | 228 KB (INT8) | √ |
| v3.2 transient | 宽度1.5× + 瞬态损失 | ~83K | PESQ ~2.15 | ~355 KB (INT8) | √ |
| v4 network opt | 架构精简 (4层GTConv) | ~87K | PESQ 2.147 | 683 KB (FP32) | √ |
| v4.1 int8 | INT8 混合精度 C 推理 | ~87K | PESQ 2.037 | 464 KB | √ |

## 网络结构 (v1/v2 共用)

```
输入 spec (B, 513, T, 2)
    │
    ├─ 可学习频带权重 (513,)
    │
    ▼
ERB_48k.bm(): 513 → 219
    │   低频171保留，高频342→48 ERB band
    │
    ▼
SFE_Lite: DWConv(1×5) → PWConv → BN
    │
    ▼
┌─ Encoder ─────────────────────────────┐
│  DSConv: 219→110 (stride=2)   ← skip1 │
│  DSConv: 110→55  (stride=2)   ← skip2 │
│  GTConvLite×6 (d=1,2,4,8,4,2) ← skip3-8
│  SubbandAttention                     │
└───────────────────────────────────────┘
    │
    ▼
DPGRNN_Enhanced × 2
    │  intra: 双向GRU (频率轴)
    │  inter: 单向GRU (时间轴)
    │
    ▼
┌─ Decoder ─────────────────────────────┐
│  GTConvLite×6 + skip (逆序)           │
│  DSDeconv: 55→110 + skip2             │
│  DSDeconv: 110→219 + skip1            │
└───────────────────────────────────────┘
    │
    ▼
ERB_48k.bs(): 219 → 513
    │
    ▼
CRM掩码 → 输出
```

### GTConvLite 内部

```
x → DWConv(3×3, dilation) → PWConv → BN → PReLU
  → TRALite (时序注意力)
  → SEBlock (通道注意力)
  → + x (残差)
```

### DPGRNN 内部

```
x (B,C,T,F)
  → reshape (B*T, F, C)
  → Linear → 双向GRU (频率轴) → Linear
  → reshape + LayerNorm
  → reshape (B*F, T, C)
  → Linear → 单向GRU (时间轴) → Linear
  → reshape + LayerNorm
  → 输出
```

---

## v1 → v2: 换损失函数

### 问题

v1 用的是标准 SpecRIMAGLoss，对所有帧一视同仁。但实际听感上，键盘敲击、鼠标点击这类突发噪音处理得不好。DNSMOS 是整段平均，掩盖了这个问题。

### 方案

不改网络，只改损失函数。加了瞬态检测：

```python
# 检测能量突变
energy_diff = |energy[t] - energy[t-1]|
transient = energy_diff > threshold * mean_energy

# 瞬态帧损失放大5倍
loss = Σ weight[t] * frame_loss[t]
weight[t] = 5.0 if transient[t] else 1.0
```

### 结果

- DNSMOS 基本持平 (3.1474 → 3.147)
- 瞬态噪音主观听感明显改善
- 训练时间变长 (29 → 71 epochs)

### 为什么不改网络

能用损失函数解决的问题就不动架构。改架构的代价：
- 要重新验证各模块交互
- 可能引入新bug
- 推理时有额外开销

改损失函数只影响训练，推理零开销。

---

## v2 → v3: 因果化

### 问题

v1/v2 是离线模型，要看完整段音频才能处理。没法用在实时场景（通话、直播）。

延迟分析：
- 非因果模型需要看"未来"帧
- 感受野决定最小延迟，v2大概要200-500ms
- 实时通话要求<50ms

### 方案

把所有"偷看未来"的操作改掉：

| 模块 | v2 (非因果) | v3 (因果) |
|------|-------------|-----------|
| GTConvLite | padding=(d,1) 对称 | pad_t=(k-1)*d 左边 |
| TRALite | Conv1d padding=2 | F.pad(x,(4,0)) |
| DPGRNN inter | 双向GRU | 单向GRU |

频率轴的操作不用改，因为频率轴不涉及时间因果。

### v3 网络结构

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
┌─ CausalEncoder ───────────────────────┐
│  DSConv: 219→110              ← skip1 │
│  DSConv: 110→55               ← skip2 │
│  CausalGTConvLite×6           ← skip3-8
│  SubbandAttention                     │
└───────────────────────────────────────┘
    │
    ▼
CausalDPGRNN × 2
    │  intra: 双向GRU (频率轴) ← 不用改
    │  inter: 单向GRU (时间轴) ← 改成单向
    │
    ▼
┌─ CausalDecoder ───────────────────────┐
│  CausalGTConvLite×6 + skip            │
│  Fuse + DSDeconv: 55→110              │
│  DSDeconv: 110→219 + skip1            │
└───────────────────────────────────────┘
    │
    ▼
out_conv → ERB_48k.bs() → CRM → 输出
```

### 因果模块对比

**GTConvLite → CausalGTConvLite**
```
离线: padding=(dilation, 1)，前后各看dilation帧
因果: F.pad(x, (0,0,pad_t,0))，只看过去pad_t帧
      pad_t = (kernel-1) * dilation
```

**TRALite → CausalTRA**
```
离线: Conv1d(k=5, padding=2)，前后各看2帧
因果: Conv1d(k=5, padding=0) + F.pad(x,(4,0))，只看过去4帧
```

**DPGRNN → CausalDPGRNN**
```
离线: inter用双向GRU，能看整个时间序列
因果: inter改单向GRU，只能看到当前和过去
```

### 其他改动

- 激活函数: PReLU → SiLU
- DSConv: 加了中间BN，顺序调整
- 参数量: 139K → 145K (+4%)

参数量增加是因为单向GRU要增大hidden_size才能保持建模能力。

### 结果

- DNSMOS: 3.15 → 2.98 (-5%)
- 延迟: 10ms (单帧)
- RTF: 0.21 (还有4.7倍余量)

掉了0.17分是预期内的。因果模型看不到未来，信息量必然少于非因果模型。

### 流式状态

实时推理要维护帧间状态：
- GTConv缓存: 12层，不同dilation长度不同
- TRA历史: 12层，每层4帧
- GRU hidden: 2×DPGRNN × 2层
- Skip缓存: 8组

---

## v3 → v3.1: 精度剪枝 (KD + QAT)

### 问题

v3 teacher 模型 (width_mult=2.0, 145K 参数) 运行时占用 711 KB，无法部署到 500 KB 内存限制的嵌入式设备。

### 方案

两步压缩：知识蒸馏 (KD) 缩小模型 → 量化感知训练 (QAT) 压缩权重。

**Step 1: 知识蒸馏**
- Teacher: v3 (width_mult=2.0, CH=32)
- Student: width_mult=1.0 (CH=16, 41.6K 参数)
- 训练 30 epochs 后收敛到容量极限

**Step 2: QAT INT8 量化**
- Conv2d / Linear → INT8 per-channel 对称量化
- GRU / BN / LN → 保持 FP32
- 导出 INT8 权重 + per-channel scale

### 结果

| 指标 | 值 |
|------|-----|
| PESQ | 2.041 |
| SI-SNR | 14.22 dB |
| DNS OVR | 2.778 |
| FP32 内存 | 888 KB |
| INT8 内存 | **228 KB** ✅ |

### 发现的问题

inter GRU 的 `weight_hh` 在长序列 (>1000 帧) 上累积量化误差，导致噪底漂移。解决方案：inter GRU 权重保持 FP32。

---

## v3.1 → v3.2: 宽度扩展 + 瞬态感知

### 问题

v3.1 (width_mult=1.0, CH=16) 容量有限，对键盘敲击、鼠标点击等瞬态噪音抑制不足。

### 方案

| 改动 | v3.1 | v3.2 |
|------|------|------|
| 宽度 | width_mult=1.0 (CH=16) | width_mult=1.5 (CH=24) |
| 参数量 | 41.6K | ~83K |
| 瞬态权重 | transient_weight=1.0 (无效) | transient_weight=8.0 |
| 瞬态检测 | 无 | 频谱平坦度 (flatness_threshold=0.3) |
| KD 瞬态 | 均匀权重 | 瞬态帧 ×5 |

**关键改进**: 引入 `TransientAwareLoss_v2`，通过频谱平坦度区分噪声瞬态和语音瞬态，避免误伤语音起始段。

### 结果

| 指标 | v3.1 | v3.2 |
|------|------|------|
| PESQ | 2.041 | ~2.15-2.25 |
| INT8 内存 | 228 KB | ~355 KB |
| 瞬态抑制 | 弱 | 明显改善 |

内存从 228 KB 增到 355 KB，仍在 500 KB 限制内。

---

## v3 → v4: 架构精简

### 问题

v3 使用 6 层 GTConv (dilation=[1,2,4,8,4,2])，encoder + decoder 共 12 层。dilation=8 的层感受野过大，对实时场景贡献有限，但占用大量因果缓存。

### 方案

精简架构，减少层数和通道数：

| 参数 | v3 | v4 |
|------|-----|-----|
| GTConv 层数 | 6 (enc) + 6 (dec) | 4 (enc) + 4 (dec) |
| Dilation 序列 | [1,2,4,8,4,2] | [1,2,4,2] |
| 通道数 CH | 32 | 20 |
| DPGRNN hidden | 32 | 20 |
| SE Block | 选择性启用 | 全部启用 |
| Skip 连接 | 8 组 | 6 组 |

### v4 网络结构

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
┌─ CausalEncoder ───────────────────────┐
│  DSConv: 219→110              ← skip1 │
│  DSConv: 110→55               ← skip2 │
│  CausalGTConv×4 (d=1,2,4,2)  ← skip3-6
│  SubbandAttention                     │
└───────────────────────────────────────┘
    │
    ▼
CausalDPGRNN × 2
    │  intra: 双向GRU (频率轴)
    │  inter: 单向GRU (时间轴)
    │
    ▼
┌─ CausalDecoder ───────────────────────┐
│  CausalGTConv×4 + skip               │
│  Fuse + DSDeconv: 55→110             │
│  DSDeconv: 110→219 + skip1           │
└───────────────────────────────────────┘
    │
    ▼
out_conv → ERB_48k.bs() → CRM → 输出
```

### 训练

- KD: v3 teacher (CH=32, 6层) → v4 student (CH=20, 4层)
- QAT: Scheme 1b 混合精度 (22层FP32 + 45层INT8)

### 结果

| 指标 | v3 | v4 |
|------|-----|-----|
| PESQ (KD) | — | 2.147 |
| PESQ (QAT) | — | 2.037 |
| 参数量 | 145K | ~87K |
| FP32 内存 | — | 683 KB |

### 内存分解 (FP32)

| 类别 | 大小 | 占比 |
|------|------|------|
| Core (权重) | 348.82 KB | 51.1% |
| — ERB 滤波器 | 128.25 KB | 36.8% of Core |
| — DPGRNN ×2 | 150.02 KB | 43.0% of Core |
| — GTConv ×8 | 55.81 KB | 16.0% of Core |
| State (状态) | 216.46 KB | 31.7% |
| Workspace | 97.20 KB | 14.2% |
| STFT + Handle | 20.17 KB | 2.9% |
| **总计** | **682.64 KB** | |

主要瓶颈: ERB 滤波器 (128 KB) 和 GRU 权重 (137 KB) 无法量化，占 Core 的 80%。

---

## v4 → v4.1: INT8 混合精度 C 推理

### 问题

v4 的 C 推理管线所有权重以 FP32 存储。需要将 QAT 训练结果迁移到 C 端，实现 INT8 混合精度推理。

### 方案

**量化策略 (Scheme 1b)**:
- FP32 保留 (22层): in_conv, down1.pw, subband_attn, 所有 TRA, up1/up2.dw, GRU, LayerNorm, alpha/beta
- INT8 量化 (45层): GTConv dw/pw, SE fc1/fc2, DSConv/DSDeconv, DPGRNN pre/post/post2, fuse, out_conv
- 量化方式: 对称 per-channel, `q = round(clamp(w / scale, -127, 127))`

**BN 折叠**: 24 个 BatchNorm 层在导出时折叠进 Conv 权重:
```
W_folded = W * (gamma / sqrt(var + eps))
b_folded = beta - mean * gamma / sqrt(var + eps)
```

**实施阶段**:
1. Python 导出脚本 (`export_qat_weights.py`) — 提取 QAT 权重，BN 折叠，量化导出
2. C 端权重结构体修改 — `int8_t weight[]` + `float scale[]` + `float bias[]`
3. C 端层计算修改 — INT8 反量化计算，移除 BN 计算
4. 权重加载 (GTC5 格式)、流式推理管线更新、Demo 更新

### 发现并修复的 Bug

1. **`export_fp32_weights.py` 缺少 `out_conv` bias**: bias `[0.5724, 0.0033]` 未导出，导致 C 端 mask 偏移严重
2. **复数 mask 乘法错误**: 修正为标准复数乘法 `out = spec * mask` (实部虚部交叉相乘)

### 窗函数问题

模型训练使用 `sqrt(hann)` + `center=True`，但 C 流式处理无法做 center padding。
- `sqrt(hann)`: 第 961 帧 (~20秒) 产生 NaN 溢出
- 普通 `hann`: 全程 30 秒稳定，无 NaN

C 端当前使用普通 hann 窗。

### 结果

| 指标 | 值 |
|------|-----|
| INT8 vs FP32 缓存 SNR | 19.87 dB |
| INT8 vs FP32 相关系数 | 0.995 |
| RTF | 0.032 |
| 总内存 | **464 KB** |
| NaN / Clipping | 无 |

> C 流式 vs Python 批处理相关系数仅 0.37，这是预期内的：Python 使用双向时间上下文 (非因果 DPGRNN + 非因果 GTConv)，C 端是单向因果推理。提升一致性需要在训练时加入 causal 约束。

---

## 演进路线图

```
v1 (离线基线, DNSMOS 3.15)
 │
 ▼ 换损失函数
v2 (瞬态感知, DNSMOS 3.15)
 │
 ▼ 因果化改造
v3 (因果流式, DNSMOS 2.98, 145K params)
 │
 ├──────────────────────┐
 │                      │
 ▼ KD压缩              ▼ 架构精简
v3.1 (41.6K, 228KB)    v4 (87K, 683KB FP32)
 │                      │
 ▼ 宽度扩展+瞬态       ▼ INT8混合精度
v3.2 (83K, 355KB)      v4.1 (87K, 464KB)
```

---

## 文件结构

```
archived_models/
├── v1_baseline/
│   ├── original_export/
│   │   └── gtrcn_light_v3_48k_enhanced.py
│   └── best_model_epoch29_score3.1474.tar
│
├── v2_transient/
│   ├── config.yaml
│   ├── best_model_epoch71_score3.147.tar
│   └── full_training_run/
│
├── v3_causal_stream/
│   ├── models/
│   │   └── gtcrn_light_v3_48k_causal_v2.py
│   ├── checkpoints/
│   │   └── best_model_epoch35_score2.983.tar
│   └── QAT/  # QAT训练脚本
│
├── v3.1_precision_pruning/
│   ├── PLAN.md
│   ├── RESULTS.md
│   └── runs/  # KD + QAT 训练记录
│
├── v3.2_width1.5_transient/
│   ├── PLAN.md
│   └── runs/  # 宽度1.5 + 瞬态训练记录
│
├── v4_network_opt/
│   ├── Streaming/  # FP32 C流式推理
│   ├── MEMORY_REPORT.md
│   └── runs/  # KD + QAT 训练记录
│
└── v4.1_int8_quantization/
    ├── PLAN.md
    ├── Streaming/  # INT8混合精度 C流式推理
    ├── export_qat_weights.py
    └── tmp/  # 调试输出和对比脚本
```

---

## 选型建议

| 场景 | 推荐 | 原因 |
|------|------|------|
| 离线处理 | v1 | 质量最高 (DNSMOS 3.15) |
| 办公环境 | v2 | 瞬态处理好 |
| 实时通话 (资源充足) | v3 | 低延迟，质量较高 |
| 极限内存 (<256KB) | v3.1 | 228 KB，最小体积 |
| 瞬态噪音 + 嵌入式 | v3.2 | 355 KB，瞬态抑制好 |
| 均衡部署 | v4.1 | 464 KB，架构精简，INT8 推理 |
