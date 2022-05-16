---
layout: post
title: 在Qt中实现多窗口通信
categories: Qt
description: 之前一直在找关于多窗口通信之间的方案
keywords: 信号收发，理解，实例，Qt,C++
---

# 在Qt中实现多窗口通信

之前一直在找关于多窗口通信之间的方案，因为我现在的项目就是一个广播，然后桌面置顶最上方会有一个提示栏，提示你当前的直播情况，点击广播的头像的最小化按钮后头像消失，title出现，点击title的
展开之后，title消失，头像出现，这显示不可能是通过一ui实现的，肯定至少用到了两个ui，所以之前找了一下这个qt多窗口之间的通信方案，但是很多写的都是所谓父子窗口之间的通信，这明显两个按钮之间
是两个单独的类，那该怎么做呢？

其实在这里要搞清楚qt的ui是怎么运作的

拿这个TitleAbove来举例子：

    class TitleAbove : public QWidget {
      Q_OBJECT

    public:
      TitleAbove(QWidget *parent = Q_NULLPTR);
    private:
      Ui::TitleAbove ui;
    };
    
这个就是我给Title的类，而其中引用的Ui文件也是对应的ui_TitleAbove.h

如果我需要在另一个类LBD_VideoMeeting_VisualBroadCast想要引用并打开这个类该如何实现呢？

只需要在LBD_VideoMeeting_VisualBroadCast.h的LBD_VideoMeeting_VisualBroadCast类中声明一个TitleAbove tta; 令其成为一个子窗口即可，反正两个窗口并不是实质上独立的，而是其中一个关闭，两个窗口一起关闭
而这个步骤可以通过SIGNAl和SLOT来完成。


写一个实例：
.h文件
        #pragma once

        #include <QtWidgets/QMainWindow>
        #include "ui_ConnectionTest.h"
        #include "qdebug.h"
        #include"ui_MainWindow.h"
        class ConnectionTest : public QMainWindow
        {
            Q_OBJECT

        public:

            ConnectionTest(QWidget *parent = Q_NULLPTR);

        private:
            Ui::ConnectionTestClass ui;


        public slots:
            void wirtedebug();
            void on_pushButton_clicked();

        signals:
            void CSignal();

        };

        class MainWindow :public QMainWindow {
            Q_OBJECT

        public:
            MainWindow(QWidget *parent = Q_NULLPTR);
            ConnectionTest *ct = new ConnectionTest();

            public slots:
            void printdebug();
        signals:
            void MSignals();
        private:
            Ui::MainWindow ui;

            private slots:
            void on_pushButton_clicked();


        };
        
.cpp文件 

        #include "ConnectionTest.h"

        ConnectionTest::ConnectionTest(QWidget *parent) : QMainWindow(parent) {
            ui.setupUi(this);
        }

        MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent) {
            ui.setupUi(this);
            ct->show();
            connect(this, SIGNAL(MSignals()), ct, SLOT(wirtedebug()));
            connect(ct, SIGNAL(CSignal()), this, SLOT(printdebug()));
        }
        void MainWindow::printdebug() {
            qDebug() << "MainWindow slot";
        }
        void MainWindow::on_pushButton_clicked() {
            emit MSignals();
        }

        void ConnectionTest::wirtedebug() {

            qDebug() << "Connectiontest slot";
        }

        void ConnectionTest::on_pushButton_clicked()
        {
            emit CSignal();
        }


## 反思

本次开发中出现了四个问题

一、最开始在vs中进行定义的时候并不是定义的指针，而是单纯地定义了一个对象，但是connect函数中并不能引入一个对象，只能引入指针，所以不管怎么引入对象，也找不到对应的信号函数。

二、在写widget的构造函数时，忘记在结尾加上:widget(parent)了。这导致了vs识别不到我这个构造函数是继承类的，而是一个普通的构造函数，这导致了vs无法识别。

三、在实际编写中，即使上述两项都写对了，你在 SIGNAL()的括号中写入信号函数，仍然是不会进行联想，只能你自己去写，然后不报错，仅此而已。

四、发送信号函数signal 和 槽函数 slot 要写对，它联想的 不一定是对的，甚至可能是错的，vs对 qt 的支持 其实不太理想。
