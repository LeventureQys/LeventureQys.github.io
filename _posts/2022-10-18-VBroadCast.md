---
title: 视频广播工具对接文档
categories: 对接文档
description: 视频广播学生端和师生对讲教师端的通信文档
keywords: 开发实例,对接文档
---

# 视频广播工具对接文档

## 视频广播教师端

### 启动项参数：

  //argc = 8
  //char* server_ip 视频服务器ip
  //int server_port 视频服务器端口号
  //char* tcp_ip 教师端ip
  //int tcp_port 教师端端口号 默认5935
  //int main_hwnd 主框架窗口句柄
  //int class_index 教室编号
  //int  lbd_student_hwnd 学生座位窗口句柄（用于确定窗口启动位置，目前暂时无效，传入主框架窗口句柄即可） 
  
### 视频广播发送消息：

视频广播教师端的所有工具都是通过copydate消息发送的

#### 1.启动时会发送的消息

启动的时候会发送一条消息

  VBroadcast|StartVBroadcast|视频广播窗口句柄
  
启动的时候会发送，这条消息给主框架，让主框架记录视频广播的窗口句柄

#### 2.退出时会发送消息

//TODO:这条消息似乎不是一定能接收到，请使用进程监控

进程退出时会发送

  VBroadcast|QuitVBroadcast
  

### 视频广播接收消息：

#### 1.退出视频广播

视频广播接收到这条消息时，会退出进程

PT_Frame|QuitVBroadcast

## 视频广播学生端

### 启动项参数

  //argc = 3
  //1.char* tcp_ip 教师端 ip
  //2.int tcp_port 教师端端口，默认5935
  //3.int main_hwnd 主框架窗体句柄 
  
### 视频广播发送的消息

#### 1.启动的时候会向主框架发送当前窗口句柄
    const ULONG_PTR sVBROADCAST = WM_USER + 5939;
		::SendMessage((HWND)mainHWND, sVBROADCAST, 0, this->winId());

### 视频广播接收的消息

#### 1.视频广播显示、隐藏

视频广播接收到这个消息之后会让当前进程显示或隐藏

  const qint32 msg_framechange = WM_USER + 5935;
  //lParam == 1 视频广播展示
  //lParam == 0 视频广播隐藏
  
