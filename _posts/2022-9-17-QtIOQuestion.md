---
layout: post
title: Qt对象跨线程出现的问题记录，以及解决方案
categories: 开发日志
description: Qt在跨线程开发的时候可能会出现不少问题，在这里记录一下
keywords: Qt,C++,实例,开发日志
---

# Qt在跨线程开发的时候可能会出现不少问题，在这里记录一下

Qt目前用下来还是非常强大的，虽然只是用在桌面端程序开发上，但是其强大的桌面开发库真的挺好用的（Layout除外，你妈死了）。

Qt除了UI，还有一些封装好的IO库，比如QFile和QTcpSocket等等，总的来说还是可以的。但问题是Qt总的来说还是一个封闭的框架，和非框架部分的兼容并没有想象中那么理想，就从之前的CLR库的转换就能看得出来了--但是你现实总是这样，你只能要求要么要么，不能既要又要，对吗？

扯远了，继续来说一下跨线程的问题，当然了这里的跨线程不是指在Qt生态内的跨线程，而是指和第三方一起操作的时候出现的跨线程问题。

首先不要以为跨线程离自己很远，跨线程无时无刻不在出现，比如你引用了第三方的DLL，你调的每一个接口，你都不知道里面会发生什么，尤其，尤其是回调函数，回调函数几乎不可避免的都是跨线程函数（你可以想象一下一个不跨线程的、阻塞的回调函数接口，提供给第三方，如果有这么个接口放给我我真的会想要杀了开发的🐎的），然后就会出很多很傻逼的问题，我等会来举例。

典中典之比如跨线程调用QTcpSocket的 write接口，就会出现：

    socket notifiers cannot be enabled from another thread

要解决这个问题，直观的说就是不要跨线程操作，网上也有很多类似的说明。这也是有道理的，很多时候真的是设计问题导致的，因为设计失误出现了不应该有的跨线程操作。

当然也可以用信号和槽封装一下，但是这样会涉及很多不必要的代码，我个人觉得也太过于麻烦，就是给发送事件绑定一个信号，然后这个信号去触发一个操韩素华，这个槽函数内部才是发送tcpsocket通信的，这个方法是真的傻逼，我觉得如果是我写的这个类库，我肯定会发现这个傻逼问题，然后想个别的接口来解决这个问题。

那么我这里就提供一个更简单的方法，对QTcpSocket跨线程调用代码如下：

    QMetaObject::invokeMethod( &socket, std::bind( static_cast< qint64(QTcpSocket::*)(const QByteArray &) >( &QTcpSocket::write ), &socket, QByteArray( "xxxx" ) ) );

来分析一下这个 invokeMethod 调用，接口的定义是这样的

    bool invokeMethod(QObject *context, Functor function, Qt::ConnectionType type = Qt::AutoConnection, FunctorReturnType *ret = nullptr)

context：表示被调用的函数要在 哪个对象 的生存线程运行

function：被调用的函数

主要看这两个，后面都有缺省值，不用管。

在本例中context指定socket，就表示在socket的生存线程运行，这可能是任何线程，取决于你在哪里实例化这个socket。如果填写qApp，就表示指定在主线程运行。

function被赋值了一个std:bind，这是因为write不是槽函数，使用起来还是有点麻烦，不能直接写名字走moc系统。所以要手动用std::bind把函数给包起来。

关于这个std::bind的3部分：

    std::bind( static_cast< qint64(QTcpSocket::*)(const QByteArray &) >( &QTcpSocket::write ), &socket, QByteArray( "xxxx" ) )

static_cast< qint64(QTcpSocket::*)(const QByteArray &) >( &QTcpSocket::write )：QTcpSocket中，叫write的有很多个，所以要依靠 qint64(QTcpSocket::*)(const QByteArray &) 去指定出来是哪一个。这是C++的方法，和Qt无关。

&socket：表示要执行谁的write，有点类似于指针的角色

QByteArray( "xxxx" )：调用write时给的参数

除了IO相关的类，其他有一些Qt的类也不可以跨线程操作，比如说QTimer，也会报错

QObject::startTimer: Timers cannot be started from another thread

按照上面说的调用原理，可以这样写：

QMetaObject::invokeMethod( &timer, std::bind( static_cast< void(QTimer::*)(int) >( &QTimer::start ), &timer, 1000 ) );

对了，start是一个槽函数，所以如果借助moc系统的话，可以这样写（两个写法是等价的）

QMetaObject::invokeMethod( &timer, "start", Q_ARG( int, 1000 ) );

注意！在QMetaObject::invokeMethod配合std::bind使用的时候，5.10.0版本的Qt会有内存泄漏，bug如下：

https://bugreports.qt.io/browse/QTBUG-65462

请注意你的Qt版本，以及bug的修复情况，酌情使用这个方法。


两个实际问题，可以参考一下，以防止后续的开发出现类似的问题：

1.回调函数调用一个Qt弹窗DLL出错

之前有一个弹窗，就是当我们接收到回调函数的信号，就向外弹出一个窗口，然后这个窗口是个Dialog，会返回一个int值，根据这个int值来决定结果，挺常见的，对吧？

但是这个弹窗有个问题，就是第一次弹出来之后有可能会导致整个程序崩溃，但是为什么会这样？我和戴工检查了一轮下来，发现是DLL内部的 paintEvent崩溃导致的，那么有两个问题，一为什么paintEvent崩溃会导致这个画面，二是为什么paintEvent会崩溃？

其实这个paintEvent崩溃是有弹出提示的，我不记得具体是什么了，反正好像是this IO Device can only paint once，大致意思就是这个绘制器一次就只能绘制一个画面。

绘制器是没问题的，我以为是同线程下的提示框和当前广播框之间抢占线程了导致的问题，于是我把提示框放在了整个程序绘制完成之后，但是并没有用，该崩溃仍然崩溃。

我在想是不是因为调用了两次导致的，于是我进行了测试

一、写Demo同时打开两次这个提示框是没问题的

二、修改了一次只打开一个提示框，仍然报错。

其实显然不是这个问题，因为提示框和主线程是保持一致的，所以无论如何都会保持顺序绘制，不会出现绘制器抢占的问题。

最后排查一路，最后发现问题还是出现在IO Device对跨线程调用上。因为第一个启动的窗口是通过回调函数启动的（其实其他函数也是通过回调函数启动的，但是非常巧合的是我在设计时后续启动的窗口时通过信号槽机制来启动的，所以即使是跨线程依然运行正常）

首先第一点，Qt IO Device本身在跨线程调用的时候就有可能出现抢占问题，不论当前是否在绘制（更何况其实就是在绘制，我的LiveEffect一直在不停地绘制...)于是跨线程调用绘制器就出现了抢占，搞得整个程序的IODevice崩溃了，这也是为什么我拔插摄像头之后画面又可以了，因为这个画面我让它强制刷新了...也就是说绘制器又被重新生成了一遍...这也是让我非常难理解问题的一个点。

### 怎么解决？

法一、其实非常简单，就是在回调函数那里把直接调用函数改为发送一个信号，让 类内的函数 改为槽函数去接收就可以了。

法二、调用上述介绍的方法，也可以的，跨线程的操作必须调用其内部的跨线程方法，不然可能会出现很多意想不到的错误和崩溃
