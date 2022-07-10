---
layout: post
title: Qt网络编程-从0到多线程编程
categories: 学习笔记
description: 少点比较，多点谦虚
keywords: 网络编程,Qt,多线程,高级编程
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



# Qt多线程开发

## 1.线程类:

就有时候，做一些很卡的时候，有时候进程内就会多的工作就会抢占线程，会导致整个程序非常卡，这部分也是非常有用的，需要了解以下

这里看到一个新的connect写法，也是c++11中的一个新的语法lamda，之前没用过这个函数也没想过会在哪里用，现在这里有一个很好的例子。。

![image](https://user-images.githubusercontent.com/102945300/177787696-720947cc-5189-4ab6-8b5e-e3b3110bf285.png)

在 qt 中使用了多线程，有些事项是需要额外注意的：

默认的线程在Qt中称之为窗口线程，也叫主线程或者GUI，负责窗口事件处理或者窗口控件数据的更新

子线程负责后台的业务逻辑处理，子线程中不能对窗口对象做任何操作，这些事情需要交给窗口线程处理

主线程和子线程之间如果要进行数据的传递，需要使用Qt中的信号槽机制，子线程和主线程之间不能直接交互数据，这是不允许的

1.常用公共函数：

    // QThread 类常用 API
    // 构造函数
    QThread::QThread(QObject *parent = Q_NULLPTR);
    // 判断线程中的任务是不是处理完毕了
    bool QThread::isFinished() const;
    // 判断子线程是不是在执行任务
    bool QThread::isRunning() const;

    // Qt中的线程可以设置优先级
    // 得到当前线程的优先级
    Priority QThread::priority() const;
    //设置线程的优先级
    void QThread::setPriority(Priority priority);
    优先级，更高的优先级强到时间片的概率就更高:
        QThread::IdlePriority         --> 最低的优先级
        QThread::LowestPriority
        QThread::LowPriority
        QThread::NormalPriority
        QThread::HighPriority
        QThread::HighestPriority
        QThread::TimeCriticalPriority --> 最高的优先级
        QThread::InheritPriority      --> 子线程和其父线程的优先级相同, 默认是这个
    // 退出线程, 停止底层的事件循环
    // 退出线程的工作函数
    void QThread::exit(int returnCode = 0);
    // 调用线程退出函数之后, 线程不会马上退出因为当前任务有可能还没有完成, 调回用这个函数是
    // 等待任务完成, 然后退出线程, 一般情况下会在 exit() 后边调用这个函数
    bool QThread::wait(unsigned long time = ULONG_MAX);

2.信号槽函数

    // 和调用 exit() 效果是一样的
    // 代用这个函数之后, 再调用 wait() 函数
    [slot] void QThread::quit();
    // 启动子线程
    [slot] void QThread::start(Priority priority = InheritPriority);
    // 线程退出, 可能是会马上终止线程, 一般情况下不使用这个函数
    [slot] void QThread::terminate();

    // 线程中执行的任务完成了, 发出该信号
    // 任务函数中的处理逻辑执行完毕了
    [signal] void QThread::finished();
    // 开始工作之前发出这个信号, 一般不使用
    [signal] void QThread::started();

3.静态函数

    // 返回一个指向管理当前执行线程的QThread的指针
    [static] QThread *QThread::currentThread();
    // 返回可以在系统上运行的理想线程数 == 和当前电脑的 CPU 核心数相同
    [static] int QThread::idealThreadCount();
    // 线程休眠函数
    [static] void QThread::msleep(unsigned long msecs);	// 单位: 毫秒
    [static] void QThread::sleep(unsigned long secs);	// 单位: 秒
    [static] void QThread::usleep(unsigned long usecs);	// 单位: 微秒

4.任务处理函数：

    // 子线程要处理什么任务, 需要写到 run() 中
    [virtual protected] void QThread::run();
    
这个 run() 是一个虚函数，如果想让创建的子线程执行某个任务，需要写一个子类让其继承 QThread，并且在子类中重写父类的 run() 方法，函数体就是对应的任务处理流程。另外，这个函数是一个受保护的成员函数，不能够在类的外部调用，如果想要让线程执行这个函数中的业务流程，需要通过当前线程对象调用槽函数 start() 启动子线程，当子线程被启动，这个 run() 函数也就在线程内部被调用了。


## 2.多线程使用方式：

方法一： 继承一个QThread类，然后重写虚函数run()方法，然后声明这个类对象，再调用Start方法启动线程。

方法二： 随便写一个QObject类，然后实例化它（千万不能指定父对象），再新建一个线程，再调用这个被实例化的对象的 实例化对象->moveToThread(子线程指针) 这样将这个对象丢到子线程中去运行，然后再让子线程Start就可以启动子线程了，启动子线程之后再调用实例化对象的方法，这样实例化对象的方法就会在子线程中运转起来，这样比较灵活，我们可以把多个子线程移动到子线程中去运行，这都是允许的。

## 3.多线程的销毁：

1.当父对象销毁的时候，子线程自然就会销毁了

2.可以对资源析构掉，当然也可以用信号槽的 方式，或者说我们可以把上述这个父窗口销毁的这个信号槽改写以下，大概就是这样：

![image](https://user-images.githubusercontent.com/102945300/177793308-b8376ec8-73c9-475d-a31f-ab5560a42b13.png)

可以直接delete t1，也可以调用destroy()函数

# Qt线程池的开发

我们使用线程的时候就去创建一个线程，这样实现起来非常简便，但是就会有一个问题：如果并发的线程数量很多，并且每个线程都是执行一个时间很短的任务就结束了，这样频繁创建线程就会大大降低系统的效率，因为频繁创建线程和销毁线程需要时间。

那么有没有一种办法使得线程可以复用，就是执行完一个任务，并不被销毁，而是可以继续执行其他的任务呢？

线程池是一种多线程处理形式，处理过程中将任务添加到队列，然后在创建线程后自动启动这些任务。线程池线程都是后台线程。每个线程都使用默认的堆栈大小，以默认的优先级运行，并处于多线程单元中。如果某个线程在托管代码中空闲（如正在等待某个事件）, 则线程池将插入另一个辅助线程来使所有处理器保持繁忙。如果所有线程池线程都始终保持繁忙，但队列中包含挂起的工作，则线程池将在一段时间后创建另一个辅助线程但线程的数目永远不会超过最大值。超过最大值的线程可以排队，但他们要等到其他线程完成后才启动。

在各个编程语言的语种中都有线程池的概念，并且很多语言中直接提供了线程池，作为程序猿直接使用就可以了，下面给大家介绍一下线程池的实现原理：

![image](https://user-images.githubusercontent.com/102945300/177792863-dcb4df52-f106-448d-9aae-9fc62120b9c6.png)

## QRunnable

在 Qt 中使用线程池需要先创建任务，添加到线程池中的每一个任务都需要是一个 QRunnable 类型，因此在程序中需要创建子类继承 QRunnable 这个类，然后重写 run() 方法，在这个函数中编写要在线程池中执行的任务，并将这个子类对象传递给线程池，这样任务就可以被线程池中的某个工作的线程处理掉了。

QRunnable 类 常用函数不多，主要是设置任务对象传给线程池后，是否需要自动析构。

    // 在子类中必须要重写的函数, 里边是任务的处理流程

    [pure virtual] void QRunnable::run();

    // 参数设置为 true: 这个任务对象在线程池中的线程中处理完毕, 这个任务对象就会自动销毁
    // 参数设置为 false: 这个任务对象在线程池中的线程中处理完毕, 对象需要程序猿手动销毁
    void QRunnable::setAutoDelete(bool autoDelete);
    // 获取当前任务对象的析构方式,返回true->自动析构, 返回false->手动析构
    bool QRunnable::autoDelete() const;

    //注意这里是继承了两个类，如果只继承了QRunnable，可能就没法用信号槽函数了
    class MyWork : public QObject, public QRunnable
    {
        Q_OBJECT
    public:
        explicit MyWork(QObject *parent = nullptr)
        {
            // 任务执行完毕,该对象自动销毁
            setAutoDelete(true);
        }
        ~MyWork();

        void run() override{}
    }

在上面的示例中 MyWork 类是一个多重继承，如果需要在这个任务中使用 Qt 的信号槽机制进行数据的传递就必须继承 QObject 这个类，如果不使用信号槽传递数据就可以不继承了，只继承 QRunnable 即可。

    class MyWork :public QRunnable
    {
        Q_OBJECT
    public:
        explicit MyWork()
        {
            // 任务执行完毕,该对象自动销毁
            setAutoDelete(true);
        }
        ~MyWork();

        void run() override{}
    }

## QThreadPool

有一个全局的线程池实例对象

    // 在每个Qt应用程序中都有一个全局的线程池对象, 通过这个函数直接访问这个对象
    static QThreadPool * QThreadPool::globalInstance();
    
    // 获取和设置线程中的最大线程个数
    int maxThreadCount() const;
    void setMaxThreadCount(int maxThreadCount);

    // 给线程池添加任务, 任务是一个 QRunnable 类型的对象
    // 如果线程池中没有空闲的线程了, 任务会放到任务队列中, 等待线程处理
    void QThreadPool::start(QRunnable * runnable, int priority = 0);
    // 如果线程池中没有空闲的线程了, 直接返回值, 任务添加失败, 任务不会添加到任务队列中
    bool QThreadPool::tryStart(QRunnable * runnable);

    // 线程池中被激活的线程的个数(正在工作的线程个数)
    int QThreadPool::activeThreadCount() const;

    // 尝试性的将某一个任务从线程池的任务队列中删除, 如果任务已经开始执行就无法删除了
    bool QThreadPool::tryTake(QRunnable *runnable);
    // 将线程池中的任务队列里边没有开始处理的所有任务删除, 如果已经开始处理了就无法通过该函数删除了
    void QThreadPool::clear();

