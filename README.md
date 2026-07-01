# hugo-paperMod Example

This repository offers an example site for [hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod)

## Install

Read Wiki => [hugo-PaperMod - Installation](https://github.com/adityatelange/hugo-PaperMod/wiki/Installation)

## Directory Tree

```
.(site root)
├── configTaxo.yml
├── config.yml
├── content
│   ├── archives.fr.md
│   ├── archives.md
│   ├── posts
│   │   ├── emoji-support.md
│   │   ├── markdown-syntax.fa.md
│   │   ├── markdown-syntax.fr.md
│   │   ├── markdown-syntax.md
│   │   ├── math-typesetting.md
│   │   ├── papermod
│   │   │   ├── _index.md
│   │   │   ├── papermod-faq.md
│   │   │   ├── papermod-features
│   │   │   │   ├── images
│   │   │   │   │   ├── homeinfo.jpg
│   │   │   │   │   ├── profile.jpg
│   │   │   │   │   └── regular.jpg
│   │   │   │   └── index.md
│   │   │   ├── papermod-icons.md
│   │   │   ├── papermod-installation.md
│   │   │   └── papermod-variables.md
│   │   ├── placeholder-text.md
│   │   └── rich-content.md
│   ├── search.fr.md
│   ├── search.md
│   └── tags
├── LICENSE
├── README.md
├── resources
│   └── _gen
│       ├── assets
│       └── images
├── static
│   ├── android-chrome-192x192.png
│   ├── android-chrome-512x512.png
│   ├── apple-touch-icon.png
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   ├── favicon.ico
│   └── papermod-cover.png
└── themes
    └── hugo-PaperMod
```

---

## LLM 文章导入规范

> **使用方式**：每次让 LLM（Claude / GPT 等）帮你撰写、导入、改写文章前，请先让它阅读本章节，并要求它严格遵守以下规则。可以直接说："请先阅读 `README.md` 的『LLM 文章导入规范』章节，然后再开始。"

### 1. 文章存放位置

- 所有正文文章统一放在 [content/posts/](content/posts/) 目录下。
- 文件名使用中文或英文均可，但要与 `title` 保持语义一致，后缀必须为 `.md`。

### 2. Frontmatter 模板

每篇文章顶部必须包含以下 YAML frontmatter（按需删改字段，但 `title` / `date` / `math` 三项不能漏）：

```yaml
---
author: "Leventure"
title: "文章标题"
date: "YYYY-MM-DD"
description: "一句话概述，会出现在列表页和分享卡片里"
tags: ["标签1", "标签2"]
categories: ["分类名"]
math: true        # 文章包含任何 LaTeX 公式时必须设为 true，否则 KaTeX 不会加载
ShowToc: true
TocOpen: true
---
```

- `math: true` 缺失会导致全篇公式无法渲染——只要文中出现 `$...$` 或 `$$...$$`，就必须加。
- `date` 写绝对日期，不要写"今天""上周"等相对表述。

### 3. 数学公式书写规则（最重要）

本站使用 **KaTeX + Hugo Goldmark passthrough** 渲染数学，对写法有硬性要求：

#### ✅ 行内公式

用单 `$` 包裹，例如 `$x_k = F x_{k-1} + w_k$`。两端紧贴文字即可，不需要转义下划线。

#### ✅ 单条独立公式

用 `$$..$$`，并且**前后各空一行**：

```markdown
上文……

$$H(s) = \frac{\omega_c^2}{s^2 + \sqrt{2}\omega_c s + \omega_c^2}$$

下文……
```

#### ❌ 禁止：多个 `$$..$$` 相邻排列

下面这种写法会触发渲染 bug（源码和渲染结果同时显示，或后续公式被吞）：

```markdown
$$L_t = \alpha(y_t - S_{t-m}) + (1-\alpha)(L_{t-1} + T_{t-1})$$
$$T_t = \beta(L_t - L_{t-1}) + (1-\beta)T_{t-1}$$
$$S_t = \gamma(y_t - L_t) + (1-\gamma)S_{t-m}$$
```

#### ✅ 正确：多行公式用 `aligned` 合并成一个 `$$..$$` 块

```markdown
$$
\begin{aligned}
L_t &= \alpha(y_t - S_{t-m}) + (1-\alpha)(L_{t-1} + T_{t-1}) \\
T_t &= \beta(L_t - L_{t-1}) + (1-\beta)T_{t-1} \\
S_t &= \gamma(y_t - L_t) + (1-\gamma)S_{t-m}
\end{aligned}
$$
```

`&` 用来对齐（一般放在 `=` 前），`\\` 换行。需要额外行间距用 `\\[4pt]`。

#### 其他细节

- 矩阵用 `\begin{bmatrix}...\end{bmatrix}`。
- 分段函数用 `\begin{cases}...\end{cases}`。
- 中文标点不要写进公式里——用英文逗号、句点。
- 公式里需要文字时用 `\text{...}`，例如 `\text{Predict:}`。

### 4. 图片资源

- 图片放在 [static/img/](static/img/) 下，按文章名建子目录，例如 `static/img/signal_denoise/00_raw.png`。
- 文章内引用时用绝对路径，省略 `static`：`![说明](/img/signal_denoise/00_raw.png)`。
- 不要把图片直接放在 `content/` 里。

### 5. 表格、代码块、引用

- 表格用标准 GFM 语法，对齐符号 `:------:` 表示居中。
- 代码块写明语言：` ```python `, ` ```bash `, ` ```yaml ` 等。
- 引用块 `>` 后留一个空格。

### 6. 风格约定

- 中英文之间、中文与数字之间**不要**强行加空格，由 Hugo / 字体处理。
- 章节分隔可用 `---`，但同一篇里不要滥用。
- 不要在正文里写 emoji，除非作者明确要求。

### 7. 提交前自检清单

在交付前，LLM 应自行确认：

- [ ] frontmatter 完整，含 `math: true`（若有公式）
- [ ] 没有相邻的 `$$..$$` 块
- [ ] 多行公式都包在 `aligned` / `cases` / `bmatrix` 等环境里
- [ ] 图片路径以 `/img/` 开头，文件已放到 `static/img/` 对应目录
- [ ] 代码块带语言标识
- [ ] 日期为绝对日期
- [ ] 从todo里面获取文章并更新完成后，需要清理todo目录

---

