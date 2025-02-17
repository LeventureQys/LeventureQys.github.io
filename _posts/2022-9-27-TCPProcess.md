---
layout: post
title: Qt网络编程-书接上文，浅谈TCP文件收发，以及心跳包
categories: 学习笔记
description: 少点比较，多点谦虚
keywords: 网络编程,Qt,多线程,高级编程
---

# qt网络编程-书接上文，浅谈文件收发

上文[Qt网络编程-从0到多线程编程](https://leventureqys.github.io//2022/07/06/TCPLearning/)中谈到 在qt中的qtcpsocket通讯的用法，接下来浅谈一下关于tcp通讯的实际应用，当然了由于是浅谈，也不能保证其功能的完整性，所以在此不能保证每一个技术细节都正确。

写在前面，只有tcp是适合于发送文件的，而udp不适合，原因也很简单，因为udp发送的信号是断断续续的，并不能保证客户端一定能收到服务器的所有包，有可能要陷入到无尽的等待中，当然可能较小的文件是可以的，但是光是在脑海中想想这个损耗应该就是不可接受的，故在此不谈udp文件收发的应用，当我想到了，可能又会写一篇。

首先我们来说套接字，也就是socket通讯的这个socket。其实我个人是很不喜欢套接字这个说法的，所谓的socket翻译成套接字这个，其实非常的难以理解，我觉得数据包这个翻译还可以，但是意思还是差点，不过既然如此我们就以数据包的形式来理解tcp就好了。

我们在通信中，可以理解tcp通信为一个数据包，然后直接从服务端发送给客户端，这样就完成了数据的传输。

是这么回事吗？

显然不是的，要考虑的问题很多

第一个，你怎么能保证一次传输数据的完整性？你发出一个包，中途可能遇到很多情况，比如断网，内存出错，或者数组超载等，如果是这样的话，那么接收到的数据就不完整了，那么组装起来的数据就会七扭八歪，失去其原有的含义。

第二个，数据在传输的过程中有没有可能错位？前面的数据传到后面去，或者后面的数据传到前面去？这些都是有可能的

第三个，如果传的是文件，又要怎么保证文件的完整性？文件可以看成是一个很长很长的二进制代码，长到需要用Mb乃至Gb来形容其文本大小

第四个，如果传的是文件，但是实际上传输的文件中是不会带有该文件的信息的，比如名字、后缀、所有者等信息，而是一个二进制的文本，这个文本的信息我们该如何获取呢？

以上这些都是可能在tcp协议中遇到的问题，就以上这些问题，也就构成了tcp实际应用中的一些常见基本构造，封包、心跳包、tcp头等等，接下来就简单聊聊该怎么实现这些功能。

## 1.封包

实际上在早期的cpp程序里面，数组的大小还不像现在现在用的qt那样直接动态的申请长度，而是用多少申请多少，比如我现在这个数组我需要1024个字节，那就只能一次申请1024个字节，少了还好说，剩下的大不了空着，但是如果多了，那就不好意思，直接内存溢出让整个程序崩溃。为了解决这个问题，我们在tcp发送的信息里面会适当地添加上一些指定的信号，以此来指挥接收端。

所以一个tcpsocket的长消息，我们要分为三个部分，分别是头 身 尾

一般头部就存放一些属性，比如包的长度，当前包个数，包的总个数，也可能是长度信息。身体就是内容。尾一般是一个0字符，就像制止符，单纯告诉你这条消息到此为止的。

当然，如果是自己用的包，就可以不用规定这么多，只需要在里面定义一个当前文件的总长度即可，至于多少个包，就可以自己内部规定，我就在内部规定的一个包就是1024个字节。另外因为是本地阻塞地发送tcpsoket（需要写锁实现），而且又是局域网内传输，所以不考虑沾包丢包的情况，当然了，如果是安全保密性要求高的链接，或者是网络通信，那么肯定是要求有沾包丢包的处理的，因为我还没实践，所以不讨论这种问题。

现在我们知道了发送端怎么处理，那么接收端呢？

接收端在创建一个实例来接受封包的时候，需要建立一个结构来存放期望接受的大小和以及实际接受到的大小，每轮接受固定长度，当实际接收到的数据大于等于期望大小时，这样就可以说明我们的一次t cp消息接受完成了，这大概就是tcp通讯的一个流程。

## 2.如何传输文件

解决完前面几个问题，现在来解决后续的问题，如何传输文件的信息呢？

其实也就和传输tcp信息一样，在已经实现了tcp通讯的前提下，我们在总的数据链上，再写一个自己定义的头，来存放一些信息，比如可以用\|符分割，第一段存放xxx，第二段存放xxx，第三段存放xxx。。。以此类推，这样就可以组成一个完整的信息，一个包含了所有需要数据的信息，通过分割的方式来组成一个完整的文件。

这个就是比较简单的理论介绍，那么现在来看看实际上我们的工程该怎么写这样的文件

首先我们准备一个QtTcpBaseHandler类，这个类是我们做封包收发的基础，也是我们做客户端或者服务端的基础，它不需要有什么别的功能，只需要有基础的收发功能就行，也就是能定义头身尾，发送TCP和接收TCP消息

首先我们来定义一个头

    struct MsgHeader
    {
      /*
      头部12字节
      [0] = 4;
      [1] = 'H';
      [2] = 'E';
      [3] = 'A';
      [4] = 'D';
      [5] = 0;
      [6] = 0;
      [7] = 0;
      [8] = 0;
      [9] = 0;
      [10] = 0;
      [11] = 0;
      */
      char gcBaseHeader[12] = { 0 };

      /*
      4字节，长度信息：内容长度+1
      */
      int nMsgBodyLen = 0;

      /*
      预留字节
      */
      char gcReserved[12] = { 0 };
    };
    
头部的话比较简单，就是首先你要定义头的前几个字符，以此为标准，然后后续预留几个字节用来发送别的信息，这里存储的信息是5-10字节合起来代表了一个字节长度信息，最后预留第十二字节是0字符结尾，用以代表头部结束。下面来看发送信息

    void SendTcp(QTcpSocket * pTcpSocket, const QByteArray &bytes)
    {
      /* 消息结构：头 + 内容 + 结尾符0 */
      MsgHeader header;
      header.nMsgBodyLen = bytes.length() + 1;

      QByteArray bytesHeaderInfo((char*)&header, sizeof(MsgHeader));
      pTcpSocket->write(bytesHeaderInfo);

      char *pData = new char[header.nMsgBodyLen];
      memset(pData, 0, header.nMsgBodyLen);
      memcpy_s(pData, header.nMsgBodyLen, bytes.data(), bytes.length());
      for (int i = 0; i < header.nMsgBodyLen; i += 1024)
      {
        pTcpSocket->write(pData + i, qMin(1024, header.nMsgBodyLen - i));
      }

      delete[] pData;
    }

发送信息的话，就是把我们要发送的消息和头部信息组装起来，先做一个pData，这个是我们用来发送数组的一个缓冲区，先把所有的数据读到这个缓冲区内，

    //缓冲区
    memset(pData, 0, header.nMsgBodyLen);
    memcpy_s(pData, header.nMsgBodyLen, bytes.data(), bytes.length());
      
再由QTcpsocket 转手发送出去，每次转发固定长度，像我们这里是固定了它的长度为1024长

    //每次发送1024个字节，当然了如果没有1024个字节了就发剩下的部分就行了。
    for (int i = 0; i < header.nMsgBodyLen; i += 1024)
      {
        pTcpSocket->write(pData + i, qMin(1024, header.nMsgBodyLen - i));
      }

那这边就是发送端，是一个比较简单的结构，那么来看接收端。接收端的话，因为qt的tcpsocket通信是异步的操作，所以非常有可能导致接收包的动作会因为QThread::sleep 或者 调试阻塞等行为导致一些无法预料的异常，从而导致接收到的包发生占包，丢包，错位等情况。之前也说过了，当前这个tcp通信类只是在本地实现的，所以在头部只有一个信息，就是消息总长度。那么在接收端就需要写一个锁，当我们没有读完上一条tcp消息时，下一条消息到来之前需要阻塞（时间非常短，因为一条消息只有1024个字节，对于现在的局域网来说传输起来没有什么苦困难）

首先我们需要一个接收tcp消息的结构体如下：

    typedef struct tagTCPRecvData
    {
      int nExpectSize = 0;	// 期望大小
      int nRecvedLen = 0;		// 已收大小
      QByteArray bytes;

      void Clear()
      {
        nExpectSize = 0;
        nRecvedLen = 0;
        bytes.clear();
      }
    }TCPRecvData;
    
我们通过这个结构体来接收文件，记录当前期望大小和已接受大小，当已收大小大于等于期望大小时，接收行为结束

为了保证每次申请的结构都能智能释放和不重复读包、读包正确，这里使用了智能指针和哈希表

    using SPTCPRecvData = std::shared_ptr<TCPRecvData>;
    QHash<QTcpSocket*, SPTCPRecvData> g_qhsSock2RecvData;
    
一把同步互斥锁：
    QMutex g_mtForQhsSock2RecvData;
    
整个读取tcp消息的函数如下：

    void ReadTCPMsg(QTcpSocket * pTcpSocket, qint64 &nCountRecvedMsg, fun_Notice funNotice)
    {
      QMutexLocker am(&g_mtForQhsSock2RecvData);

      if (!g_qhsSock2RecvData.contains(pTcpSocket))
      {
        SPTCPRecvData spTcpRecvData = std::make_shared<TCPRecvData>();
        g_qhsSock2RecvData.insert(pTcpSocket, spTcpRecvData);
      }
      SPTCPRecvData spTcpRecvData = g_qhsSock2RecvData[pTcpSocket];

      while (pTcpSocket->bytesAvailable() > 0)
      {
        if (0 == spTcpRecvData->nRecvedLen)
        {
          if (pTcpSocket->bytesAvailable() < sizeof(MsgHeader)) return;

          QByteArray bytesHeader = pTcpSocket->read(sizeof(MsgHeader));

          MsgHeader *pHeader = (MsgHeader*)(bytesHeader.data());
          spTcpRecvData->nExpectSize = pHeader->nMsgBodyLen;
        }

        int nBytesAvailable = pTcpSocket->bytesAvailable();
        if (nBytesAvailable > 0)
        {
          int nThisRecv = qMin(nBytesAvailable, spTcpRecvData->nExpectSize - spTcpRecvData->nRecvedLen);
          spTcpRecvData->bytes += pTcpSocket->read(nThisRecv);
          spTcpRecvData->nRecvedLen += nThisRecv;

          // 其实就是等于，加大于号为了保险...
          if (spTcpRecvData->nRecvedLen >= spTcpRecvData->nExpectSize)
          {
            // 通知
            if (nullptr != funNotice) funNotice(spTcpRecvData->bytes);

            // 重置
            spTcpRecvData->Clear();
          }
        }
      }

      nCountRecvedMsg = spTcpRecvData->nRecvedLen;
    }
    
一条锁 QMutexLocker am(&g_mtForQhsSock2RecvData);锁定当前函数，这个 QMutexLocker将保证在销毁前不重复执行当前函数。

后续就是处理具体数据的部分了，就是拆开来慢慢读写的问题，其实既然都能保证数据按队列输入了，接下来也就是考虑意外的问题，这里就没什么好说的了。

那以上这个类就是tcp通讯的收发基础，接下来就是写服务端和客户端两端，也就是应用层。
