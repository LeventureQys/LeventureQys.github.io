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
