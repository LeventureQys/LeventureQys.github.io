---
layout: post
title: 李宏毅机器学习笔记:从0到写AI
categories: 学习笔记
description: 李宏毅教学视频的学习笔记
keywords: 机器学习,深度学习,学习,学习笔记
topmost: true
---

# part1.基本介绍

## 1.机器学习的三个任务

一般情况下，我们在机器学习中有三个基本任务，分别是Regression Classification和Structured

Regression是计算数值解

而Classification则是求离散解（分类），也就是做选择题

Structured则是找一个结构，这种结构除了数据结构，还包括文字、绘画等广义的结构或者说某种意义上，让机器学习了之后创造一种东西出来

## 2.找函数三步骤

### 2.1写出一个带有为止参数的函数

![image](https://user-images.githubusercontent.com/102945300/180217011-7a979c24-dea0-4e4c-9087-4ce668fb88a8.png)

也就是面对一些我们位置的问题，仙写出一个带有未知参数的函数，也就是先猜测一下我们要如何求这个问题的解，比如一下这个简单的线性函数：

![image](https://user-images.githubusercontent.com/102945300/180217224-67013c99-d3ea-4fb2-98d2-9a1405903848.png)

![image](https://user-images.githubusercontent.com/102945300/180217242-6877d077-3659-409f-9fe6-e1221f9d4830.png)

这个猜测来自于作者对问题本质的了解，我们管这种带未知参数的函数为模型，也就是数学模型

### 2.2 定义Loss

第二部要定义一个Loss

![image](https://user-images.githubusercontent.com/102945300/180217569-6e447273-9794-43ef-878d-4f2bc473e3fb.png)

这个所谓的Loss其实就是一个Function，输入的值就是我们定义的未知参数，在上述就是我们给定的b和w（参数，变量是x），这个Loss输出的值代表 现在如果我们把这一组未知的参数设定为某个值的时候，这个数值好还是差。

就像我们在计算一组数据的线性回归方程的时候，是不是会有一部分和实际上的值偏差？某种意义上来说，这个Loss函数就是在对这个偏差值的情况做出评价

![image](https://user-images.githubusercontent.com/102945300/180218400-d29b8d82-69a9-411b-8453-41626471a233.png)

这里我们可以把每个离散值的误差加起来然后求个平均（原文中引用的视频播放量作为参考，但我觉得这个比较好理解，就随便放张图了）

![image](https://user-images.githubusercontent.com/102945300/180218653-828ed751-c9b7-405f-82b1-cc79ecde0fa2.png)

这种就是绝对差值叫MAE Mean Absolute error 还有就是把这个插值的平方算出来的，就叫Mean Square error，或者MSE，作业利用的MAR比较多

![image](https://user-images.githubusercontent.com/102945300/180220676-4accca20-e80d-418f-baef-b6c85e2026cc.png)

计算出来得到一个Error surface

## 2.3 优化

当然了，第三步就是优化问题，最佳化问题的结果，其实也就是我们要去找最好的w和b，让loss最小化

在这们课程里我们会用到的优化方式就只有梯度下降，现在我们简化一下，假设我们的未知参数只有一个，就是w

那当我们有不同的w，就会有不同的 loss，这时候我们的error surface就是一条曲线，如下图：

![image](https://user-images.githubusercontent.com/102945300/180221241-b7da5034-f9bf-4c0b-b517-66956a791d72.png)

那我们要怎么去找这么一个w呢？

![image](https://user-images.githubusercontent.com/102945300/180221297-7331157a-b59c-4861-b976-56456b3119a0.png)

看着复杂，其实也就是跟着这条曲线的斜率变化去做调整：斜率为负，则向右找；斜率为正，就向左找

那每次走多少呢？这就涉及到一个调参了：

![image](https://user-images.githubusercontent.com/102945300/180221899-c4fee0e1-30a2-415b-9ae6-48ff6af7dbb4.png)

注：loss是自己定义的，所以可以是负的

当然这里老师也注意到了局部最优解的问题，其实我也想到了，就是如果只根据这个逼近“极小值”的方法，其实是找不到最小值的，这个确实是梯度下降方法的一个问题。下面是老师的一段那话：

![image](https://user-images.githubusercontent.com/102945300/180222795-c13392af-a704-42c4-b9a6-f565d71e1166.png)

现在我们回到之前的有两个参数的模型，也就是有w和b的那个，这时候我们如何梯度下降呢？

![image](https://user-images.githubusercontent.com/102945300/180223440-92f21fbc-9cfa-4c2a-80fb-bf0dc6501ef2.png)

这个η就是我们定义的步长，或者说叫learning rate

![image](https://user-images.githubusercontent.com/102945300/180224632-c56ff1c0-f1e6-486d-8466-3c48dee5771a.png)

其实由上可以看出，整个loss的收敛方向其实是朝着 多个维度进行的，并不是单指一个方向，当多个维度下的数据都有不同的方向时，其效应就像带有引力的洞一样，会将我们的点向最深不见底的洞吸引过去。

什么时候停下来？两种情况

1.一开始就设定好最多迭代多少次，设定好迭代次数

2.最好的情况就是直接找到了极小值 w' = 0，当然这个...

### 线性模型

以上三个步骤：定义模型，写出loss，优化参数这三个步骤合起来就被我们称作训练，当然了，这个训练是在我们知道答案的基础上进行的，但是这并不是我们想要的，某种意义上来说这只是对过去规律的总结，真正对于我们重要的是未来的发展，预知未来。

那我们来拿着数据来预测一下试试看

![image](https://user-images.githubusercontent.com/102945300/180225961-53c89896-827b-46ca-afd0-39ceca300832.png)

然后我们发现，真实的数据和我们预测的数据 还是有很大的差距的，实际的数据有一定的周期，周末看的人多，工作日看的人少，然后七天一个循环

那我们假设给定它一个这样的参数列表：

![image](https://user-images.githubusercontent.com/102945300/180226757-16941c0e-c5d4-440c-abc2-fcc5da843262.png)

我们之前只考虑了一天，那我们最低的loss是0.58k的误差，其实这里计算出来的误差是0.33k，这两个数据至今的差距，就不言而喻了。

那我们考虑一个月，甚至考虑一年，又怎么样呢？我们管这种模型称作线性模型，之后会浅谈怎么把线性模型做得更好。
