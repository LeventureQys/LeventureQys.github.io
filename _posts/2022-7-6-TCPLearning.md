---
layout: post
title: Qt网络编程-从0到多线程编程
categories: 学习笔记
description: 少点比较，多点谦虚
keywords: 网络编程,Qt,多线程,高级编程
topmost: true
---



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

用到了两个类，都来自Qt自带的网络模块network
