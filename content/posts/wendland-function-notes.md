---
author: "Leventure"
title: "Wendland Functions"
date: "2026-07-07"
slug: wendland-function-notes
description: "Wendland 紧支撑径向基函数的性质、构造与插值应用"
tags: ["Wendland", "RBF", "径向基函数", "插值", "数值分析"]
pdf: true
categories: ["机器学习"]
ShowToc: false
TocOpen: false
---

# Wendland Functions

Wendland 函数是一类具有紧支集的径向基函数（Compactly Supported Radial Basis Functions），由 Holger Wendland 在其 1995 年的论文 *Piecewise Polynomial, Positive Definite and Compactly Supported Radial Functions of Minimal Degree* 中提出。

这类函数广泛应用于散乱数据插值（scattered data interpolation）、无网格方法（meshfree methods）等领域，其紧支撑特性使得插值矩阵具有稀疏性，显著降低了大规模问题的计算复杂度。

{{< pdf src="/pdfs/Wendland-Function.pdf" >}}
