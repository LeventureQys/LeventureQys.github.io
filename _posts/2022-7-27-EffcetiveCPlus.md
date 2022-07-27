---
layout: post
title: Effective C++试读笔记
description: 简单看看EffectiveC++这本C++程序员圣经
categories: 笔记
keywords: 学习,C++,笔记,经验之谈
---

# Part1 习惯C++

## 1.1 视C++为一个语言联邦

C++非常的屌，除了开发效率和编译效率不高，其他的都非常屌

C++ 可以视为一系列的语言联邦构成的紧密结合体，分为以下四个部分

1. C

![image](https://user-images.githubusercontent.com/102945300/181257629-7dde1d80-3def-4601-93b9-a02b29f5f7bf.png)

2.C with Classes 

![image](https://user-images.githubusercontent.com/102945300/181257667-d4f979ba-0480-400c-978a-b3972b28fb85.png)

3. Template C++ 泛型编程

![image](https://user-images.githubusercontent.com/102945300/181257718-4c523969-0622-4e88-b8e6-6b5ad6362b6b.png)

4.STL

![image](https://user-images.githubusercontent.com/102945300/181257751-42bec57e-c05f-4e67-adcc-5c3a8a8d799d.png)

## 1.2尽量用const enum inline替换 #define

其实这里也好理解，准确的说，是以编译器替换预处理器，因为#define其实不被视为语言的一部分,预处理器的话，如果这个数值出现错误了，那么可能获得的编译错误信息就是其中具体的值，而不会出现这个预编译的名称

比如我 #define a1 1.6，我在后续的程序中用到了这个a1，但是出错了，那么就不会报a1的错误，而是 1.6 的错误，这就很容易给人带来困惑，如果是用const double a1 = 1.6，那么此处报错就会提示a1的问题，甚至IDE本身可能就会捕捉到这个语法错误。

另外一个值得注意的是，如果我们想要一个限制在class内的const成员，那么要用static修饰

![image](https://user-images.githubusercontent.com/102945300/181259050-84200dcb-adb5-4e0c-8ac7-0d8d88c21770.png)

当然有些旧的编译器 不允许static 整数型 class常量 完成in class初值设定，可以改用 the enum hack补偿做法：一个属于枚举类型 的 数值 科权充ints被使用

![image](https://user-images.githubusercontent.com/102945300/181260835-fcd0c8d9-584e-471f-b401-042fc9fa2a2f.png)

enum hack值值的认识

一、enum hack的行为某方面说比较像#define 而不像const，取const的地址合法，取enum的地址就非法，#define的地址也不能取，如果不想让别人去取你pointer或者reference指向某个整数常量，这个enum hack可以实现这个约束。

二、实用主义，许多代码用了它，所以必须人事，这也是模板元编程的基础技术。

继续讨论预处理器，还有一种用法就是实现宏，就是那种看起来像函数的预处理，比如![image](https://user-images.githubusercontent.com/102945300/181261576-d3d2f7c2-3aaf-46ec-b293-5b1c1b88dc3c.png)

当然这个写法 也不太好，如果一定要写，就必须记住为宏中所有的实参加上小括号，否则可能会出现一些意想不到的问题：

![image](https://user-images.githubusercontent.com/102945300/181262073-c65c72fb-7ad2-41b0-963e-4f78626504c1.png)

当然了这种问题有更好的解法，就是template inline函数

![image](https://user-images.githubusercontent.com/102945300/181262230-bf2a9a0c-078c-471f-82a9-c0844d701cee.png)

这样定义的函数是一个真正的函数，遵守作用域和访问规则，光是这点就比宏好了不少。

当然预处理仍然有它存在的道理，比如#include 和 #ifdef/ifndef仍然是当前的重要一环，可能还需要时间，预编译的问题才能慢慢解决。

不过本节的重点就以下两点：

1.对于单纯常量，最好用const对象或者enums 替换 #defines

2.对于形似函数的宏，最好用inline替换 #defines

## 1.3尽可能用const

const 允许你指定一个语义约束，编译器会强制实施这项约束。就是可以让你指定一个不会变的值，就这样。

![image](https://user-images.githubusercontent.com/102945300/181263816-63470d33-bef7-4c27-9e01-3665d1044de2.png)

![image](https://user-images.githubusercontent.com/102945300/181263840-ee607a83-06db-4d42-8fb6-2f886217070a.png)

![image](https://user-images.githubusercontent.com/102945300/181264252-767034c2-f5e3-495b-96ff-76898b49c72a.png)

小结：如果const位于的左侧，则const就是用来修饰指针所指向的变量，即指针指向为常量；如果const位于的右侧，const就是修饰指针本身，即指针本身是常量。说是这么说，但是想必也不会有人用常指针这种东西吧。。。

当然了，const 和变量类型之间换一换还是没什么的，比如：

![image](https://user-images.githubusercontent.com/102945300/181264502-f2dea7c9-7e34-48a4-8266-b0ed07c3d65f.png)

举个例子，如果我们从STL的迭代器触发，我们想表示这个迭代器不得不指向不同的东西，最好是所指的东西也不可被改动，即希望STl模拟一个const T*指针，那么就需要一个常迭代器

const_iterator

![image](https://user-images.githubusercontent.com/102945300/181265031-d0effbc5-143b-4f1c-905b-6bd4c0ec16c4.png)

const最猛的用法就是面对函数声明时的应用。在一个函数声明式内，const可以和函数返回值、各参数、函数自身产生关联。

比如我们：

![image](https://user-images.githubusercontent.com/102945300/181266193-0ba3723f-2e2f-483d-9d46-f66f915c5ed7.png)

卧槽，为什么这么写啊，返回一个const类型，那不傻逼了吗，这当然是我们可爱的用户，有时候真的是你想都想不到...比如

Rational a,b,c;
..
(a*b) = c; //在a * b的成果上调用 operator=

本来这个*号就是被定义的了，现在又要让这个值等于c，那不相当于是这个operator*白写了吗？这样肯定是不行的，但是这么写又非常符合我们的直觉。

