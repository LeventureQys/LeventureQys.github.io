---
layout: post
title: Qt栅格布局、ScrollArea和用户选择界面
description: 从用户选择界面出发，到聊聊如何使用栅格布局，ScrollArea
categories:  实例
keywords: 教程,Qt,素材,实例
---

# 用户选择界面

就我们在实际开发的时候可能需要面对这样一个界面

![image](https://user-images.githubusercontent.com/102945300/173481199-27b662be-df7f-44b2-a025-773df7de5852.png)

做个demo试试看

![GIF 2022-6-14 11-14-02](https://user-images.githubusercontent.com/102945300/173485884-74da6762-7d04-4756-9111-4a65e957c26d.gif)


其实我们可以分解一下这个界面

就是除了控制相关的内容，最主要的就是这个界面之上，有一个个动态的输入的控件，上面都是学生的信息、头像等等数据，而且这个数据是动态变化的，也就是说主框架来条消息，我这个exe里的数据就要变动

那问题来了，这个部分怎么实现呢？不可能是让代码去一个个把空年间直接定位，这显然不显示，所以要用更自动化的方法-->栅格布局和scrollArea

栅格布局不用多说，就是可以栅格化摆放控件的一种布局，是Qt特有的部分

而scrollArea则是一个特殊的控件，在里面的内容如果超过当前scrollArea，则会令该控件自适应地生成滚动条

在实际开发中遇到了几个问题：

### 1.实际操作中，我们该如何使用栅格布局？

因为初始的时候我们在整个代码中是不带元素的，所以不能提前在我们需要的地方提前布置上栅格布局，这也为我们后面的一个问题出现奠定了基础。

由上，在实际的开发中栅格布局只能通过代码实现。我们在类中声明一个栅格布局的指针：
![image](https://user-images.githubusercontent.com/102945300/173484414-0266c4c9-2118-417b-b115-8082f73fdbfd.png)


注意c++中的指针一定要给空间，也就是后面的这个new QGridLayout()是必须的，否则可能会导致一些不必要的错误信息出现。

因为我们的layout是给的指针，所以如果中途没有单独析构，那么整个指针会存续整个软件的生命周期中，所以我们实际开发中只需要对需要用到该布局的部分进行->setLayout(QLayout *) 操作即可。

### 2.向layout中添加部件 

首先我们要确定layout每个部件的宽度，也就是最小大小。不然在实际的开发过程中，layout特性很可能就会导致宽度不够从而使得部件挤在一起，所以我们需要设置一下

![image](https://user-images.githubusercontent.com/102945300/173484918-ad5c9246-08ca-4031-89cd-5aa5bbcf99ae.png)

这里有个问题，就是每行每列的长度都只能单独设定，两个方法中的参数，一个是当前行、列，第二个才是具体的数值。而不是设定一个总的外推到所有的行列，所以在这里我们也是每次更新数据的时候就修改一次即可。

添加部件的方法很简单，就是向其中输入命令，包含需要输入的widget，第几行，第几列。这里输入的temp是我自定义的控件

![image](https://user-images.githubusercontent.com/102945300/173485167-4b044489-6c3d-4e58-944f-ce713705faba.png)

### 3.给scrollArea绑定了gridlayout，并向其中输入了控件之后，为什么没出现进度条？

因为scrollArea并不是一个独立的控件，其包含两部分，一部分是gridlayout本体，还有一个部分是scrollAreaWidgetContents，这是一个附属的widget控件，真正的内容要输入到scrollAreaWidgetContents中才可以自动地生成进度条，否则就不行

也就是说不论是我们的QGridLayout还是别的什么，都应该是直接输入到scrollAreaWidgetContents，这样就不会出现之前的问题了，控件也可以正常运行了。




## 7-3修改

其实完全没必要用gridlayout来进行这个修改，事实上有一个更简单的方法，就是直接一个个的插入widget，然后对应的位置就直接给它指定了（注：我们这里的窗体大小是要求不能变化的，如果要要求可以变化，则还是需要用到layout）

具体可以上代码

![image](https://user-images.githubusercontent.com/102945300/177041458-2c11643e-3b78-4af6-aa1b-b8d7290abd29.png)

如果需要遍历整个ScrollArea的话，则可以如下：

![image](https://user-images.githubusercontent.com/102945300/177041481-55c7e0db-18c3-4565-9441-0a6084a4bbc7.png)

