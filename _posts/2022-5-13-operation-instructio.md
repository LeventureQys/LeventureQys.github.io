---
layout: post
title: 大学生通讯社使用官网说明
categories: 说明书
description: 关于如何使用大学生通讯社官网后台
keywords: 说明书 
---

## 关于如何从零开始使用大学生通讯社使用官网说明官网后台的说明

### 写在前面

&emsp;&emsp;本项目基于github page ，是一个比较简单的静态界面，因为我是做c++和c#的，前端这个东西不是很懂，所以很多东西其实我也是一知半解，不过我会尽我所能将整个项目修改到一个最佳状态，以供大家使用。

&emsp;&emsp;另外提一点，就是这个github因为不是部署在国内的网络，所以用起来网络不会很稳定，要有心理准备，如果有vpn的话也可以尝试使用vpn登陆账号和做后台修改，至于这种东西怎么获取，你联系我，如果我有相关的资源我会分享给你的，当然了也不一定。这个页面的控件很多，我只改了其中的一部分，还有一部分可能还留着我的痕迹，如果需要修改的话可以联系到我，或者你自己看得懂这个后台的文件也可以自己尝试修改。

&emsp;&emsp;需要联系我的话，可以加我的QQ:593541465，QQ不一定在，可以联系我的vx:Lenventure，如有需要请说明来意。

### 1.关于排版

&emsp;&emsp;本官网的所有后台文章的排版均基于markdown格式[markdown-百度百科](https://baike.baidu.com/item/markdown/3245829)，对此需要补充的一点是，在markdown格式文档中无法直接对段首进行缩进
所以如果需要对段首进行缩进的话，只能在文章的开头部分输入

![段首缩进字符演示](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@4cc9a86f56ffd2c255447f85db4e6763d7705544/2022/05/13/3acc340de5cee5bdb3170837e4a0d4bd.png)
  
&emsp;&emsp;来输入一个全角的空格，段首缩进两个字符，就是在段首输入两次这个字符组，比如

段首缩进示范：![段首缩进示范](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@548690251f1c90816f0ecb25d57b6a130f63f1dc/2022/05/13/e3465fe1e3914b62d44ab5807cbc8d8c.png) 

段首缩进效果：![段首缩进效果](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@a807aefa8038b5860ef40a026798ecf8cd2256ae/2022/05/13/0590556c494de345608267ebae5df0b3.png)

### 2.从登陆到进入管理后台

&emsp;&emsp;首先，本项目是基于github page的，所以一个基础的github账号，肯定是要有的。这个大通文学部的官方账号我到时候会提供给你们，直接根据提示一步步登陆即可，这个应该没有什么不会的吧？实在不会的可以看

&emsp;&emsp;登陆之后，点击右上角的头像
 
![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@65f7c0d30c276b19cdded6543f35aa61253d6d1f/2022/05/13/c0b5ecf7dd73fe78d0389eceba62a6a9.png)

&emsp;&emsp;点击 your repositories 

&emsp;&emsp;进入到仓库界面 - >

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@e85ad904295dda8c26675056dc9fbfeca204d0d6/2022/05/13/2e348016b5bee9d1ebaead6520a7ae20.png)

&emsp;&emsp;正式版主页这里应该只有两个仓库，其中一个叫DTS_Literature.github.io，另一个叫blogtalk。前者就是整个主页的后台，后者是评论区内容，每个文章都会有对应的评论区内容。

&emsp;&emsp;点击前者DTS_Literature.github.io，即可进入整个管理后台如图所示

&emsp;&emsp;此时应该可以看到当前页面下的内容如此

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@8d6c4448d51f9c8fc32b016d1222e825dbc37561/2022/05/13/853695c1531fa6a387b57b0976516797.png)

&emsp;&emsp;到此处就算成功进入主页管理后台界面了

### 3.如何插入一篇征稿启事，或者文章？

&emsp;&emsp;在整个后台中有非常多的文件，其中涉及到整个界面的ui，和各个界面的内容，但是如果你不懂计算机的话，则只用修改_posts文件夹就好，里面就是文章的内容

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@e72e308869b3f028fa9e4533b14bc3bb90757bb8/2022/05/13/34b95e6aaf856a42f9f31d87ccfc69ee.png)

&emsp;&emsp;点开后，可以看到该网站中的每一篇推送

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@d31b7dd58dfe63c85e24a3c1a1c538061bc19f89/2022/05/13/74ec33eff6f3529fa68237d76f5f6806.png)

&emsp;&emsp;注意这些推送的命名格式 ，一般都是 年-月-日-象征该文章名称的名字，当然这个名字你可以任意命名，但请确保是英文，避免不必要的错误发生，这里的命名和文章的名称无关，只是一个单纯的存储内容的地址而已。

&emsp;&emsp;插入一个新的推送，需要点击右上角的Add File->Create new File

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@612d21b942307631d47444ec1f141b9c10072d30/2022/05/13/c9f87e1e32ef135743a2b52707feb65d.png)

&emsp;&emsp;点击后，进入文章撰写界面，首先要对该文件命名，就按照年-月-日-文件名的形式，注意名称中如果不应该出现空格，和各种各样的特殊字符，都可能造成不必要的错误。

&emsp;&emsp;当然这个名字你可以任意命名，但请确保是 英文***，避免不必要的错误发生。

&emsp;&emsp;这里的命名并不是文章的名称，只是一个单纯的存储内容的地址而已，所以不用纠结。

#### 注意，文章一定要以.md结尾，一定要注意，否则文件是无法被识别的。

&emsp;&emsp;比如2022-5-13-Happy-Weekend.md，2022-5-10-Sad-RainyDay.md这种命名都是合法的

&emsp;&emsp;命名方式如下:

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@113f90f861b55e0358c2fa28f3a19cfeac9f9fe4/2022/05/13/57c09115810e184d7f8d9da9caacf0e2.png)

### 4.开始写一篇推送

&emsp;&emsp;如何写一篇推送呢？

&emsp;&emsp;首先是整个文章抬头的格式，用于规范当前文章的各种信息，可以举个例子如下：

&emsp;&emsp;![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@1886975f45e26594c4882a60ca976fb45d78d5fb/2022/05/13/3b1c19ec1400af5f721caf16106660f4.png)

&emsp;&emsp;layout不用管

&emsp;&emsp;title：标题代表了你这篇推送的名称，比如第xx期征稿启事，xx美文等等

&emsp;&emsp;categories：类别:指的是你这个文章的存放分区在哪里，可以是征稿启示、小说、散文、诗歌等等

&emsp;&emsp;description：描述，用于展示在首页标题下方，用于预览当前页面的主要内容是什么的

&emsp;&emsp;keywords：关键字：用于右方search栏里面用来搜索文章的关键字， 比如小说、郴州河、爱情、天气、日记等等

&emsp;&emsp;然后就可以在下面正式地开始写文章和推送了按照，第一条所给的[markdown-百度百科](https://baike.baidu.com/item/markdown/3245829)格式进行排版即可。

&emsp;&emsp;例如:

&emsp;&emsp;![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@c7e0f89d16b2e71a378c868befcebf57ed1af3aa/2022/05/13/c0c552c1e0b4a5331d77c871d5b15e93.png)

### 5.开启评论区

&emsp;&emsp;因为gittalk控件的关系，这个官网的评论区需要每次使用的时候单独建立一个评论区，具体方法就是点到文章之后，拖到最下方的评论区

![](https://cdn.jsdelivr.net/gh/hnkjdaxzzq/img@8b195967b5ba114f42cdc6319c4d75746f2c1c24/2022/05/13/a418882b4d61ee2cdc3845df392dcbe1.png)

点击使用github登陆，然后登陆你手上的github账号即可，因为网络原因这个可能需要稍微等待一会

如果出现了ERROR:Network Error或者not found，请联系我，我可以上来看看问题

