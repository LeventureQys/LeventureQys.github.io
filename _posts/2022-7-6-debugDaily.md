---
layout: post
title: Debug日志:如何设置模态窗口、qss中的image丢失、进程自杀、任务日志、命令行中文乱码
description: 讲两个例子，一个是座位更新后，如何将座位信息传递到软件中，二个是教师端如何向学生端发送消息码
categories:  开发日志
keywords: 留档,开发日志,实例,Qt
---

## 1.设置模态窗口

对窗口设定属性如下：

    this->setWindowModality(Qt::WindowModal);
    
注意模态窗口只对父窗口生效，在建立窗口的时候要注意，如果不是指针也可以用setParent方法进行

## 2.qss中的image丢失

不知道为什么，在qss中进行image设置的时候，莫名其妙的图标就会丢失，我看了一下午没感觉到有什么原理上的问题，戴工说的是就是有些设备对小图标的支持有问题？我觉得不是这么回事，具体什么原因我也没找到，不过据说就是QSS界面就是单纯的玄学罢了。

怎么解决的呢？就是不用pushbutton了，改用widget，然后给widget添加上一个eventfilter事件，单独设置一下，反正点击事件的槽函数也是我自己重写的，所以是不是按钮也没有关系，只用稍微转发一下事件就好了。

## 3.进程自杀：

这个是戴工给我的代码。可以更好的结束进程，注销掉所有的资源，避免QApplication::exit()的时候会出一些莫名其妙的超栈bug，这样就需要用一个更好的代码来注销所有的资源。

以下是代码，之后会画个事件单独整理一下所有可重用资源：

    void tApp::KillMySelf()
    {
      QString qsAppName = QString("%1.exe").arg(QCoreApplication::applicationName());
      KillProcessByName(qsAppName);
    }
    void tApp::KillProcessByID(int nID)
    {
      QProcess p;
      QString cmd = QString("taskkill /F /PID %1 /T").arg(QString::number(nID));
      p.execute(cmd);
      p.close();
    }
    void tApp::KillProcessByName(const QString &qsName)
    {
      QString qsConvertName = qsName;
      qsConvertName.replace('/', '\\');
      qsConvertName = qsConvertName.mid(qsConvertName.lastIndexOf('\\') + 1);

      QProcess p;
      QString cmd = QString("taskkill /F /IM %1 /T").arg(qsName);
      p.execute(cmd);
      p.close();
    }

## 4.任务日志：

任务日志也是一个可重用的代码，可以直接在main函数处就直接调用，如果是release模式下就没有输出的debug消息，只会输出消息到txt文件中

需要在main.cpp中声明

    #define QT_MESSAGELOGCONTEXT
    
main函数中调用如下：

    QT_LOG::logInit("errorlog.txt",0);
    
QLog.h的内容:

    #ifndef LOG_H
    #define LOG_H

    #include <QFile>
    #include <QTextStream>
    #include <QDateTime>
    #include <QMutex>

    //选择屏幕打印还是输出到文件可以根据这个宏控制或者控制函数调用位置都可以
    //#define _DEBUG

    //默认调试级别为warning，即小于warning级别的都不会写入日志文件
    //只有release版本的时候，才会输出到日志，debug版本正常输出到终端。
    namespace QT_LOG
    {
      //默认文件名为当前时间命名的log文件
      static int m_LogLevel = 1;
      static QString m_LogFile = QString("%1.log").arg(QDateTime::currentDateTime().toString("yyyyMMddhhmmss"));
      QMutex m_LogMutex;

      void customMessageHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg)
      {
        //设置输出日志级别，小于该级别，将不会写入日志文件，默认是warning级别，即debug信息不会写入日志文件
        if (type < m_LogLevel)
        {
          return;
        }

        QString log_info;
        switch (type)
        {
        case QtDebugMsg:
          log_info = QString("%1[Debug]:").arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
          break;

        case QtWarningMsg:
          log_info = QString("%1[Warning]:").arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
          break;

        case QtCriticalMsg:
          log_info = QString("%1[Critical]:").arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
          break;

        case QtFatalMsg:
          log_info = QString("%1[Fatal]:").arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
          abort();

        case QtInfoMsg:
          log_info = QString("%1[Info]:").arg(QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
          break;
        }
        log_info += QString(context.file) + QString(context.line) + QString("%1").arg(msg);

        //为了线程安全
        m_LogMutex.lock();

        QFile outFile(m_LogFile);
        outFile.open(QIODevice::WriteOnly | QIODevice::Append | QIODevice::Text);
        QTextStream ts(&outFile);
        ts << log_info << endl;
        outFile.close();

        m_LogMutex.unlock();
      }

      //默认调试级别为warning及以上才会写入日志文件，默认log文件名为程序启动时间命名的log文件
      void logInit(QString logFile = "", int logLevel = 1)
      {
    #ifndef _DEBUG  //实现debug版本的时候，输出到终端；release版本的时候输出到日志文件
        if ((logLevel < 0) || (logLevel > 3))
        {
          m_LogLevel = 1;
        }
        else
        {
          m_LogLevel = logLevel;
        }

        if (!logFile.isEmpty())
        {
          m_LogFile = logFile;
        }

        qInstallMessageHandler(customMessageHandler);
    #endif
      }
    }

    #endif // LOG_H

## 5.命令行中文乱码

不知道我的电脑的默认编码格式是出了什么问题，总之就是Qt默认是不可以输出中文的，但是莫名其妙的就是可以，本来命令行传中文是没事的，但是莫名其妙的我的代码传中文就是乱码，可能这边项目做完了周末找个时间来重装以下系统吧，具体原因我也不清楚。

解决方法：加入QString::fromLocal8Bit();
