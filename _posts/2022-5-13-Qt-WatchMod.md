---
layout: post
title: Qt实现全局观察者模式（多层窗体之间直接传递消息）-支持传参
categories: Qt
description: 近来做项目发现，多个窗体之间要通信真的好麻烦，比如：A调出B，B调出C,那么C给A发消息，那就得经过B转发才能实现。对于两三层窗体，这种方法还可以接受，但嵌套太多就有点烦人了。基于这个原因，那么要实现的东西就很清楚了，有一个全局类，去直接绑定信号槽关系，在需要触发的时候，通过这个全局类的函数，去相应的触发一下，就可以实现直连通信了。
keywords: Qt，实例，信号收发，C++
---

# Qt实现全局观察者模式（多层窗体之间直接传递消息）-支持传参

主要参考文章为：[Qt实现全局观察者模式（多层窗体之间直接传递消息）-支持传参](https://blog.csdn.net/q862343646/article/details/79947005)

内容为：

globalObserver.h

  #ifndef GLOBALOBSERVER_H
  #define GLOBALOBSERVER_H

  #include <QObject>
  #include "obesrverApater.h"

  struct relationData
  {
      QString type;
      QObject *reciver;
      obesrverApater *obesrverApater;
  };

  class globalObserver : public QObject
  {
      Q_OBJECT
  public:
      //因为是全局只有一个，所以直接单例模式
      static globalObserver* getGlobalObserver();
      static void release();
      static globalObserver *m_pInst;
      //绑定
      void attach(const QString type, QObject *reciver, const char *method);
      //解绑
      void detach(const QString type, const QObject* reciver);
      //触发
      void notify(const QString type);
  private:
      explicit globalObserver(QObject *parent = 0);
      ~globalObserver();

  private:
      QList<relationData*> m_oRelationList;
  };

  #endif // GLOBALOBSERVER_H


relationData：结构体，保存对应关系；
relationData::type：字符串类型，就相当于信号的唯一标识符
relationData::reciver：信号接收者，保存这个变量主要实在detach的时候去使用。
relationData::obesrverApater;这个类的作用就很重要了，具体看该类的详解。


obesrverApater.h

  #ifndef OBESRVERAPATER_H
  #define OBESRVERAPATER_H

  #include <QObject>
  class obesrverApater;

  //工厂，方便构造对象
  class obesrverApaterFactory
  {
  public:
      static obesrverApaterFactory *getInst();
      static void realese();
      static obesrverApaterFactory* inst;

      obesrverApater* createObesrverApater();

  private:
      obesrverApaterFactory()
      {}
  };

  //中间层，用来连接信号槽
  class obesrverApater : public QObject
  {
      Q_OBJECT
  public:
      explicit obesrverApater(QObject *parent = 0);

  signals:
      void notify();
  };

  #endif // OBESRVERAPATER_H

  
obesrverApater：该类的主要目的是attach的时候，将传进来的槽函数直接绑定到改类的notify信号，因为传进来的槽函数，要想在触发时去掉用拿不到函数名称，所以借助中间层直接绑定，在触发的时候直接去触发中间层的信号，就可达到目的。
obesrverApaterFactory：创建中间层的工厂，方便类创建。

接下来就主要看看具体函数的实现了：

工厂类去创建中间层对象实体
  obesrverApater *obesrverApaterFactory::createObesrverApater()
  {
      return new obesrverApater();
  }

观察者绑定函数实现
  void globalObserver::attach(const QString type, QObject *reciver, const char *method)
  {
      obesrverApater *oA = obesrverApaterFactory::getInst()->createObesrverApater();
      connect(oA, SIGNAL(notify()), reciver, method);
      relationData *data = new relationData();
      data->type = type;
      data->reciver = reciver;
      data->obesrverApater = oA;
      m_oRelationList.append(data);
  }

- 观察者解绑函数实现

  void globalObserver::detach(const QString type, const QObject *reciver)
  {
      QList<relationData*>::iterator iter = m_oRelationList.begin();

      while (iter != m_oRelationList.end())
      {
          if ((*iter)->type.compare(type) == 0 && (*iter)->reciver == reciver)
          {
              relationData *data = *iter;
              m_oRelationList.removeOne((*iter));

              delete data->obesrverApater;
              delete data;
              return;
          }
          iter++;
      }
  }

观察者触发函数实现
  void globalObserver::notify(const QString type)
  {
      QList<relationData*>::iterator iter = m_oRelationList.begin();
      while (iter != m_oRelationList.end())
      {
          if ((*iter)->type.compare(type) == 0)
          {
              emit (*iter)->obesrverApater->notify();
          }
          iter++;
      }
  }

程序结束时别忘了销毁
  globalObserver::~globalObserver()
  {
      //释放列表数据
      QList<relationData*>::iterator iter = m_oRelationList.begin();

      while (iter != m_oRelationList.end())
      {
          delete (*iter)->obesrverApater;
          delete *iter;
          iter++;
      }

  }

测试：

测试代码
  Widget::Widget(QWidget *parent)
      : QWidget(parent)
  {
      globalObserver::getGlobalObserver()->attach("haha", this, SLOT(haha()));
      globalObserver::getGlobalObserver()->attach("hehe", this, SLOT(hehe()));

      QPushButton *p = new QPushButton("haha", this);
      connect(p, SIGNAL(clicked()), this, SLOT(onHaha()));
      p->setGeometry(10, 10, 200, 40);
  }

  Widget::~Widget()
  {
      globalObserver::getGlobalObserver()->detach("haha", this);
      globalObserver::getGlobalObserver()->detach("hehe", this);
  }

  void Widget::haha()
  {
      QMessageBox::about(this, "", "haha");

  }

  void Widget::hehe()
  {
      QMessageBox::about(this, "", "hehe");
  }

  void Widget::onHaha()
  {
      globalObserver::getGlobalObserver()->notify("haha");
  }
