---
layout: post
title: 关于Frameless突然不可用的原因及解决方案及鼠标事件的简单应用
categories: 日常踩坑
description: 之前将整个窗体设置成了frameless，但是最终却不可用了，现在找到了问题所在也解决方案
keywords: Qt，技术，实例，frameless，无边框，QMouseEvent，鼠标事件
---

# 关于Frameless突然不可用的原因及解决方案

&emsp;&emsp;之前将整个窗体设置成了frameless，但是最终却不可用了，现在找到了问题所在也解决方案。

&emsp;&emsp;之前的问题是什么呢？之前我在设置frameless窗口属性的时候，是直接设置的centralwidget上的，但是不知道为什么，重启了之后发现了一个问题，就是当执行到ui.centralwidget->setwindowflags(Qt::FramelessHint)的时候
不管怎么样代码都不会执行下去了，而且也显示不到窗口的内容，而且整个外窗口的边框也并未消失。

&emsp;&emsp;当然了，这其实是我的一个疏忽。为什么这么说呢，其实我甚至不知道一开始整个程序是如何按正常情况下运行起来的。首先我们要注意到一点，那就是这个所谓的centralwidget其实只不过是this
指针的一个组件，也就是说真正代表了整个窗口的指针其实是 this 而不是那个centralwidget，所以说 后续对centralwidget的任何设置其实都是在设置this窗口上的一个名叫centralwidget的控件而已，这也是为什么
后续代码不执行的原因：并不是代码不执行，而是执行了，导致整个centralwidget位置偏移找不到了而已。

# 关于鼠标事件

&emsp;&emsp;如果只是单纯地用到了鼠标事件，那么QMouseEvent类就很好用。

&emsp;&emsp;但是需要注意的一点是，QMouseEvent不能和eventFilter混用，否则总会有一方盖过另一方的指令，既然Qt有自带的指令包，如果只是一些比较简单的指令，那么直接用QMouseEvent或者QKeyEvent都可以

&emsp;&emsp;这里就不再赘述在之前无边框窗口中有写到关于如何对frameless窗口进行事件改写达到移动窗口的目的的方法了，具体内容见[一个关于如何将widget变成一个像商用软件那样 不可拖拽大小、没有开启、关闭等按钮的固定窗口](https://leventureqys.github.io//2022/05/13/FrameLesstech/)

&emsp;&emsp;在这里我只写一个我自己写的实例，当鼠标放到控件上之后，按钮出现，鼠标离开，按钮消失

 LBD_VideoMeeting_VisualBroadCast.h

    #include <QMouseEvent>

    void enterEvent(QEvent *);
    void leaveEvent(QEvent *);


   LBD_VideoMeeting_VisualBroadCast.cpp


    void LBD_VideoMeeting_VisualBroadCast::enterEvent(QEvent *) {
      ui.btn_Close->setVisible(true);
      ui.btn_Mini->setVisible(true);
    }

    void LBD_VideoMeeting_VisualBroadCast::leaveEvent(QEvent *) {
      ui.btn_Close->setVisible(false);
      ui.btn_Mini->setVisible(false);
    }
