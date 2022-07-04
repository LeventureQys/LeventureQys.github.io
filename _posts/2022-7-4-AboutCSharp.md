---
layout: post
title: 主框架代码中，关于委托的一些事，开发日志
description: 讲两个例子，一个是座位更新后，如何将座位信息传递到软件中，二个是教师端如何向学生端发送消息码
categories:  开发日志
keywords: 留档,日报,实例
---

# ----- 委托是什么------

其实委托事件很好理解，就当成是c语言中的函数指针或者是回调函数，或者说换种理解方式，信号和槽？触发器和接收器？总之就是一个地方调用了这个函数，那么在另一个地方也会调起《同参数》《同类型》的这么个函数。就目前我学到的，这个就比较接近于信号和槽的关系。

另外由于C#相对自由的类外调用方式，一开始整个代码我看的云里雾里的，但是这两天嗯造看下来，已经大致明白了不少。

比如我们现在做的这个工具，在LBD.IEngTeachV53项目下的ClsTools.cs类中，我们做了两个工具一个叫Intercom，师生对讲，另一个叫Broadcast 视频广播。然后两个工具是这样的，都是先开启教师端，然后再开启学生端。向学生端启动的时候传入教师端的tcp ip 和 tcp port，然后将教师端再将需要的参数补给学生端即可。这只是说个前提，但是不管怎么说，我们只用管一点就是如何在教师端和软件之间互相传递参数。

反正是在本地，那就用WinMessage来传递信号。

包含两个部分：

1.教师端接收exe发送的消息

2.exe接收教师端发送的消息

### 详解：

需要注意的是，这个ClsTools类中有一个专门用来处理本地WinMessage消息的类对象，叫clsWinMessage，其中有很多方法：

在这个对象上我犯了很多错误，这里只讲解正确用法。

1.教师端接收exe发送的消息：

  1>在启动的时候，需要初始化这个对象，这个类中写了一个方法叫InitWinMessage()，调用它就可以了。
  
  2>需要改写InitWinMessage方法，这个方法中需要包含以下几个要素：1.new一下这个成员，否则可能为null 2.添加一个委托如下：
  
    this.clsWinMessage.MessageReceive += new LBD.Frame.Base.Utils.MessageEventHandler(this.WinMessage_MessageReceive);

    this.clsWinMessage.CopyDataMessageReceive += new LBD.Frame.Base.Utils.CopyDataMessageEventHandler(this.WinMessage_CopyDataMessageReceive);

这就是添加了一个委托，当clsWinMessage接到消息MessageReceive和CopyDataMessageReceive，分别会触发ClsTools.cs中的WinMessage_MessageReceive和WinMessage_CopyDataMessageReceive方法，并向其中传值。

注意一点就是这个MessageReceive和CopyDataMessageReceive不同，具体哪里不同我不知道，但是在我现在的这个Qt中的SendMessage的方法，发送的其实是CopyData，和单纯的Message好像又有些不一样，具体的区别我不太了解，之后有机会看下MFC可能就懂了。

  3>添加消息接收。这个clsWinMessage类并不是什么WinMessage消息都可以接收，只能接受部分被声明的消息码，不然整个程序需要相应的消息码太多了会导致卡顿。由上我们可以想到，Message和CopyData并不是一回事，所以添加的消息也不是按照它原本的方式添加的。
  
    this.clsWinMessage.AddMessage(WM_TAKECLASS);

    //上为旧代码，下为新代码

    this.clsWinMessage.AddCopyDataMessage(tINTERCOMSTART);

    this.clsWinMessage.AddCopyDataMessage(tNEWSELECTED);

而教师端接收WinMessage消息，也只能放在这个WinMessage_CopyDataMessageReceive的方法去接受处理，不在Message中去处理

       private void WinMessage_CopyDataMessageReceive(System.Object sender, CopyDataMessage m)
        {
            try
            {
                System.String strData = System.String.Empty;
                System.String strClientOpenIntercom = System.String.Empty;


                if (m.Message == tINTERCOMSTART)
                {
                    
                    strData = m.Data;

                    System.Diagnostics.Trace.WriteLine("InterCome.StartMsg:" + strData);

                    blnIntercomState = true;

                    intIntercomHwnd = int.Parse(strData);

                }else if(m.Message == tNEWSELECTED)
                {
                    strData = m.Data;
                   
                    string[] SelectedSeatArray = strData.Split('|');
                    strClientOpenIntercom = "PT_Frame_OpenIntercom";

                    foreach(string str in SelectedSeatArray)
                    {
                        //将消息发送给每一个Actived目录中的成员即可 
                       this.SendToClientMessage(this,0, strClientOpenIntercom);
                        System.Diagnostics.Trace.WriteLine("SelectedSeatArray:"+str);
                    }
                   

                }



            }

            catch (System.Exception err)
            {
                WriteErrorMessage("WinMessage_CopyDataMessageReceive:" + err.Message);
            }
        }


  4>接收消息的句柄

即使注意到上述的问题所在，但是仍有个问题，那就是传入的句柄。需要注意的是这个clsWinMessage类是完全独立的，也就是说它接收消息码其实是有一个自己的隐形窗体在进行，而不是通过整个软件的母窗体来进行，这也是我们需要注意的一点，这个一开始我没注意到

    this.InitWinMessage();

    if (this.clsWinMessage != null)
    {
        intHandle = this.clsWinMessage.WinHandle;
    }
    
可以看上述代码，每次启动这个软件的时候就会Init一个 winmessage，当我们关闭的时候也应该要将其Dispose掉（暂时没做，之后会考虑），也就是说每次启动关闭软件的时候，传入的句柄都是可能不同的，和当前的母窗体并没有什么大关系。

2.exe接收框架端的消息

到这里了其实就简单了，向软件发送消息，其实就是直接调用WMUser的SendCopyDataMessage方法直接发送就可以了，不需要别的，就是在这里其实不需要额外声明编码格式，之前我声明的是unicode，但是这样传过来的参数反而是乱码了，是真的傻逼

## 关于如何将座位更新

现在我们假设我们可以在主框架中将所有的学生座位信息打包好，然后在软件中也提供了根据用户座位信息刷新的接口---

那么这个时候问题来了，我们怎么知道用户的状态更新？

这时候就要用到委托：

