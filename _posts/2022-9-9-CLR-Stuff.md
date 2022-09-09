---
title: 关于如何在C#中调用C++的DLL，以及如何在C++中调用C#的DLL
description: 关于如何在C#中调用C++的DLL，以及如何在C++中调用C#的DLL
categories: 笔记
keywords: qt,学习笔记,C++,C#,CLR,联合开发
---

# 一、关于如何在C#中调用C++的DLL，以及如何在C++中调用C#的DLL

注：clr指公共语言运行库

CLR是一门非常恶搞的语言，就好像是在C++里面写C#的文件一样，也就是一种所谓的“托管模式”，把C++的代码丢到.net中去运行。

C#和C++形成的DLL有一层天然的屏障，并不能简单地互相调用，想要C#工程调用c++dll，需要先在其外部包裹上clr c++的外壳。

公共语音运行库提供了一系列能够使托管代码与非托管代码进行交互的解决方案

主要包含三类互操作技术:

1. 平台调用(P/Invoke):主要用于处理在托管代码中调用C库函数以及Win32 API 函数等非托管函数情形。

2.C++ Interop：适用在托管代码与C++ 类库、核心算法库之间进行高效、灵活的互操作过程。

3.COM Interop：该技术用于处理托管代码与COM之间的交互过程。

当然如果你的dll是那种类C的接口，就是声明了extern "C" 的，单纯的某个方法的函数（就是纯粹的在Cpp里面写C语言模式的接口，没有实例化对象，没有面向对象，没有类，只有结构体和面向过程），当然你的类大概率是不可能以这种形式去调用的，至于这样的dll 该怎么去调用，聪明的你肯定已经想到了，在主程序里面有很多类似[DllImport "xxx.dll"] extern xxx 的方法，去看吧，那里有你想要的。

我们大部分情况下调用的dll都是c++那种带类的dll(当然了，不带类的c++ DLL，听上去就像一个冷笑话)，在c#中调用这种dll则需要用到托管代码与C++类库，也就是我们的第二种方法

至于COM组件是什么我现在还没弄懂，之后如果搞懂了我会单独开一篇文章来专门介绍，如果我还记得的话，我会补充到这里。

因为Qt 中的信号和槽机制是无法通过CLR C++直接封装的(原因1:CLR C++ 继承的Object，Qt 中的类大部分继承QObject,CLR C++不支持多继承，所以无法将Qt信号和槽转换为 委托的形式，CLR C++可以封装没有使用信号和槽的Qt类,但是为了结构上统一不建议这样做)

所以如果需要向外部使用信号槽机制的话，最好是换成回调函数或者是委托（也不建议这么做），最好是回调函数，因为你这个dll不可能生来就是为了被C#调用而生的对吧。

调用过程:

1. 一般C# 调用 C++ 情况

C# ------> 托管 C++----->非托管C++

2. C# 调用Qt

C#---->托管C++--->非托管C++--->Qt

故 C# 调用Qt 多了一层 通过非托管C++ 封装Qt的过程(此过程主要是为了屏蔽Qt的信号和槽，将信号和槽转换为C++中的回调)

这里以我的一个完整工程为例：

## part1:原始轮子

我这里有一个第三方轮子 -Mixerwrap，这个类是一个纯纯的qt类，用来进行麦克风控制的

![image](https://user-images.githubusercontent.com/102945300/189310927-44d5d3a4-4214-4bbc-99ea-a71e51478e86.png)

原来的这个类是没有继承QObject的，这里需要记得加上QObject

![image](https://user-images.githubusercontent.com/102945300/189311376-e58f0c82-ef7e-4f6e-987d-7afd4fb65a0e.png)

然后我们生成，那么这个类就可以用来当成我们已经存在的Qt库了，甚至说可以不需要这个工程文件，只需要这个dll就可以了。

## part2 : 轮子套壳

 C#---->托管C++--->非托管C++--->Qt 
 
ok，现在我们完成了第一步Qt,现在我们要给qt套上非托管c++的壳，为了方便起见，我们非托管和托管C++的壳就放在一个工程文件内操作，首先创建一个MixerwrapHelper，这个工程就是我们两层套壳的地方。

![image](https://user-images.githubusercontent.com/102945300/189312042-2ffc0ae5-ed72-4bdb-9560-df6f91c72155.png)

这里方便起见，我直接在工程内部引用了Mixerwrap的工程

![image](https://user-images.githubusercontent.com/102945300/189312160-5eb0d0d3-54c1-4717-bab2-2314f5c6e15b.png)

当然了一般情况下是通过.lib文件去连接.dll文件完成引用，但想必你已经看到这了，不会还不知道怎么通过 lib 连接 dll吧，想必你已经非常清楚了。

开始套壳，我们建立一个新的工程文件，就叫Mixerwrap

![image](https://user-images.githubusercontent.com/102945300/189313593-0263d876-434f-43bc-bbc5-5ddb5be7694e.png)

然后我们来套第一层壳，添加一个非托管C++的类，就叫他MixerwrapStdWrapper

![image](https://user-images.githubusercontent.com/102945300/189312682-45d77c05-041d-493c-98b6-993b6a3d3dba.png)

注：目前托管类C++文件夹还是空的。

然后现在我们开始写这个非托管C++类，大概就是这样

![image](https://user-images.githubusercontent.com/102945300/189313859-3cc7da26-fdbb-4f32-b8f6-b7291323c807.png)

注：1.不一定需要导入这个_global文件，这个文件是一个导出声明的预编译头文件，类似这样

![image](https://user-images.githubusercontent.com/102945300/189314494-a9da4f03-fe54-4f11-b2b5-87eae86dae4f.png)

可以照着抄一份，这个全大写的这个是导出标志而已...置于这个预编译不会看不懂吧...

然后我们在这个导出类内实现功能，就如图，只是把方法搬运了过来而已，这样我们就得到了一个纯C++的无托管导出类MixerwrapStdWrapper

![image](https://user-images.githubusercontent.com/102945300/189317839-904dbb71-9e1c-4eab-9306-6c431b8c2dff.png)

这样做我们第一层套壳就成功了，现在开始套第二层壳MixerwrapCLRWrapper

我们新建一个C++的类，初始设定没有什么特别的，就像创建一个普通的C++类一样即可，我们给第二层壳MixerwrapCLRWrapper生成一下

![image](https://user-images.githubusercontent.com/102945300/189318621-a908ed52-2496-42aa-9e7a-cfa61136215e.png)

![image](https://user-images.githubusercontent.com/102945300/189318650-e1590fb4-7ad9-497b-831a-ac18ab640719.png)

ok，这个类我们要做一点小小的设置，右键MixerwrapCLRWrapper.cpp->属性->c++->常规->公共语言运行时支持->公共语言运行时支持 (/clr)

![image](https://user-images.githubusercontent.com/102945300/189318863-3f2d9033-37ac-4330-9ff9-c30033ca15ab.png)

套壳方式与第一层类似，如图所示

![image](https://user-images.githubusercontent.com/102945300/189319216-f2ca7fba-de3c-428b-b389-bc3847e8f83f.png)

注意四点：

1.引用的是非托管类C++ 文件的头文件

2.namespace 不是必须的，但是我建议你写，不要问为什么，.net写多了你就明白了

3.public ref class MixerwrapCLRWrapper 这个头要注意 一个是public 不加就读不到这个类，一个是ref，代表引用传递，这里不明白就去百度

4.建立的是非托管类C++的指针，不是原始DLL的指针，相当于是在非托管类DLL上方套了一层壳。

实现方法同套的第一层壳

![image](https://user-images.githubusercontent.com/102945300/189319771-4a8336c2-36fb-4a3a-abb3-b003b6c368c8.png)

这里需要注意的是，这里开始已经是CLR语法了，即在C++中写.net 或者说C# 程序的语法，有点怪怪的，但是并没有什么难理解的。

最后我们要对整个工程的性质修改一下，将其改为CLR导出DLL即可，我们在右键工程->属性->配置属性->常规->公共语言运行时支持->公共语言运行时支持(/clr)

![image](https://user-images.githubusercontent.com/102945300/189320330-08fcb894-ad6d-4422-9422-d06e5064d45c.png)

注意是整个工程的，不是某个cpp文件的。

## part3.调用

ok，最恶心的套壳结束了之后，接下来就是调用了。.net程序的托管方式使得程序的dll调用起来比C++的DLL调用舒服很多，我们建立一个新的C#程序，来调用试一下：

建立一个交MicphoneControlTest的窗口工程，简单写个窗口，可以调用两个功能

![image](https://user-images.githubusercontent.com/102945300/189320703-d8ffcea3-fef8-4e3c-8fa7-fb4a3c9e19c8.png)

尝试引用这个dll：右键引用->添加引用->浏览-》找到对应DLL->勾选并确定

当然我在这里偷懒就直接引用这个工程项目了

对象浏览器里应该就能看到这些东西了吧

![image](https://user-images.githubusercontent.com/102945300/189321009-b5ee01a7-21d5-4d5c-93e8-b0e11e93d5d8.png)

这就是我们从CLR这个类中导出的方法什么的了，我们来尝试一下调用

![image](https://user-images.githubusercontent.com/102945300/189321144-5bd97242-44b7-49fd-a597-607541110f2b.png)

尝试一下，点击，注意先将C#程序设为启动项，另外两个工程都是dll 是没法启动的，会提示是非标准的win32程序，需要注意


# 二、如何在Qt中调用C#的DLL

这部分内容不再更新，方案类似，只不过是反向套壳罢了，不会有人不理解吧？
