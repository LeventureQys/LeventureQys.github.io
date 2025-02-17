--- 
title: 三套无边框窗体的方案：可按比例拖拽窗体大小的无边框窗口和几个常见的无边框实例
description: 可按比例拖拽窗体大小的无边框窗口实例，开发实例
categories: 开发日志
keywords: 实例,C#,开发日志
--- 

# 一、可按比例拖拽窗体大小的无边框窗口

前几天接到一个需求，就是视频广播的窗体画面要可以拖拽，修改成了可以拖拽全屏的窗口之后，又有一个问题：视频画面也被拉伸了。

由于视频画面是有比例的，所以我们最好也能保证窗口画面也保持一定的比例，所以这里我就改了一下之前的无边框窗口方案如下：

优点：改造过的无边框方案，可以让无边框的窗体变换大小的时候保持一定比例，保证窗体中的画面不变形

缺点：1.不够自由，不能自由拖动 

2.如果拖动的是左边，因为拖动事件实际上是先变换大小后修改坐标，那么右边就会有明显抖动 

3.因为要检测当前的鼠标状态，所以是挺浪费系统资源的，较差的机型上可能会有一些意想不到的问题。

.h文件下：

    enum {
        TOPLEFT = 11,
        TOP = 12,
        TOPRIGHT = 13,
        LEFT = 21,
        CENTER = 22,
        RIGHT = 23,
        BUTTOMLEFT = 31,
        BUTTOM = 32,
        BUTTOMRIGHT = 33
      };
    #define FRAMESHAPE 15  
    const double default_rate = 4.00 / 3.00; //画面比例参数
    public:
      int CalCursorCol(QPoint pt);    //计算鼠标X的位置 
      int CalCursorPos(QPoint pt, int colPos);    //计算鼠标的位置
      void setCursorShape(int CalPos);    //设置鼠标对应位置的形状
    protected:
      void mouseMoveEvent(QMouseEvent *event);
      void mousePressEvent(QMouseEvent *event);
      void mouseReleaseEvent(QMouseEvent *event);
    private:
      int     m_iCalCursorPos;
      bool    m_bLeftPress;
      QRect   m_rtPreGeometry;
      QPoint  m_ptViewMousePos;
  
  .cpp文件：
  
    //注，要在构造函数写上setMouseTracking(true)，要从表面的控件->控件的父控件 ->...->this都要写上
    void Mengban::mouseMoveEvent(QMouseEvent * event)
    {
      //窗体不是最大的话就改变鼠标的形状
      if (Qt::WindowMaximized != windowState())
      {
        setCursorShape(CalCursorPos(event->pos(), CalCursorCol(event->pos())));
      }
      //获取当前的点，这个点是全局的
      QPoint ptCurrentPos = QCursor::pos();
      //计算出移动的位置，当前点 - 鼠标左键按下的点
      QPoint ptMoveSize = ptCurrentPos - m_ptViewMousePos;
      QRect rtTempGeometry = m_rtPreGeometry;
      if (m_bLeftPress)
      {
        switch (m_iCalCursorPos)
        {
        //case TOPLEFT:
        //	rtTempGeometry.setTopLeft(m_rtPreGeometry.topLeft() + ptMoveSize);
        //	break;
        case TOP:
          rtTempGeometry.setTop(m_rtPreGeometry.top() + ptMoveSize.y());
          rtTempGeometry.setRight(this->x() + this->height() * default_rate);
          break;
        //case TOPRIGHT:
        //	rtTempGeometry.setTopRight(m_rtPreGeometry.topRight() + ptMoveSize);
        //	break;
        case LEFT:
          rtTempGeometry.setLeft(m_rtPreGeometry.left() + ptMoveSize.x());
          rtTempGeometry.setTop(this->y() - this->width() / default_rate + this->height());
          break;
        case RIGHT:
          rtTempGeometry.setRight(m_rtPreGeometry.right() + ptMoveSize.x());
          rtTempGeometry.setBottom(this->y() + this->width() / default_rate);
          break;
        //case BUTTOMLEFT:
        //	rtTempGeometry.setBottomLeft(m_rtPreGeometry.bottomLeft() + ptMoveSize);
        //	break;
        case BUTTOM:
          rtTempGeometry.setBottom(m_rtPreGeometry.bottom() + ptMoveSize.y());
          rtTempGeometry.setLeft(this->x() - this->height() * default_rate+this->width());
          break;
        //case BUTTOMRIGHT:
        //	rtTempGeometry.setBottomRight(m_rtPreGeometry.bottomRight() + ptMoveSize);
        //	break;
        case CENTER:
          rtTempGeometry.moveTo(rtTempGeometry.x() + ptMoveSize.x(), rtTempGeometry.y() + ptMoveSize.y());
        default:
          break;
        }
        //移动窗体，如果比最小窗体大，就移动
        if (rtTempGeometry.width() >= 360 && rtTempGeometry.height() >= 270)
          setGeometry(rtTempGeometry);

      }
    }

    void Mengban::mousePressEvent(QMouseEvent * event)
    {
      m_iCalCursorPos = CalCursorPos(event->pos(), CalCursorCol(event->pos()));
      if (event->button() == Qt::LeftButton /*&& Qt::WindowMaximized != windowState()*/)
      {
        //if (m_iCalCursorPos != CENTER)
        //{
          m_bLeftPress = true;
        //}
      }
      m_rtPreGeometry = geometry();
      m_ptViewMousePos = event->globalPos();
    }

    void Mengban::mouseReleaseEvent(QMouseEvent * event)
    {
      m_bLeftPress = false;
      QApplication::restoreOverrideCursor();
    }

    int Mengban::CalCursorCol(QPoint pt)
    {
      return (pt.x() < FRAMESHAPE ? 1 : ((pt.x() > this->width() - FRAMESHAPE) ? 3 : 2));
    }

    int Mengban::CalCursorPos(QPoint pt, int colPos)
    {
      return ((pt.y() < FRAMESHAPE ? 10 : ((pt.y() > this->height() - FRAMESHAPE) ? 30 : 20)) + colPos);
    }

    void Mengban::setCursorShape(int CalPos)
    {
      Qt::CursorShape cursor;
      switch (CalPos)
      {
      //case TOPLEFT:
      //case BUTTOMRIGHT:
      //	cursor = Qt::SizeFDiagCursor;
      //	break;
      //case TOPRIGHT:
      //case BUTTOMLEFT:
      //	cursor = Qt::SizeBDiagCursor;
      //	break;
      case TOP:
      case BUTTOM:
        cursor = Qt::SizeVerCursor;
        break;
      case LEFT:
      case RIGHT:
        cursor = Qt::SizeHorCursor;
        break;
      default:
        cursor = Qt::ArrowCursor;
        break;
      }
      //qDebug() << "fresh!!";
      //qDebug() << "current cursor" << cursor;
      this->setCursor(cursor);

    }
   
# 二、可拖拽大小的windows系统方案：
  
  这个方案拖拽窗体大小是通过系统api实现的，具体怎么实现的我也不是很清楚，之后有时间系统看一下windows高级编程再回来聊聊这个技术点。这里只谈优缺点
  
  优点:
  
  1.windows自带api，效率更高，消耗资源更少
  
  2.没有限制，自由拖拽大小（当然了，窗体会受到最大最小窗口大小的限制）
  
  3.代码简单，分析方便
  
  缺点：
  
  1.不可修改，这部分就像个黑盒，native只是告诉你现在修改的时候那个地方是锚点，仅此而已，基本上没法修改，当然了，我什么都不知道 :<
  
  2.因为是windows的api，所以该功能仅限windows平台
  
      #ifndef MBASEWIDGET_H

      #define MBASEWIDGET_H



      #include <QtWidgets/QWidget>

      #include "windows.h"



      class MBaseWidget : public QWidget

      {

          Q_OBJECT



      public:

          MBaseWidget(QWidget *parent);

          ~MBaseWidget();

          void setMarginWidth(const int &);           //设置鼠标可以在界面边缘多大范围内拖动改变界面大小

          void serResizable(bool);                    //设置是否可以拖动改变大小



      protected:

          bool nativeEvent(const QByteArray & eventType, void * message, long * result);


      private:

          int m_iMarginWidth;

          bool m_bCanResize;

      };



      #endif // MBASEWIDGET_H

      #include "MBaseWidget.h"

      #include "windowsx.h"



      MBaseWidget::MBaseWidget(QWidget *parent)

          : QWidget(parent)

      {

          m_iMarginWidth = 3;
          m_bCanResize = true;
          setWindowFlags(Qt::FramelessWindowHint);

      }


      MBaseWidget::~MBaseWidget()

      {
      }



      void MBaseWidget::setMarginWidth(const int &iWidth)

      {

          m_iMarginWidth = iWidth;

      }

      void MBaseWidget::serResizable(bool bCanResize)

      {

          m_bCanResize = bCanResize;

      }

      bool MBaseWidget::nativeEvent(const QByteArray &eventType, void *message, long *result)
      {
          if (!m_bCanResize)
          {
              return QWidget::nativeEvent(eventType,message,result);
          }

          MSG* msg = (MSG*)message;
          switch(msg->message)
              {
              case WM_NCHITTEST:

                  int xPos = GET_X_LPARAM(msg->lParam) - this->frameGeometry().x();
                  int yPos = GET_Y_LPARAM(msg->lParam) - this->frameGeometry().y();
                  if(xPos < m_iMarginWidth && yPos<m_iMarginWidth)                    //左上角
                      *result = HTTOPLEFT;
                  else if(xPos>=width()-m_iMarginWidth&&yPos<m_iMarginWidth)          //右上角
                      *result = HTTOPRIGHT;
                  else if(xPos<m_iMarginWidth&&yPos>=height()-m_iMarginWidth)         //左下角
                      *result = HTBOTTOMLEFT;
                  else if(xPos>=width()-m_iMarginWidth&&yPos>=height()-m_iMarginWidth)//右下角
                      *result = HTBOTTOMRIGHT;
                  else if(xPos < m_iMarginWidth)                                     //左边
                      *result =  HTLEFT;
                  else if(xPos>=width()-m_iMarginWidth)                              //右边
                      *result = HTRIGHT;
                  else if(yPos<m_iMarginWidth)                                       //上边
                      *result = HTTOP;
                  else if(yPos>=height()-m_iMarginWidth)                             //下边
                      *result = HTBOTTOM;
                  else              //其他部分不做处理，返回false，留给其他事件处理器处理
                     return false;
                  return true;
              }
              return false;         //此处返回false，留给其他事件处理器处理

      }
      
# 三、之前用的老的frameless方案：
  
  最开始在网上找的frameless的方案，没什么好说的，详情见[一个关于如何将widget变成一个像商用软件那样 不可拖拽大小、没有开启、关闭等按钮的固定窗口](https://leventureqys.github.io//2022/05/13/FrameLesstech/)
  
  讲道理，我发现莫名其妙的其实在这里就包含了前两种写法，但是我莫名其妙地一点都没用过。所以说抄代码也要看源码啊
  
  内容如下：

在程序中定义Padding 为2，并同时定义枚举类型。

        #define PADDING 2
        enum Direction { UP=0, DOWN=1, LEFT, RIGHT, LEFTTOP, LEFTBOTTOM, RIGHTBOTTOM, RIGHTTOP, NONE };
        
在.cpp中设置当前窗口

        this->setWindowFlags(Qt::FramelessWindowHint);                //取消标题栏
        // 去掉标题栏,去掉工具栏，窗口置顶
        setWindowFlags(Qt::FramelessWindowHint | Qt::Tool | Qt::WindowStaysOnTopHint);
        setWindowOpacity(0.7); //设置窗体透明度
        重写mouseMoveEvent,mousePressEvent,mouseReleaseEvent

MainWindow.h

        public:
            void region(const QPoint &currentGlobalPoint);  //鼠标的位置,改变光标
        protected:
            //鼠标按下移动及释放事件
            void mousePressEvent(QMouseEvent *event);
            void mouseMoveEvent(QMouseEvent *event);
            void mouseReleaseEvent(QMouseEvent *event);

        private:
            QPoint m_movePoint;  //鼠标的位置
            bool isLeftPressDown;  // 判断左键是否按下
            Direction dir;        // 窗口大小改变时，记录改变方向
MainWindow.cpp

    void MainWindow::region(const QPoint &currentGlobalPoint)
    {
      // 获取窗体在屏幕上的位置区域，topLeft为坐上角点，rightButton为右下角点
      QRect rect = this->rect();

      QPoint topLeft = this->mapToGlobal(rect.topLeft()); //将左上角的(0,0)转化为全局坐标
      QPoint rightButton = this->mapToGlobal(rect.bottomRight());

      int x = currentGlobalPoint.x(); //当前鼠标的坐标
      int y = currentGlobalPoint.y();

      if(((topLeft.x() + PADDING >= x) && (topLeft.x() <= x))
              && ((topLeft.y() + PADDING >= y) && (topLeft.y() <= y)))
      {
          // 左上角
          dir = LEFTTOP;
          this->setCursor(QCursor(Qt::SizeFDiagCursor));  // 设置光标形状
      }else if(((x >= rightButton.x() - PADDING) && (x <= rightButton.x()))
                && ((y >= rightButton.y() - PADDING) && (y <= rightButton.y())))
      {
          // 右下角
          dir = RIGHTBOTTOM;
          this->setCursor(QCursor(Qt::SizeFDiagCursor));
      }else if(((x <= topLeft.x() + PADDING) && (x >= topLeft.x()))
                && ((y >= rightButton.y() - PADDING) && (y <= rightButton.y())))
      {
          //左下角
          dir = LEFTBOTTOM;
          this->setCursor(QCursor(Qt::SizeBDiagCursor));
      }else if(((x <= rightButton.x()) && (x >= rightButton.x() - PADDING))
                && ((y >= topLeft.y()) && (y <= topLeft.y() + PADDING)))
      {
          // 右上角
          dir = RIGHTTOP;
          this->setCursor(QCursor(Qt::SizeBDiagCursor));
      }else if((x <= topLeft.x() + PADDING) && (x >= topLeft.x()))
      {
          // 左边
          dir = LEFT;
          this->setCursor(QCursor(Qt::SizeHorCursor));
      }else if((x <= rightButton.x()) && (x >= rightButton.x() - PADDING))
      {
          // 右边
          dir = RIGHT;
          this->setCursor(QCursor(Qt::SizeHorCursor));
      }else if((y >= topLeft.y()) && (y <= topLeft.y() + PADDING))
      {
          // 上边
          dir = UP;
          this->setCursor(QCursor(Qt::SizeVerCursor));
      }else if((y <= rightButton.y()) && (y >= rightButton.y() - PADDING))
      {
          // 下边
          dir = DOWN;
          this->setCursor(QCursor(Qt::SizeVerCursor));
      }else
      {
          // 默认
          dir = NONE;
          this->setCursor(QCursor(Qt::ArrowCursor));
      }   }
    //三个鼠标事件的重写 //鼠标按下事件

      void MainWindow::mousePressEvent(QMouseEvent *event)
      {
      switch(event->button())
      {
          case Qt::LeftButton:
              isLeftPressDown = true;

              if(dir != NONE)
              {
                  this->mouseGrabber(); //返回当前抓取鼠标输入的窗口
              }
              else
              {
                  m_movePoint = event->globalPos() - this->frameGeometry().topLeft();
                  //globalPos()鼠标位置，topLeft()窗口左上角的位置
              }
              break;
          case Qt::RightButton:
              this->setWindowState(Qt::WindowMinimized);
              break;
          default:
              MainWindow::mousePressEvent(event);
      }   }
    //鼠标移动事件 void MainWindow::mouseMoveEvent(QMouseEvent *event) { QPoint globalPoint = event->globalPos(); //鼠标全局坐标

      QRect rect = this->rect();  //rect == QRect(0,0 1280x720)
      QPoint topLeft = mapToGlobal(rect.topLeft());
      QPoint bottomRight = mapToGlobal(rect.bottomRight());

      if (this->windowState() != Qt::WindowMaximized)
      {
          if(!isLeftPressDown)  //没有按下左键时
          {
              this->region(globalPoint); //窗口大小的改变——判断鼠标位置，改变光标形状
          }
          else
          {
              if(dir != NONE)
              {
                  QRect newRect(topLeft, bottomRight); //定义一个矩形  拖动后最大1000*1618

                  switch(dir)
                  {
                      case LEFT:

                          if(bottomRight.x() - globalPoint.x() <= this->minimumWidth())
                          {
                              newRect.setLeft(topLeft.x());  //小于界面的最小宽度时，设置为左上角横坐标为窗口x
                              //只改变左边界
                          }
                          else
                          {
                              newRect.setLeft(globalPoint.x());
                          }
                          break;
                      case RIGHT:
                          newRect.setWidth(globalPoint.x() - topLeft.x());  //只能改变右边界
                          break;
                      case UP:
                          if(bottomRight.y() - globalPoint.y() <= this->minimumHeight())
                          {
                              newRect.setY(topLeft.y());
                          }
                          else
                          {
                              newRect.setY(globalPoint.y());
                          }
                          break;
                      case DOWN:
                          newRect.setHeight(globalPoint.y() - topLeft.y());
                          break;
                      case LEFTTOP:
                          if(bottomRight.x() - globalPoint.x() <= this->minimumWidth())
                          {
                              newRect.setX(topLeft.x());
                          }
                          else
                          {
                              newRect.setX(globalPoint.x());
                          }

                          if(bottomRight.y() - globalPoint.y() <= this->minimumHeight())
                          {
                              newRect.setY(topLeft.y());
                          }
                          else
                          {
                              newRect.setY(globalPoint.y());
                          }
                          break;
                       case RIGHTTOP:
                            if (globalPoint.x() - topLeft.x() >= this->minimumWidth())
                            {
                                newRect.setWidth(globalPoint.x() - topLeft.x());
                            }
                            else
                            {
                                newRect.setWidth(bottomRight.x() - topLeft.x());
                            }
                            if (bottomRight.y() - globalPoint.y() >= this->minimumHeight())
                            {
                                newRect.setY(globalPoint.y());
                            }
                            else
                            {
                                newRect.setY(topLeft.y());
                            }
                            break;
                       case LEFTBOTTOM:
                            if (bottomRight.x() - globalPoint.x() >= this->minimumWidth())
                            {
                                newRect.setX(globalPoint.x());
                            }
                            else
                            {
                                newRect.setX(topLeft.x());
                            }
                            if (globalPoint.y() - topLeft.y() >= this->minimumHeight())
                            {
                                newRect.setHeight(globalPoint.y() - topLeft.y());
                            }
                            else
                            {
                                newRect.setHeight(bottomRight.y() - topLeft.y());
                            }
                            break;
                        case RIGHTBOTTOM:
                            newRect.setWidth(globalPoint.x() - topLeft.x());
                            newRect.setHeight(globalPoint.y() - topLeft.y());
                            break;
                        default:
                            break;
                  }
                  this->setGeometry(newRect);
              }
              else
              {
                  move(event->globalPos() - m_movePoint); //移动窗口
                  event->accept();
              }
          }
      }   }


    //鼠标释放事件

    void MainWindow::mouseReleaseEvent(QMouseEvent *event)
    {
      if (event->button() == Qt::LeftButton)
      {
          isLeftPressDown = false;
          if (dir != NONE)
          {
              this->releaseMouse(); //释放鼠标抓取
              this->setCursor(QCursor(Qt::ArrowCursor));
              dir = NONE; //热心网友指正
          }
      }   }
法2： 重写nativeEvent事件： MainWindow.h

        protected:
            bool nativeEvent(const QByteArray &eventType, void *message, long *result);
MainWindow.cpp

        bool MainWindow::nativeEvent(const QByteArray &eventType, void *message, long *result)
        {
            MSG* msg = (MSG*)message;
            switch(msg->message)
            {
            case WM_NCHITTEST:
                int xPos = GET_X_LPARAM(msg->lParam) - this->frameGeometry().x();
                int yPos = GET_Y_LPARAM(msg->lParam) - this->frameGeometry().y();
                if(this->childAt(xPos,yPos) == 0)
                {
                    *result = HTCAPTION;
                }else{
                    return false;
                }
                if(xPos > 0 && xPos < 8)
                    *result = HTLEFT;
                if(xPos > (this->width() - 8) && xPos < (this->width() - 0))
                    *result = HTRIGHT;
                if(yPos > 0 && yPos < 8)
                    *result = HTTOP;
                if(yPos > (this->height() - 8) && yPos < (this->height() - 0))
                    *result = HTBOTTOM;
                if(xPos > 18 && xPos < 22 && yPos > 18 && yPos < 22)
                    *result = HTTOPLEFT;
                if(xPos > (this->width() - 22) && xPos < (this->width() - 18) && yPos > 18 && yPos < 22)
                    *result = HTTOPRIGHT;
                if(xPos > 18 && xPos < 22 && yPos > (this->height() - 22) && yPos < (this->height() - 18))
                    *result = HTBOTTOMLEFT;
                if(xPos > (this->width() - 22) && xPos < (this->width() - 18) && yPos > (this->height() - 22) && yPos < (this->height() - 18))
                    *result = HTBOTTOMRIGHT;
                return true;
            }
            return false;
        }

