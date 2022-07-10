---
layout: post
title: C++基础语法学习：STL
categories: 学习笔记
description: 少点比较，多点谦虚
keywords: 基础语法,C++,STL
---

# 基础语法学习，少点比较，多些谦虚

## 1.容器：

常见的容器有以下几类：

1.vector:向量

2.deque:双端队列

3.list：列表

4.set：集合

5：multiset：多重集合

6.map:映射

7：multimap：多重映射

## 2.迭代器：

迭代器的话，其实可以简单点理解就是一个指向容器内部的指针，比如我们现在伸出一根指针i，它可以进行任意的前后移动，同时我们可以取到指针i对应的内容，这就是迭代器，然后我们实际上操作这些容器，就是在操作迭代器。

声明方式有很多，比如s.begin()和s.end(),

容器类名::iterator  迭代器名等

当然了iterator前面还可以加一些限定符，比如const_iterator代表获得的是常量迭代器，reverse_iterator获得反向迭代器，const_reverse_iterator获得常量反向迭代器

声明迭代器需要头文件<iterator>
  
## 3.函数对象

如果一个类将()运算符重载为成员函数，这个类就称为函数对象类，这个类的对象就是函数对象。函数对象是一个对象，但是使用的形式看起来像函数调用，实际上也执行了函数调用，因而得名。
  
就是，函数对象其实也就是一个类，不过在指定的操作符函数里对某个数据进行了处理，然后得到一个另外的数据类型，这样操作起来就好像是在进行了函数操作一样，目前不知道这样做有什么含义
  
      public:
        double operator()(int a1, int a2, int a3)
        {  //重载()运算符
            return (double)(a1 + a2 + a3) / 3;
        }
    };
  
## 4.算法
  
  这个就不多说了，就是一些STL中自带的方法，比如取平均数，比大小什么的，这个就不用过多赘述了
  
  STL中的算法需要包含头文件
  
  <algorithm>
  
## 5.vector中的属性和方法
    
### 1.构造方法
    vector():创建一个空vector
    vector(int nSize):创建一个vector,元素个数为nSize
    vector(int nSize,const t& t)​:创建一个vector，元素个数为nSize,且值均为t
    vector(const vector&):复制构造函数
    vector(begin,end):复制[begin,end)区间内另一个数组的元素到vector中
 
### 2.增加函数
    
    ​void push_back(const T& x)​:向量尾部增加一个元素X
    ​iterator insert(iterator it,const T& x)​:向量中迭代器指向元素前增加一个元素x
    ​iterator insert(iterator it,int n,const T& x)​:向量中迭代器指向元素前增加n个相同的元素x
    ​iterator insert(iterator it,const_iterator first,const_iterator last)​:向量中迭代器指向元素前插入另一个相同类型向量的[first,last)间的数据
    
### 3.删除函数
    
    ​iiterator erase(iterator it)​:删除向量中迭代器指向元素
    ​iterator erase(iterator first,iterator last)​:删除向量中[first,last)中元素
    ​void pop_back()​:删除向量中最后一个元素
    ​void clear()​:清空向量中所有元素
    
### 4.遍历函数
    
    ​reference at(int pos)​:返回pos位置元素的引用
    ​reference front()​:返回首元素的引用
    ​reference back()​:返回尾元素的引用
    ​iterator begin()​:返回向量头指针，指向第一个元素
    ​iterator end()​:返回向量尾指针，指向向量最后一个元素的下一个位置
    ​reverse_iterator rbegin()​:反向迭代器，指向最后一个元素
    ​reverse_iterator rend()​:反向迭代器，指向第一个元素之前的位置
    
### 5.判断函数
    
    ​bool empty() const​:判断向量是否为空，若为空，则向量中无元素
    ​int size() const​:返回向量中元素的个数
    ​int capacity() const​:返回当前向量所能容纳的最大元素值
    ​int max_size() const​:返回最大可允许的 vector 元素数量值
    
### 6.其他函数
    
    ​void swap(vector&)​:交换两个同类型向量的数据
    ​void assign(int n,const T& x)​:设置向量中前n个元素的值为x
    ​void assign(const_iterator first,const_iterator last)​:向量中[first,last)中元素设置成当前向量元素
    
### 7.常见方法
    
    push_back 在数组的最后添加一个数据
    pop_back 去掉数组的最后一个数据
    at 得到编号位置的数据
    begin 得到数组头的指针
    end 得到数组的最后一个单元+1的指针
    front 得到数组头的引用
    back 得到数组的最后一个单元的引用
    max_size 得到vector最大可以是多大
    capacity 当前vector分配的大小
    size 当前使用数据的大小
    resize 改变当前使用数据的大小，如果它比当前使用的大，者填充默认值
    reserve 改变当前vecotr所分配空间的大小
    erase 删除指针指向的数据项
    clear 清空当前的vector
    rbegin 将vector反转后的开始指针返回(其实就是原来的end-1)
    rend 将vector反转构的结束指针返回(其实就是原来的begin-1)
    empty 判断vector是否为空
    swap 与另一个vector交换数据

    
## 6.deque 双端队列：
    
双端队列和向量比起来的话，就是说双端队列本身的算法就是在两头添加或删除数据，其时间复杂度是1，也就是说如果是经常会进行头尾增删的数据结构，尽量选用deque，当然用vector应该或者别的数据结构也是可以的，其实这个结构本身感觉没有其特别的特色，不过要注意的是：eque 容器中存储元素并不能保证所有元素都存储到连续的内存空间中。
    
这个感觉不怎么会用到，所以这里的话我就不看了，如果将来回看这个有用的话，可以查看这条博客
    
[C++ STL deque容器 详解版](http://c.biancheng.net/view/6860.html)
    
## 7.list 列表
    
列表，其实准确的说是一个双向链表，具体怎么实现的就不过多赘述了，这样的存储结构也不用多嘻嘻哈哈别的，它在任意位置增删的时间复杂度都是1，移动元素的速度也最快，是一个效率非常高的数据结构，这可不是随便和什么vector和array可以嘻嘻哈哈的啊。当然了这么牛逼的list也有它的问题：不能随机存取数据，也就是说不能像vector那样直接给一个位置，就可以直接转到指定的元素上去，而是只能一个个遍历，直到找到指定的位置才行。
    
这个很重要，着重写一下。
 
### 1.创建方法：
    
    std::list<int> values;
    std::list<int> values(10);
    
    //拷贝普通数组，创建list容器
    int a[] = { 1,2,3,4,5 };
    std::list<int> values(a, a+5);
    //拷贝其它类型的容器，创建 list 容器
    std::array<int, 5>arr{ 11,12,13,14,15 };
    std::list<int>values(arr.begin()+2, arr.end());//拷贝arr容器中的{13,14,15}
    
### 2.常用方法
    
![image](https://user-images.githubusercontent.com/102945300/178144451-6d988408-a594-40c3-9c7b-39a9f14b062e.png)

## 8.set集合
  
这位更是重量级
    
set其实也是键值对，这点和map很像，但是又有些不同，因为set中的键值必须相等，也就是key 和 value两个值都必须相等，比如![image](https://user-images.githubusercontent.com/102945300/178144825-bdac9488-b98b-4b59-82a6-447d43070922.png)
上面的数据就不能组成set，下面的才可以，当然了，既然如此那set就不用写键值对了，直接每个元素写一个值就可以了。
    
set容器有两个特点，一是：不可以存在有重复的键值对 二是：输入元素数据之后会自动排序。
    
    对于初学者来说，切勿尝试直接修改 set 容器中已存储元素的值，这很有可能破坏 set 容器中元素的有序性，最正确的修改 set 容器中元素值的做法是：先删除该元素，然后再添加一个修改后的元素。
    
### 1.初始化：
    
    std::set<std::string> myset;
    
    std::set<std::string> myset{"http://c.biancheng.net/java/",
                            "http://c.biancheng.net/stl/",
                            "http://c.biancheng.net/python/"};
    
    std::set<std::string> copyset(myset);
    //等同于
    //std::set<std::string> copyset = myset
    
    std::set<std::string> myset{ "http://c.biancheng.net/java/",
                    "http://c.biancheng.net/stl/",
                    "http://c.biancheng.net/python/" };
    //copyset方法支持从某个元素开始到某个元素结束，皆可自由指定
    std::set<std::string> copyset(++myset.begin(), myset.end());
    
 ### 2.常用方法
    
![image](https://user-images.githubusercontent.com/102945300/178145072-e63e6716-2fdd-4576-83d8-51ccce63f4c9.png)

### 3.multiset：
    
和set的区别？同样是排序好的集合，但是multiset允许有相同的元素
    
个人感觉没什么含义，不如直接vector排序，追求极致性能的时候可能有用，详情见
    
在学习掌握set和multiset过程中，我们会了解到set和multiset是存在一定差异的；
在set中每个元素的值都唯一，并且元素在插入后会自动的为其升序排序，值得注意的是set中数元素的值不能直接被改变。
    
C++ STL中标准关联容器set, multiset, map, multimap内部采用的就是一种非常高效的平衡检索二叉树：红黑树，也成为RB树(Red-Black Tree)。RB树的统计性能要好于一般平衡二叉树，所以被STL选择作为了关联容器的内部结构。

区别：
set不能插入已有的数据，即不能重复插入；multiset可以实现；
    
set在插入数据同时会返回插入成功失败结果；
    
multiset不会实现数据监测；
 
    
[multiset详解](http://c.biancheng.net/view/386.html)
    
##9.map映射
    
和set差不多，但是不同的是map是键值对，其中的数据是一对一的，且key不能重复，但是value可以，容器会根据key的大小来进行排序，
    
### 1.构造方式
    
    std::map<std::string, int>myMap;
    
    std::map<std::string, int>myMap{ {"C语言教程",10},{"STL教程",20} };
    
    std::map<std::string, int>myMap{std::make_pair("C语言教程",10),std::make_pair("STL教程",20)};
    
    std::map<std::string, int>newMap(myMap);
    
    std::map<std::string, int>newMap(++myMap.begin(), myMap.end());
    
    
### 2.常用方法
    
![image](https://user-images.githubusercontent.com/102945300/178146346-370d7391-12fa-49d0-baac-2f3de82289d5.png)
