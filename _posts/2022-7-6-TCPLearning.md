---
layout: post
title: Qt网络编程-从0到多线程编程
categories: 学习笔记
description: 少点比较，多点谦虚
keywords: 网络编程,Qt,多线程,高级编程
topmost: true
---

# 网络编程开发

## 1.简介

两个协议，一个是TCP协议，一个是UDP协议

先说TCP：

![image](https://user-images.githubusercontent.com/102945300/177563298-ca9c9c9c-d8ea-4aca-8c23-e7ce23ea7110.png)

TCP的话，服务器端需要端口监听，直到有客户端进行连接发送过来请求数据，然后客户端根据请求数据进行应答，之后就算tcp连接建立完成

再说UDP:

UDP的就比较简单：

![image](https://user-images.githubusercontent.com/102945300/177564194-4719b904-8ab0-4fdd-a796-883ece8c2f29.png)

不用太纠结，Qt中已经封装好了，戴工也有一个完整的DEMO,到时候可以上传上来以下这里放个连接:

//

//这里应该有个连接

//

用到了两个类，都来自Qt自带的网络模块network，稍微聊聊API

## 2.网络通信常用的API函数

### 1.公共成员函数

1.

![image](https://user-images.githubusercontent.com/102945300/177777872-26b8c4f7-b91a-4e70-a9b1-d5794692ffe8.png)
得到和客户端建立连接之后用于通信的 QTcpSocket 套接字对象，它是 QTcpServer 的一个子对象，当 QTcpServer 对象析构的时候会自动析构这个子对象，当然也可自己手动析构，建议用完之后自己手动析构这个通信的 QTcpSocket 对象。
  
    //开始监听，绑定ip和端口进行监听，这个QHostAddress 是来自ipv4或者ipv6中的任何一个可用的，而port需要些，默认是随机的端口，一般是必须要绑定的，端口范围0-65535，一般是要大于5000，5000以下默认是系统占用的
    
    bool QTcpServer::listen(const QHostAddress &address = QHostAddress::Any, quint16 port = 0);
    
    // 判断当前对象是否在监听, 是返回true，没有监听返回false
    bool QTcpServer::isListening() const;
    // 如果当前对象正在监听返回监听的服务器地址信息, 否则返回 QHostAddress::Null
    QHostAddress QTcpServer::serverAddress() const;
    // 如果服务器正在侦听连接，则返回服务器的端口; 否则返回0
    quint16 QTcpServer::serverPort() const

    参数：
    address：通过类 QHostAddress 可以封装 IPv4、IPv6 格式的 IP 地址，QHostAddress::Any 表示自动绑定
    port：如果指定为 0 表示随机绑定一个可用端口。
    返回值：绑定成功返回 true，失败返回 false

注意，这里绑定本地网卡，要注意双网卡问题，可以通过找到所有QNetworkInterface的flag属性来判定，不然可能出现一些意想不到的问题。


    QTcpSocket *QTcpServer::nextPendingConnection();
    
阻塞等待客户端发起的连接请求，不推荐在单线程程序中使用，建议使用非阻塞方式处理新连接，即使用信号 newConnection() 。

    bool QTcpServer::waitForNewConnection(int msec = 0, bool *timedOut = Q_NULLPTR);3
    
如果没有客户端连接，这个函数就可以阻塞当前进程，可以定时阻塞多久，：

参数：

msec：指定阻塞的最大时长，单位为毫秒（ms）

timeout：传出参数，如果操作超时 timeout 为 true，没有超时 timeout 为 false，相当于回调函数

[signal] void QTcpServer::acceptError(QAbstractSocket::SocketError socketError);

2.信号

    [signal] void QTcpServer::newConnection();

此信号代表新连接进入：

    [signal] void QTcpServer::acceptError(QAbstractSocket::SocketError socketError);
    
此信号代表连接失败了，会返回错误信息

### 2. QTcpSocket

![image](https://user-images.githubusercontent.com/102945300/177781367-f9c51de6-eba3-40f0-9101-66806d212e2a.png)


1.构造函数

    QTcpSocket::QTcpSocket(QObject *parent = Q_NULLPTR);

2.连接到服务器

    [virtual] void QAbstractSocket::connectToHost(const QString &hostName, quint16 port, OpenMode openMode = ReadWrite, NetworkLayerProtocol protocol = AnyIPProtocol);

    [virtual] void QAbstractSocket::connectToHost(const QHostAddress &address, quint16 port, OpenMode openMode = ReadWrite);

在 Qt 中不管调用读操作函数接收数据，还是调用写函数发送数据，操作的对象都是本地的由 Qt 框架维护的一块内存。因此，调用了发送函数数据不一定会马上被发送到网络中，调用了接收函数也不是直接从网络中接收数据，关于底层的相关操作是不需要使用者来维护的。

3.接收数据

    // 指定可接收的最大字节数 maxSize 的数据到指针 data 指向的内存中
    qint64 QIODevice::read(char *data, qint64 maxSize);
    // 指定可接收的最大字节数 maxSize，返回接收的字符串
    QByteArray QIODevice::read(qint64 maxSize);
    // 将当前可用操作数据全部读出，通过返回值返回读出的字符串
    QByteArray QIODevice::readAll();

4.发送数据

    // 发送指针 data 指向的内存中的 maxSize 个字节的数据
    qint64 QIODevice::write(const char *data, qint64 maxSize);
    // 发送指针 data 指向的内存中的数据，字符串以 \0 作为结束标记
    qint64 QIODevice::write(const char *data);
    // 发送参数指定的字符串
    qint64 QIODevice::write(const QByteArray &byteArray);

5.信号

    //在使用 QTcpSocket 进行套接字通信的过程中，如果该类对象发射出 readyRead() 信号，说明对端发送的数据达到了，之后就可以调用 read 函数接收数据了。
    [signal] void QIODevice::readyRead();
    
    //调用 connectToHost() 函数并成功建立连接之后发出 connected() 信号。
    [signal] void QAbstractSocket::connected();
    
    //在套接字断开连接时发出 disconnected() 信号。
    [signal] void QAbstractSocket::disconnected();
    
    
注意这里IO操作，操作的不是网络上的数据，是接受下来之后，存到内存的数据，缓冲区中的数据，这块需要明确。
    
其实qt中自己封装的这个类，还是蛮简单的，这里上传一个完全写好了的模块：

[LgQtNetwork](https://github.com/LeventureQys/LgQtNetwork)

## 3.通信流程

### 1.服务端

1.创建套接字服务器 QTcpServer 对象

2.通过 QTcpServer 对象设置监听，即：QTcpServer::listen()

3.基于 QTcpServer::newConnection() 信号检测是否有新的客户端连接

4.如果有新的客户端连接调用 QTcpSocket *QTcpServer::nextPendingConnection() 得到通信的套接字对象

5.使用通信的套接字对象 QTcpSocket 和客户端进行通信

示例代码如下：

头文件

    class MainWindow : public QMainWindow
    {
        Q_OBJECT

    public:
        explicit MainWindow(QWidget *parent = 0);
        ~MainWindow();

    private slots:
        void on_startServer_clicked();

        void on_sendMsg_clicked();

    private:
        Ui::MainWindow *ui;
        QTcpServer* m_server;
        QTcpSocket* m_tcp;
    };
    
源文件

    MainWindow::MainWindow(QWidget *parent) :
        QMainWindow(parent),
        ui(new Ui::MainWindow)
    {
        ui->setupUi(this);
        setWindowTitle("TCP - 服务器");
        // 创建 QTcpServer 对象
        m_server = new QTcpServer(this);
        // 检测是否有新的客户端连接
        connect(m_server, &QTcpServer::newConnection, this, [=]()
        {
            m_tcp = m_server->nextPendingConnection();
            ui->record->append("成功和客户端建立了新的连接...");
            m_status->setPixmap(QPixmap(":/connect.png").scaled(20, 20));
            // 检测是否有客户端数据
            connect(m_tcp, &QTcpSocket::readyRead, this, [=]()
            {
                // 接收数据
                QString recvMsg = m_tcp->readAll();
                ui->record->append("客户端Say: " + recvMsg);
            });
            // 客户端断开了连接
            connect(m_tcp, &QTcpSocket::disconnected, this, [=]()
            {
                ui->record->append("客户端已经断开了连接...");
                m_tcp->deleteLater();
                m_status->setPixmap(QPixmap(":/disconnect.png").scaled(20, 20));
            });
        });
    }

    MainWindow::~MainWindow()
    {
        delete ui;
    }

    // 启动服务器端的服务按钮
    void MainWindow::on_startServer_clicked()
    {
        unsigned short port = ui->port->text().toInt();
        // 设置服务器监听
        m_server->listen(QHostAddress::Any, port);
        ui->startServer->setEnabled(false);
    }

    // 点击发送数据按钮
    void MainWindow::on_sendMsg_clicked()
    {
        QString sendMsg = ui->msg->toPlainText();
        m_tcp->write(sendMsg.toUtf8());
        ui->record->append("服务器Say: " + sendMsg);
        ui->msg->clear();
    }
    
### 2客户端：

客户端的通信流程就相对简单了

创建通信的套接字类 QTcpSocket 对象

使用服务器端绑定的 IP 和端口连接服务器 QAbstractSocket::connectToHost()

使用 QTcpSocket 对象和服务器进行通信

客户端的具体源码就不发了，详情可以直接看我之前给的demo，这个是实战中可以用到的demo，或者直接看博客[基于 TCP 的 Qt 网络通信](https://subingwen.cn/qt/socket-tcp/#3-2-2-%E4%BB%A3%E7%A0%81%E7%89%87%E6%AE%B5)




