---
title: Qt的进程间通信开发：如何在VS上进行Qt的COM、ActivedQt Server的开发
description: 关于QtCOM组件开发的记录实例
categories: Qt
keywords: Qt,C++,实例,COM组件
---

# Qt的进程间通信,以服务器的形式，手把手教你VS上进行Qt的COM、ActivedQt Server的开发，比保姆还保姆

## 一、Qt开发COM组件背景：COM组件是什么？为什么要用COM组件？

我是个Windows平台上的程序员，开发主要以Windows应用程序为主。目前在当前平台上我们做了很多进程间通信开发的尝试，包括但不限于Windows窗体消息（SendMessage等），共享内存，COM组件，已知的进程间通信方案还有socket通信（没必要，一般用于网络通信）和D-Bus方案(部分平台貌似不兼容，尚未了解）。

关于上述方案，Windows窗体消息和共享内存的方案我居然没写博客，之后可能会补上，这里暂时不做讨论。

先说开发场景：现在我有一个主框架或者说主程序，会有很多别的模块需要在外部开发，这些模块可能会需要用到主框架中的信息，或者说一些接口来调用一些特定的功能。比如说我一个课堂教学模块，可能需要实现屏幕广播，语音广播，资料下发等功能。出于低耦合的基本原则，我们当然不希望每个这样的教学模块里都实现一个类似的功能，这样不仅是对开发资源的极大浪费，也会极影响整个程序的维护难度。所以我们希望所有类似的功能都集成到一个主框架里，任外部的模块去调用功能，将二者隔离开来，这样不仅极大地提高了程序复用的可能，也能提高开发速度。

这个和之前的SendMessage方式最大的区别就是：如果想用SendMessage传递信号，首先需要两个应用程序之间互相获得句柄就挺麻烦的，需要从启动项传入然后再给予回执。其次SendMessage可能导致线程间不同步等情况出现，可能会导致部分程序的渲染、启动等县城不同步产生的意外问题。最主要的一点，SendMessage智能发送消息码，而这些消息码都是需要提前指定好的，而且接收方也不一定能统一，所以需要特定的消息码特定处理，很难进行全局的消息码处理。这些都是在之前的主框架开发中暴露出来的问题。

但是窗体消息有没有什么优点呢？当然是有的，最大的优点就是可靠，且开发简单。消息的发送是相当可靠的，而且一般的框架都会有一个关于窗体消息的收发机制，只需要重写或者指定接收函数即可，对于小组件或者进程内部可以采取类似的方法。

但我们是一个中心组件，是为了给其他进程提供服务的，所以我们这个中心服务需要更加简单，外部更加易用，所以我们要向所有模块的开发者提供适当的接口以调用，而且接口必须足够简单。

COM组件只需要暴露一些需要暴露在外部的类即可，比如我需要向外部暴露一个屏幕广播的接口，那就可以让其他的用户去通过COM组件去调用这个接口，至于具体是怎么实现的，这不是开发人员需要关心的内容，只需要模块的开发人员简单的调用接口，就像魔法一样，让功能在外部实现即可。

而主框架的开发人员也不需要把每个工具分门别类地用不同的进程管理工具去一个个进程单独分析，管理他们这个那个的消息码，或者管理这个那个具体行为，而是更多地把精力放在具体功能的具体接口上，也就不存在上下级模块调用的问题了。

现在让我们来说一下关于Qt如何进行COM组件的开发，或者说ActiveX控件的开发。ActiveX是Microsoft对于一系列策略性面向对象程序技术和工具的称呼，其中主要的技术是组件对象模型（COM）。在有目录和其它支持的网络中，COM变成了分布式COM（DCOM）。

国内外论坛关于Qt开发COM组件和ActiveQt Server开发的资料和讨论并不多，官方文档里也并没有提供我需要知道的资料，所以我这里写的东西不一定完全正确，如果我写的内容有问题，欢迎给我发送Issue提供一些相关的咨询或者疑问，也欢迎讨论。

## 二、我们做什么？

由上所述，我们想做一个可执行程序EXE，希望在这个程序运行的时候，暴露出一些接口供外部进程调用，来调用这个进程里面的一些类和方法，在这个进程正在执行的时候，可以通过COM组件的消息来执行指定的任务。

但是我们在实际开发过程中，发现ActiveQt Server编写的EXE并不能向调用发发送Signal消息。也就是说，在我们开发完COM组件后，启动该COM组件EXE，此EXE能够接收到调用方的请求，而且如果发送信号的事件是在请求的函数中执行的，那么该信号也可以成功发送给调用方。但是如果我是在COM组件EXE内主动发送的这个信号，比如点击按钮，那么接收方就接收不到这个信号了，不能达到双向通信的目的。目前尚未查明原因，所以我们只能退而求其次。

也就是我们通过一个COM组件来做中间件，让一个COM组件做单纯的中间件，只负责发送信号和接收事件，主框架和其他的工具都通过这个中间件来执行命令和接收消息。

## 三 我们怎么做？

根据上面的需求，我们就有了三个程序：主程序 COM中间件 子程序 ，主程序和子程序我在博客里就不提供了，这里来说一下COM中间件如何开发

![image](https://user-images.githubusercontent.com/102945300/206837934-db226315-e65e-457a-a1e8-826a92e30b75.png)

这里选Qt ActiveQt Server选项，它就会给你把默认全部设置好了

![image](https://user-images.githubusercontent.com/102945300/206837978-87f9649b-b26e-4e0d-8b53-18cd18b78fd9.png)

可以看到，这里多了一串

    QAXFACTORY_DEFAULT(ActiveQtServer1, //暴露给外部的类的名称，我们这里暴露的类名称为ActiveQtServer1，先就这么写
        "{82a36901-0766-498b-beaf-8b3e62e0b530}", //类ID，不用管
        "{b8de8377-4185-4c9d-a803-77b1939b1360}", //接口ID，不用管
        "{70744dbb-3062-4ade-9a0c-fc42dafa5b8f}", //事件ID，不用管，如果当前的类需要发送事件的话需要定义
        "{f763f5b7-cc63-4a05-9757-9debc4a7078d}", //当前lib 的ID，这个是这个lib的唯一标识，是我们要用的东西
        "{cd0da224-8eec-4739-a342-ecf88f6d3259}" //当前进程ID，这个如果是你将这个COM组件设定为
        
这个宏，这个宏命令的作用是为了给定一个GUID，设定一些默认的值，适用于一个DLL只需要暴露一个类的情况，如果一个DLL需要暴露多个类，则需要另外打算。

我们换一种写法，这样可以让这个结构更清晰：

我们在想要暴露的类中定义宏如下：

![image](https://user-images.githubusercontent.com/102945300/206839327-0264e81f-d499-49fd-bc31-c0eba1594d1e.png)

在这个类里定义了有关这个类的属性，也就是ClassID,InterfaceID,EventsID，然后我们还需要在总的宏编译（如果是EXE则可以直接加到main.cpp中，如果是DLL的话随便找一个头文件，反正是最后编译的位置处随便写就行了）处定义我们需要导出的类，内容如下：

![image](https://user-images.githubusercontent.com/102945300/206839465-0cbd0658-4c77-4091-af8c-bbe7a9e638fa.png)

如果是dll，我们直接把这一段放在cpp文件的最后就可以了

类似如此，注意这个#include "qaxfactory.h"要写在QAXFACTORY_BEGIN()的前面，因为这个宏本身也是qaxfactory.h带来的。这里QAXCLASS()中带着的是我们希望在这个QAxtive server中带出的类，如果我们有很多的类，可以以类似的方式来导出，就不用它默认的宏了。

另外需要注意的一点是，因为我们这个类默认带了个QWidget的类，所以会同时导出很多父类的乱七八糟的槽函数和信号会跟随其一同导出，目前我还没有想到该怎么屏蔽掉这些东西不让其导出，之后也许会找到，我会放在这里。

总而言之我们现在试着编译一下

![image](https://user-images.githubusercontent.com/102945300/206840177-4d4a0bb0-4129-4027-b33f-0ac022322f6a.png)

当出现这个指令的时候，说明我们的dll编译成功了，在编译的时候我们还同时注册了这个dll。如果我们的程序要挪到客机上去使用，就需要在控制台中输入regsvr32 xxx(dll名称).dll来注册这个dll控件。

当然了，除了注册，还需要给这个dll加载一些依赖，具体怎么做详情参考[windeployqt 打包Qt应用程序](https://www.baidu.com/link?url=86ZxD_w6QM0sb-Zj_Oo0yM7QkoQDwV-NaRJPrb9sKM6lAtndmYZ8JUwGUBNZr59FbUDl0yJAHk8tHGvJhd29ae8A2JXvvye_oFHMKKRKkNq&wd=&eqid=97de7861000d39ec0000000663943f94) 打包完毕后，这个COM组件就算是可以发布了

整体流程说完了，那我们现在该往里面写点东西了

写一个信号，一个函数，一个变量来举例。注意，函数和变量都必须是公用的才是可用的，否则是调用方不可见的

![image](https://user-images.githubusercontent.com/102945300/206840993-c0662f21-adcf-4d6d-b57d-458d5980f483.png)

其中红色的代表变量控制，黄色的代表接口，蓝色代表了信号事件。注意变量控制的写法，因为不管是读取还是写入变量其本质还是通过接口去实现的，这个Q_PROPERTY的宏是为了让调用方更好地操作ActiveX控件。

然后我们可以去注册表里面搜我们这个LIB的ID，找一下我们这个COM组件的名称：

搜索regedit打开注册表，搜索我们Class的ID ： A9787707-850D-4D42-BB09-5549713B008F，找到我们这个输出的类的唯一标识：

![image](https://user-images.githubusercontent.com/102945300/206841574-2ff586ef-882e-41ab-8137-b93d4310c883.png)

由上可见我们这个类的名称是ActiveQtServer1.ActiveQtServer1.1 这个是我们COM组件名称的唯一标识，这个要记住，后面要用

那么这边Qt的COM组件开发就结束了，现在我们来看一下怎么调用这个COM组件

## 3.如何调用COM组件？

我们新建一个项目 Qt_ComTest_Client如图 

![image](https://user-images.githubusercontent.com/102945300/206841163-dbb7d3c8-7dc8-40a4-86a9-bff28660a0aa.png)

我们调用COM组件主要通过QAxObject 或者QAxWidget实现，这里我就用QAxWidget 大体来说没很大区别，习惯上可以用QAxWidget，比较方便

      QAxWidget *ax_test;
      ax_test = new QAxWidget();
      ax_test->setControl("ActiveQtServer1.ActiveQtServer1.1"); //这里通过名字就可以直接找到COM组件了，如果你想通过COM组件ID也是可以的
      //ax_test.setControl("17C4C136-0EC8-4EF9-B2DF-891A4DBA6E6D");
      
      QString interfaces = ax_test->generateDocumentation(); //解析COM组件的接口文档

      QFile docs("AX_Interfaces.html");
      docs.open(QIODevice::ReadWrite | QIODevice::Text);
      QTextStream TS(&docs);
      TS << interfaces << endl;//将COM组件的文档尝试写入到一个html页面里面去，可以在里面看到有什么内容

     this->ui.plainTextEdit->appendPlainText(interfaces);
      
在这里我们就可以看到COM 组件提供的内容了，我们在程序根文件夹里面找到这个html文件，看一下内容

![image](https://user-images.githubusercontent.com/102945300/206842123-3dd259de-150d-4508-8d2f-63621175ed44.png)

可以找到我们定义的事件 add 和 test，点击一下 还有这个东西怎么用的提示

![image](https://user-images.githubusercontent.com/102945300/206842154-9bd2f2a8-2f11-4adc-9ac4-316aa128c62a.png)

![image](https://user-images.githubusercontent.com/102945300/206842161-192f0319-8c55-40d6-acc0-4e48c8891db0.png)


然后我们可以尝试绑定信号，并尝试引用内容。调用方法用dynamicCall("function_name(params)",params),接收信号通过QObject::connect(object,SIGNAL,eceiver,SLOT())的形式，调用参数通过property("object_name")的形式

来试一下

尝试触发事件,按下按钮：

    void Qt_ComTest_Client::on_pushButton_clicked()
    {
      qDebug() << "cliecked";
      QVariantList params = { 100,200 };
      qint32 result = ax_test->dynamicCall("add(int,int)", params).toInt();
      this->ui.plainTextEdit->appendPlainText(QString::number(result));
    }
    
来尝试接收一下信号
        connect(ax_test, SIGNAL(test(int)), this, SLOT(receive_slot(int)));


        void Qt_ComTest_Client::receive_slot(int result)
        {
            this->ui.plainTextEdit->appendPlainText("Receive Signal:" + QString::number(result));
        }

来尝试一下获取参数：

    this->ui.plainTextEdit->appendPlainText(QString(ax_test->property("number").toInt()));

来验证一下：

1.获取参数：

![image](https://user-images.githubusercontent.com/102945300/206842633-1b2ec8b2-b3d6-4069-9c55-3f7ab6315c73.png)

2.点击按钮获得回调：

![image](https://user-images.githubusercontent.com/102945300/206842643-86245980-f846-4f0b-b9da-cd8acce5bcf4.png)


3.点击控件上的按钮已得到消息：（注，这里需要通过 dynamicCall调用COM控件的show方法来展示界面）

![image](https://user-images.githubusercontent.com/102945300/206842907-665dcfd2-cb0f-4540-b310-f89ce0031763.png)

现在就算是完成了整个COM组件的开发，从建立到调用，具体详情我还是建议直接去看Qt的官方文档，不推荐自己一个人琢磨，貌似国内没有什么相关的讨论和研究。
