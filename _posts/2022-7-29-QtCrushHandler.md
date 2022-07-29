---
layout: post
title: 在VS中调用基于Google Breakpad的跨平台Qt崩溃异常捕获调用方案
categories: 实例
description: 记录以下
keywords: Qt,崩溃异常处理,跨平台,实例
---

# 方案一、基于Google Breakpad的跨平台Qt崩溃异常捕获调用方案

首先上博客：[Windows下Qt生成dump文件并定位bug（基于qBreakpad）](https://blog.csdn.net/zyhse/article/details/112533333)

这个地方使用的是一个叫qBreakPad的方案，这个之前在网上有过文档，但是文档太老了，不是很看得懂，这里看到个说的比较明白的，故拿来简单介绍一下：

## 1.生成静态库lib文件

首先我们拿到这个qBreakpad工程文件，先构建一下，生成一个我们想要的静态库文件，可能会出现一些bug，在上文提到的博客中有相关的一些解决方案。

这里我们需要获得两个静态库文件，一个是debug版本的，一个是release版本的，其实也可以只获得需要的那个，但是我在这里会上传一个demo，里面有两个静态库文件，具体存放方式如图所示

1.![image](https://user-images.githubusercontent.com/102945300/181666812-d99c3f61-a8f6-4e3c-b7a4-7b985e50517d.png)

2.![image](https://user-images.githubusercontent.com/102945300/181666821-6b58ce2b-6ee3-401c-9a41-7d0a3160cf29.png)

3.include : ![image](https://user-images.githubusercontent.com/102945300/181666836-ac0a24d8-f684-4081-8ca6-109f98be2dd2.png)

4. lib: ![image](https://user-images.githubusercontent.com/102945300/181666857-9b322f8d-96f5-4c46-9704-48e003849126.png)

其中debug和release文件夹中只放了一个根据版本的qBreakpad.lib文件

## 2.添加引用和库

这个就不多说了，在那个vc++里面设置一下就行了，记得这一步还需要在连接器里面添加lib文件的引用，或者直接用pragma，也是可以的

## 3.写代码

直接在main函数里面，添加这么一行

    #include "QBreakpadHandler.h"

    QBreakpadInstance.setDumpPath("crashes"); // 设置生成dump文件路径
    
这样就可以在程序崩溃的时候生成dump文件了

![image](https://user-images.githubusercontent.com/102945300/181667085-2642741d-b2f7-42e3-8ae5-667b65fbf07f.png)


# 方案二，仅限于windows环境下的崩溃捕捉方案，调用更简单

QDump.h

        #pragma once

        //注意下面2个头文件引入的顺序
        #include <windows.h>
        #include <dbghelp.h>

        extern char* g_qsDumpName;

        class QtDumpGenerate
        {
        public:
            QtDumpGenerate();

            void ApplicationCrashHandler(EXCEPTION_POINTERS *pException);
        };

        // dump处理
        // 使用方法： SetUnhandledExceptionFilter((LPTOP_LEVEL_EXCEPTION_FILTER)ApplicationCrashHandler);
        long ApplicationCrashHandler(EXCEPTION_POINTERS *pException);
        
QDump.cpp:

        #include "QDump.h"

        #include <QObject>
        #include <QDir>
        #include <QDateTime>
        #include <QDebug>
        #include <QCoreApplication>

        #pragma comment(lib, "dbghelp.lib")

        char* g_qsDumpName = "";

        QtDumpGenerate::QtDumpGenerate()
        {

        }

        void QtDumpGenerate::ApplicationCrashHandler(EXCEPTION_POINTERS *pException)
        {
            QDateTime current_date_time = QDateTime::currentDateTime();
            QString current_date = current_date_time.toString("yyyyMMdd_hhmmss");
            QString dmpName = QString::fromLocal8Bit(g_qsDumpName);
            QString dmpFileName = QCoreApplication::applicationDirPath() + "/" + dmpName + current_date + ".dmp";
            EXCEPTION_RECORD *record = pException->ExceptionRecord;
            QString errCode(QString::number(record->ExceptionCode, 16));
            QString errAddr(QString::number((uint)record->ExceptionAddress, 16));
            QString errFlag(QString::number(record->ExceptionFlags, 16));
            QString errPara(QString::number(record->NumberParameters, 16));

            qDebug() << "errCode: " << errCode;
            qDebug() << "errAddr: " << errAddr;
            qDebug() << "errFlag: " << errFlag;
            qDebug() << "errPara: " << errPara;

            HANDLE hDumpFile = CreateFile((LPCWSTR)QString(dmpFileName).utf16(), GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

            if (hDumpFile != INVALID_HANDLE_VALUE) {
                MINIDUMP_EXCEPTION_INFORMATION dumpInfo;
                dumpInfo.ExceptionPointers = pException;
                dumpInfo.ThreadId = GetCurrentThreadId();
                dumpInfo.ClientPointers = TRUE;
                MiniDumpWriteDump(GetCurrentProcess(), GetCurrentProcessId(), hDumpFile, MiniDumpNormal, &dumpInfo, NULL, NULL);
                CloseHandle(hDumpFile);
            }
            else {
                qDebug() << "hDumpFile == null";
            }
        }

        long ApplicationCrashHandler(EXCEPTION_POINTERS *pException)
        {
            QtDumpGenerate dmpGenerate;
            dmpGenerate.ApplicationCrashHandler(pException);
            return EXCEPTION_EXECUTE_HANDLER;
        }


main.cpp：

        #include "QCrushHandler.h"
        #include <QtWidgets/QApplication>
        #include "QDump.h"//方案二
        #include "QBreakpadHandler.h"//方案一
        int main(int argc, char *argv[])
        {
            QApplication a(argc, argv);
            //方案二
            QString g_qsDumpName = "LgInteractSmartCompus";
            SetUnhandledExceptionFilter((LPTOP_LEVEL_EXCEPTION_FILTER)ApplicationCrashHandler);
            //方案一
            QBreakpadInstance.setDumpPath("crashes"); // 设置生成dump文件路径
            QCrushHandler w;
            w.show();
            return a.exec();
        }
