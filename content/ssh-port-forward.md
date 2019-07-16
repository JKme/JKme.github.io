Title: SSH端口转发
Category: Learning
Date: 2017-2-16
slug: SSH-Port-forward

以下几个原则：

* SSH简单来说就是2台机器之间安全的数据通道，它包括ssh的client和ssh的server2个角色，这样的一条通道就是(ssh tunneling)
* SSH端口转发需要ssh连接，同时SSH连接有方向，从SSH Client到SSH Server
* 同理应用请求也是有方向的，一般是客户端向服务端发出请求
* 一旦这两个方向相同，称为SSH的本地转发(-L)，反之称为远端转发(-R）

###本地转发

`ssh -L <local port>:<host>:<hostport> <sshserver>`

通过sshserver建立与host的连接，并将host的hostport绑定到本地的localport端口

应用场景：比如有一台应用服务器appserver（appserver.com），要访问其80端口，但是本地却不能直接访问，于是可以借助一台可以访问appserver的sshserver（sshserver.com）来访问它。
`ssh -L 8000:appserver.com:80  user@sshserver.com`

ssh链接建立之后，发送到本地8000的包会通过sshserver转发给appserver的80端口

###远程转发

`ssh -R <remoteport>:<host>:<hostport> <remoteserver>`
远程转发可以通过本地主机，将remoteserver与host连接，host的hostport
将会映射到remoteserver的remoteport端口

应用场景: 一台应用服务器appserver(appserver.com），只有本地才能访问80端口，假如remoteserver想访问appserver的80端口，需要通过本地主机做隧道来完成。

`ssh -R 8000:appserver.com:80 user@remoteserver.com`
之后要求输入user用户在remoteserver上的密码。

remoteserver会监听自己的8000端口，其后发往remoteserver的8000端口的包，会通过本地服务器发到remoteserver的80端口。

>如果访问http://remoteserver:remoteport，注意修改remoteserver的ssh配置,`sshd_config添加GatewayPorts yes`

`https://ricterz.me/posts/Mount%20NFS%20via%20Proxy?_=1487726774098`

这篇文章里面是这样用的：

`ssh ricterz.me -lroot -R[remoteport]:localhost:[localport] －CNfg`


###动态转发
`ssh -D <localport> <sshserver>`

监听本地localport端口，创建一个通过sshserver连接的socks服务，之后发往localport的代理请求将会通过sshserver转到相应地址。

`ssh -D 8000 user@sshserver.com`

输入user的密码之后，你就可以将浏览器的socks5代理设为自己的8000端口，之后会有数据以加密的方式传给sshserver，sshserver获取www.blockedwebsite.com之后返回本地。


```
-f ssh在后台运行，即认证之后，ssh退居后台
-T 不要分配tty终端
-N 不要在服务器执行命令
-C  压缩数据包
-i  指定认证密钥
-n  将studio重定向到/dev/null 与-f配合使用
-q  安静模式
-l  指定连接远程服务器的用户名
-g  允许远程主机连接主机的转发端口
```
另外：
`ssh -f -L 1234:localhost:6667 server.example.com sleep 10`
后台运行转发，但是再ssh运行后10秒钟都没有连接1234端口的话，ssh自动退出。

* http://wlwang41.github.io/content/ops/ssh%E9%9A%A7%E9%81%93%E4%BB%A3%E7%90%86.html
* http://lcwangchao.github.io/linux/unix/2012/08/03/sshport/