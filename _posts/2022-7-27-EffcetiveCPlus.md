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

另外值得说到的一点，两个成员函数如果只是常量性不同，那么是可以被重载的

比如这个例子：

![image](https://user-images.githubusercontent.com/102945300/181435525-4c79eab3-61b8-4914-a433-24340e25bab0.png)

我们根据对象的常量性不同，调用的函数也不尽相同，当一个普通函数和常函数重载时，如果一个对象是普通对象，那么调用的就是普通对象方法，如果一个对象是常对象，那么调用的就是常函数方法。
也就是说这个时候，有以下这几种情况![image](https://user-images.githubusercontent.com/102945300/181437589-35c643ad-e281-4775-b4e6-e8d86e6e5abd.png)

成员函数如果是const意味什么？有两种流行概念:bitwise constness or logical constness

bitwise const代表，成员函数只有在不更改对象之任何变量（static除外）时才可以说是const。也就是说const不改变对象内任何一个bit。这样的好处就是很容易看出来问题所在，只用查询是否有对成员变量赋值的动作即可，而且这也是const在c++中对常量性的定义。

但是这里也有问题：我们只是不修改任何值？这样就可以了吗？如果我们从const函数里返回的是指针，那有将会是一个什么情景呢？![image](https://user-images.githubusercontent.com/102945300/181438660-4a76ebc3-c364-41f8-81e9-fe494076ed98.png)

在这个例子里，class 不适当地将其[]符号声明为cosnt成员函数，这个函数返回了一个对象内部值的引用，而且我们的[]也确实不更改pText，也符合我们所谓的bitwise const定义，但是这又会有新的问题，比如如下这段代码：

![image](https://user-images.githubusercontent.com/102945300/181438841-3e8bd4a1-c32f-44e6-9578-1fb99de9de99.png)

也就是说，我们返回的这个引用，它仍然可以通过指针来操作这个const字段的内容，这样就和我们的const精神不符了，那么const也就没有含义了。

另外一个流派：logical constness的含义:const成员函数可以修改他所处理的对象内的某些bits，但只有在客户端侦测不出的情况才得如此，比如CTextBlock class 有可能告诉缓存文本区块的长度一边应付询问：

![image](https://user-images.githubusercontent.com/102945300/181439353-1407b482-19d5-4675-9f19-2058b69d7b5f.png)

比如这个length函数，这显然就不是bitwise const，因为在这里textLength和lengthIsValid都被修改了，这样就不能说是bitwise constness，但是这两笔数据的修改对const CTextBlock对象而言应该是可接受的不是吗？但是编译器不同意啊，这咋整呢？

那么就要利用C++的一个与const相关的摆动场：mutable，mutalble释放掉non static成员变量的bitwise constness约束

也就是这样使用：

![image](https://user-images.githubusercontent.com/102945300/181442256-9ad3ccf7-998e-4505-8b8c-e71ad63ac0ff.png)

### const和non-const成员函数中避免重复

对于bitwise的问题，也许mutable诗歌解决办法，但他不能解决所有的 const相关难题，之前我们说constness不同的话，那函数就可以重载，如果我们要返回的值不一样，就可能会出现一些令人不愉快的代码膨胀问题，比如：

![image](https://user-images.githubusercontent.com/102945300/181443288-2334cccc-0029-446e-a014-23444bc41805.png)

如上，其实是一样的代码，我们却重复了两次，这其实是相当糟糕的写法。那么我们可以试着用转型，即强行将const的类型成none const 类型，如下：

![image](https://user-images.githubusercontent.com/102945300/181443639-2d758cf7-b246-4a27-87e4-f0ccb2b213b5.png)

但需要注意的是，转型:cast，并不是一个安全的做法，但是代码重复实在不是一件令人愉快的事。在本例中因为输出的值const operator[]和 none const operator[]之间的唯一差别就是多了个const修饰，所以这样强制转换是安全的，因为不论谁调用non-const operator[]都一定首先有个non-const对象，否则就不能调用这个non-const函数。

另外比较符合直觉的一点就是，为什么不是const函数取调用non-const函数呢？这样不是更方便了，直接给生成的变量添加上一个const属性，是不是就可以了呢？答案是否，这并不是我们该做的事

记住，const成员函数承诺绝不改变其对象的逻辑状态，而non-const成员函数却没有这样的承诺，如果我们在const成员函数里调用non-const函数这样是要冒风险的

请记住：

1.将某些东西声明为 const可以帮助编译器检测出错误用法。const可以被施加于任何作用域内的对象、函数参数、函数返回类型、成员函数本体

2.编译器强制实施bitwise constness，但你编写程序时应该使用 概念上的常量性

3.当const 和 non-const 成员函数有着实质性等价的是现实，令non-const版本调用const版本可避免代码重复

## 1.4确定对象被使用前已被初始化

