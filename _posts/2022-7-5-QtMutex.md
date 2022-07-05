---
layout: post
title: Qt多线程开发总览，既然用到了就记录一下
categories: 开发日志
description: 这个description是不是没有用啊，你妈的
keywords: qt,多线程,开发日志,技术
---

# 多线程

## 在LBD_VM_Intercom中使用的一个简单的实例

陶工给的dll需要进行异步操作才可以将视频画面附到窗体上，必须得在画面出现之后才可以附加画面，否则就有可能出现意外bug，所以需要在这个添加画面这里加上一个异步操作。

Qt提供了一个非常简单的异步操作方法，就是可以直接把一个函数单独拎出来放到另外一个线程里面进行计算和操作，然后这个事件的处理就和当前这个事件没有什么关系了（如果有输出，或者返回什么的，还是会有，但是不会因为计算量过大而阻塞主线程，就比如你在主线程里面写一个死循环不停地算，可能ui界面会直接卡死不动，也是有可能的）。

比较简单的方法就是：现在Qt的依赖库中添加一个concurrent，然后在头文件上加上

    #include <QtConcurrent/QtConcurrent>

    using namespace QtConcurrent;
    
这样这个多线程库就算被调用起来了，只需要在使用处如此声明：

    QFuture<void> future = QtConcurrent::run(JoinMeeting, sroom, sperson);
    
这样这个JoinMeeting(sroom,sperson)就算是在另外一个线程里进行的了，这个函数的运行就不会阻塞当前线程里的进程。

# 浅谈多线程

## 一、线程基础

### 1、GUI线程与工作线程．

每个程序启动后拥有的第一个线程称为主线程，即GUI线程。QT中所有的组件类和几个相关的类只能工作在GUI线程，不能工作在次线程，次线程即工作线程，主要负责处理GUI线程卸下的工作。

### 2、数据的同步访问
每个线程都有自己的栈，因此每个线程都要自己的调用历史和本地变量。线程共享相同的地址空间。

## 二、QT多线程简介

QT通过三种形式提供了对线程的支持，分别是平台无关的线程类、线程安全的事件投递、跨线程的信号-槽连接。

QT中线程类包含如下：

QThread 提供了跨平台的多线程解决方案
QThreadStorage 提供逐线程数据存储
QMutex 提供相互排斥的锁，或互斥量
QMutexLocker 是一个辅助类，自动对 QMutex 加锁与解锁
QReadWriterLock 提供了一个可以同时读操作的锁
QReadLocker与QWriteLocker 自动对QReadWriteLock 加锁与解锁
QSemaphore 提供了一个整型信号量，是互斥量的泛化
QWaitCondition 提供了一种方法，使得线程可以在被另外线程唤醒之前一直休眠。

## 三、QThread线程

### 1、QThread线程基础

QThread是Qt线程中有一个公共的抽象类，所有的线程类都是从QThread抽象类中派生的，需要实现QThread中的虚函数run(),通过start()函数来调用run函数。

void run（）函数是线程体函数，用于定义线程的功能。

void start（）函数是启动函数，用于将线程入口地址设置为run函数。

void terminate（）函数用于强制结束线程，不保证数据完整性和资源释放。

QCoreApplication::exec()总是在主线程(执行main()的线程)中被调用，不能从一个QThread中调用。在GUI程序中，主线程也称为GUI线程，是唯一允许执行GUI相关操作的线程。另外，必须在创建一个QThread前创建QApplication(or QCoreApplication)对象。

当线程启动和结束时，QThread会发送信号started()和finished()，可以使用isFinished()和isRunning()来查询线程的状态。

从Qt4.8起，可以释放运行刚刚结束的线程对象，通过连接finished()信号到QObject::deleteLater()槽。
使用wait()来阻塞调用的线程，直到其它线程执行完毕（或者直到指定的时间过去）。

静态函数currentThreadId()和currentThread()返回标识当前正在执行的线程。前者返回线程的ID，后者返回一个线程指针。

要设置线程的名称，可以在启动线程之前调用setObjectName()。如果不调用setObjectName()，线程的名称将是线程对象的运行时类型（QThread子类的类名）。
