
---
author: "Konpaku Youran"
title: "rvc结构简介"
date: "2026-02-14"
description: "rvc "
tags: ["子监督学习", "机器学习","GTCRN"]
categories: ["音频算法"]
ShowToc: true
TocOpen: true
---

# RVC结构简介

## 推理流程

```
输入音频 (16kHz)
    │
    ▼
┌─────────────────┐
│  HuBERT         │  提取内容特征，输出256维(v1)或768维(v2)
└────────┬────────┘
         │
    ▼    ▼
┌─────────────────┐
│  F0 Extractor   │  提取基频，支持RMVPE/CREPE/Harvest/PM
└────────┬────────┘
         │
    ▼    ▼
┌─────────────────┐
│  Index Search   │  可选，用faiss做音色检索，混合特征
└────────┬────────┘
         │
    ▼    ▼
┌─────────────────┐
│  Synthesizer    │  VITS架构，生成目标音色波形
└────────┬────────┘
         │
         ▼
输出音频 (32k/40k/48k)
```

## Synthesizer结构

主类是`SynthesizerTrnMs256NSFsid`（v1）和`SynthesizerTrnMs768NSFsid`（v2），区别只在输入维度。

```
SynthesizerTrnMs*NSFsid
├── enc_p (TextEncoder)
│   ├── emb_phone: Linear(256/768 → hidden)
│   ├── emb_pitch: Embedding(256, hidden)  # pitch量化到256级
│   ├── encoder: Transformer Encoder
│   └── proj: Conv1d → (mean, log_var)
│
├── flow (ResidualCouplingBlock)
│   └── 4层 ResidualCouplingLayer + Flip
│       每层内部是WaveNet结构
│
├── dec (GeneratorNSF)
│   ├── m_source (SourceModuleHnNSF)
│   │   └── SineGen: 根据F0生成正弦激励信号
│   ├── conv_pre
│   ├── ups: 多级上采样 (ConvTranspose1d)
│   ├── resblocks: HiFiGAN残差块
│   └── conv_post
│
└── emb_g: Embedding(spk_num, gin_channels)  # speaker embedding
```

推理时的数据流：
1. `enc_p`: HuBERT特征 + pitch → 编码后的mean/log_var
2. 采样得到z_p，过`flow`（reverse模式）得到z
3. `dec`: z + f0 + speaker_emb → 波形

## F0提取器 (RMVPE)

```
RMVPE
├── mel_extractor: MelSpectrogram (16kHz, 128 mel bins)
└── model: E2E
    ├── unet: DeepUnet
    │   ├── encoder: 5层下采样
    │   ├── intermediate: 4层中间处理
    │   └── decoder: 5层上采样 (带skip connection)
    ├── cnn: Conv2d(16→3)
    └── fc: BiGRU(384→256) + Linear(512→360) + Sigmoid
```

输出360维，对应360个pitch bin（20 cents间隔，覆盖约50Hz-1100Hz）。后处理用local average得到连续F0值。

## 关键模块

### WN (WaveNet)

用在Flow和PosteriorEncoder里。结构是标准的WaveNet：
- 多层dilated conv（dilation rate指数增长）
- gated activation: tanh(x) * sigmoid(x)
- 残差连接 + skip connection
- 可选的global conditioning (speaker embedding)

### ResBlock (HiFiGAN)

两种变体：
- ResBlock1: 3组(dilated conv → conv)，dilation=(1,3,5)
- ResBlock2: 2组dilated conv，dilation=(1,3)

每层都用weight_norm。

### NSF激励源

`SourceModuleHnNSF`根据F0生成正弦波激励：
1. `SineGen`按F0频率生成正弦波
2. 线性层合并谐波
3. 加噪声（unvoiced段噪声更大）

这个激励信号在Generator的每层上采样后都会加进去，让生成的波形更好地跟踪F0。

## 模型变体

| 类名 | 输入维度 | F0 | 说明 |
|------|---------|-----|------|
| SynthesizerTrnMs256NSFsid | 256 | 有 | v1模型 |
| SynthesizerTrnMs768NSFsid | 768 | 有 | v2模型 |
| SynthesizerTrnMs256NSFsid_nono | 256 | 无 | v1无F0版本 |
| SynthesizerTrnMs768NSFsid_nono | 768 | 无 | v2无F0版本 |

无F0版本用普通的Generator而不是GeneratorNSF，适合不需要音高控制的场景。

## 文件对应

```
infer/lib/
├── rtrvc.py          # 实时推理主类RVC
├── rmvpe.py          # RMVPE F0提取器
└── infer_pack/
    ├── models.py     # Synthesizer、Generator、Discriminator
    ├── modules.py    # WN、ResBlock、Flow层
    ├── attentions.py # Transformer Encoder
    └── commons.py    # 工具函数
```