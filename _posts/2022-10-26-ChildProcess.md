---
title: C#-将进程注册为子进程，父进程崩溃的时候子进程也随之退出的方案和实例
description: 将进程注册为子进程，父进程崩溃的时候子进程也随之退出的方案和实例
categories: 开发日志
keywords: 实例,C#,开发日志
---

# C#-将进程注册为子进程，父进程崩溃的时候子进程也随之退出的方案和实例

Kill child process when parent process is killed

我正在使用我的应用程序中的System.Diagnostics.Process类创建新进程。

当/如果我的应用程序崩溃了，我希望这个进程被杀死。 但是如果我从任务管理器中删除我的应用程序，子进程就不会被杀死。 有没有办法让子进程依赖于父进程？

如果关闭强制关闭父进程，Process类启动的子进程就会被提升为独立的进程，能不能让子进程随着父进程的崩溃而一起退出呢？当然是有的，通过windows自带的作业对象来完成

本文来自机翻问答:[关于c＃：杀死父进程时杀死子进程](https://www.codenong.com/3342941/)

首先作业对象的使用需要用到枚举类型如下：


     public enum JobObjectInfoType
            {
                AssociateCompletionPortInformation = 7,
                BasicLimitInformation = 2,
                BasicUIRestrictions = 4,
                EndOfJobTimeInformation = 6,
                ExtendedLimitInformation = 9,
                SecurityLimitInformation = 5,
                GroupInformation = 11
            }

            [StructLayout(LayoutKind.Sequential)]
            public struct SECURITY_ATTRIBUTES
            {
                public int nLength;
                public IntPtr lpSecurityDescriptor;
                public int bInheritHandle;
            }

            [StructLayout(LayoutKind.Sequential)]
            struct JOBOBJECT_BASIC_LIMIT_INFORMATION
            {
                public Int64 PerProcessUserTimeLimit;
                public Int64 PerJobUserTimeLimit;
                public Int16 LimitFlags;
                public UInt32 MinimumWorkingSetSize;
                public UInt32 MaximumWorkingSetSize;
                public Int16 ActiveProcessLimit;
                public Int64 Affinity;
                public Int16 PriorityClass;
                public Int16 SchedulingClass;
            }

            [StructLayout(LayoutKind.Sequential)]
            struct IO_COUNTERS
            {
                public UInt64 ReadOperationCount;
                public UInt64 WriteOperationCount;
                public UInt64 OtherOperationCount;
                public UInt64 ReadTransferCount;
                public UInt64 WriteTransferCount;
                public UInt64 OtherTransferCount;
            }

            [StructLayout(LayoutKind.Sequential)]
            struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
            {
                public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
                public IO_COUNTERS IoInfo;
                public UInt32 ProcessMemoryLimit;
                public UInt32 JobMemoryLimit;
                public UInt32 PeakProcessMemoryUsed;
                public UInt32 PeakJobMemoryUsed;
            }

引用系统接口如下：

        /// <summary>
        /// 创建作业对象
        /// </summary>
        /// <param name="lpJobAttributes">该作业的安全描述符</param>
        /// <param name="name">作业名字</param>
        /// <returns></returns>
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
        static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string name);

        
        /// <summary>
        /// 将进程注册为作业对象进程
        /// </summary>
        /// <param name="job">作业对象句柄</param>
        /// <param name="process">进程句柄</param>
        /// <returns></returns>
        [DllImport("kernel32.dll", SetLastError = true)]
        static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

        /// <summary>
        /// 设置作业对象限制
        /// </summary>
        /// <param name="hJob">标识要限制的作业   </param>
        /// <param name="infoType">枚举类型，用于指明要使用的限制类型</param>
        /// <param name="lpJobObjectInfo">包含限制设置值的数据结构的地址</param>
        /// <param name="cbJobObjectInfoLength">指明第三个参数的大小</param>
        /// <returns></returns>
        [DllImport("kernel32.dll")]
        static extern bool SetInformationJobObject(IntPtr hJob, JobObjectInfoType infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

我们所有的工作就是围绕上面这三个接口来展开，我在这里写一个类叫JobControl类，具体调用示例代码如下

       Process target_process = new Process();
  
      JobControl clsJobControl = new JobControl();
  
       clsJobControl.AddProcess(target_process);
  
  到这这个进程就被注册为主进程的子进程了，具体的JobControl类的内容如下，主要看构造函数和AddMessage即可
  
            using System;
          using System.Collections.Generic;
          using System.Diagnostics;
          using System.IO;
          using System.Linq;
          using System.Runtime.InteropServices;
          using System.Text;
          using System.Threading.Tasks;

          namespace LBD.CloudNetIntelClassroom.Seat
          {
              public class JobControl
              {
                  public enum JobObjectInfoType
                  {
                      AssociateCompletionPortInformation = 7,
                      BasicLimitInformation = 2,
                      BasicUIRestrictions = 4,
                      EndOfJobTimeInformation = 6,
                      ExtendedLimitInformation = 9,
                      SecurityLimitInformation = 5,
                      GroupInformation = 11
                  }

                  [StructLayout(LayoutKind.Sequential)]
                  public struct SECURITY_ATTRIBUTES
                  {
                      public int nLength;
                      public IntPtr lpSecurityDescriptor;
                      public int bInheritHandle;
                  }

                  [StructLayout(LayoutKind.Sequential)]
                  struct JOBOBJECT_BASIC_LIMIT_INFORMATION
                  {
                      public Int64 PerProcessUserTimeLimit;
                      public Int64 PerJobUserTimeLimit;
                      public Int16 LimitFlags;
                      public UInt32 MinimumWorkingSetSize;
                      public UInt32 MaximumWorkingSetSize;
                      public Int16 ActiveProcessLimit;
                      public Int64 Affinity;
                      public Int16 PriorityClass;
                      public Int16 SchedulingClass;
                  }

                  [StructLayout(LayoutKind.Sequential)]
                  struct IO_COUNTERS
                  {
                      public UInt64 ReadOperationCount;
                      public UInt64 WriteOperationCount;
                      public UInt64 OtherOperationCount;
                      public UInt64 ReadTransferCount;
                      public UInt64 WriteTransferCount;
                      public UInt64 OtherTransferCount;
                  }

                  [StructLayout(LayoutKind.Sequential)]
                  struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION
                  {
                      public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
                      public IO_COUNTERS IoInfo;
                      public UInt32 ProcessMemoryLimit;
                      public UInt32 JobMemoryLimit;
                      public UInt32 PeakProcessMemoryUsed;
                      public UInt32 PeakJobMemoryUsed;
                  }


                  /// <summary>
                  /// 创建作业对象
                  /// </summary>
                  /// <param name="lpJobAttributes">该作业的安全描述符</param>
                  /// <param name="name">作业名字</param>
                  /// <returns></returns>
                  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
                  static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string name);


                  /// <summary>
                  /// 将进程注册为作业对象进程
                  /// </summary>
                  /// <param name="job">作业对象句柄</param>
                  /// <param name="process">进程句柄</param>
                  /// <returns></returns>
                  [DllImport("kernel32.dll", SetLastError = true)]
                  static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

                  /// <summary>
                  /// 设置作业对象限制
                  /// </summary>
                  /// <param name="hJob">标识要限制的作业   </param>
                  /// <param name="infoType">枚举类型，用于指明要使用的限制类型</param>
                  /// <param name="lpJobObjectInfo">包含限制设置值的数据结构的地址</param>
                  /// <param name="cbJobObjectInfoLength">指明第三个参数的大小</param>
                  /// <returns></returns>
                  [DllImport("kernel32.dll")]
                  static extern bool SetInformationJobObject(IntPtr hJob, JobObjectInfoType infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);               
                  const System.String job_name = "Leventure_SeatJob";
                  private System.UInt32 job_ptr = 0;
                  private System.IntPtr job_handle = System.IntPtr.Zero;
                  /// <summary>
                  /// 构造函数，声明作业对象，限制作业对象。
                  /// </summary>
                  public JobControl()
                  {
                      job_handle = CreateJobObject(System.IntPtr.Zero, job_name);
                      JOBOBJECT_BASIC_LIMIT_INFORMATION info = new JOBOBJECT_BASIC_LIMIT_INFORMATION();
                      info.LimitFlags = 0x2000;
                      JOBOBJECT_EXTENDED_LIMIT_INFORMATION extendedInfo = new JOBOBJECT_EXTENDED_LIMIT_INFORMATION();
                      extendedInfo.BasicLimitInformation = info;
                    //Design by LeventureQys
                      int length = Marshal.SizeOf(typeof(JOBOBJECT_EXTENDED_LIMIT_INFORMATION));
                      IntPtr extendedInfoPtr = Marshal.AllocHGlobal(length);
                      Marshal.StructureToPtr(extendedInfo, extendedInfoPtr, false);

                      if (!SetInformationJobObject(job_handle, JobObjectInfoType.ExtendedLimitInformation, extendedInfoPtr, (uint)length))
                          throw new Exception(string.Format("Unable to set information.  Error: {0}", Marshal.GetLastWin32Error()));
                  }


                  /// <summary>
                  /// 为该dll注册子进程，当主程序崩溃的时候，子进程一样退出
                  /// </summary>
                  /// <param name="added_process"></param>
                  /// <returns></returns>
                  public bool AddProcess(Process added_process)
                  {
                      System.IntPtr handle = System.IntPtr.Zero;
                      handle = added_process.Handle;
                      return AssignProcessToJobObject(job_handle, handle);
                  }
              }
          }


