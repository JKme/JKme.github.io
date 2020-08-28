Title: 后门隐藏-Windows
Date: 2020-08-28
Category: Pentest
Slug: hide-your-backdoor-in-windows

分为三个部分:

1. shellcode的分离免杀
2. C2服务器的隐藏
3. Windows后门的设置

###shellcode的分离免杀

shellcode的分离免杀有很多种，这里把每个模块拿出来就是如下的几个:

1. 通信: `socket`,`http`
2. `shellcode`的执行方式
3. `shellcode`的流量
4. 远程服务器的隐藏

除去第二种方式有很多种可以执行shellcode的，其他三种最好的解决方案是实用`Domain Fronting`隐藏服务器，AES动态加密解密运行shellcode。这样子既隐藏了服务器，又避免shellcode的明文流量被探测到。当然上线之后的操作被探测不在被讨论的范围之内。

在参考资料里面,`uknownsec`已经把主要的代码放出来了。只需要拿出来拼凑一下就可以食用。

其中服务端出去python的功能之外，可以给自己加上一个`slack`机器人的通知，这样子上线的时候就有通知。



###C2服务器的隐藏

见上一篇的`Domain Fronting`隐藏HTTPS。

这个C2的隐藏如果更完美一点的话，可以加上redirector。但是我想了一下，开启CS的时间就是控制利用的那一小段，这里就不折腾了。

###Windows后门的设置

除去最常见的计划任务，剩下的是一堆注册表，如果存在360之类的话，是比较难处理的。其中有一个`WMI`，很奇怪各个杀软的拦截都不是太积极。

在实际测试中，如果留的后门是服务器，那么后门必须是定时启动，如果是个人电脑，那么是在特定的时间内启动。注意这个时间点的设置。

在Windows上面，最后留下2个以上的后门。一个exe，一个dll劫持，dll劫持我在github上面放了两个方式，推荐使用spooler，因为它默认权限最高，每个电脑都是开机启动。


###云查杀的绕过

之前在测试`Windows Defender`的时候，本来是免杀的exe，我跑两三次之后就被杀了。百思不得其解，后来发现是云上传之后被查杀了，观察一下上线云查杀的机器，可以很容易的绕过。

再往后一点，考虑一下如果每个机器上线都是你动手来做的话，那么可以考虑写一个程序，为每一个被放后门的电脑生成一个唯一的hash值，这个hash值存放在shellcode加载服务器上面，shellcode执行之前先检查是否在数据库里面，这样是不是更完美的方式?

####End

所以终极的方式就是:

`AES`动态加解密 + `Domain Fronting`隐藏存放`shellcode` + `Domain Fronting`隐藏`C2` + `shellcode`免杀的执行方式



参考资料:

* <https://uknowsec.cn/posts/notes/ShellCode%E8%BF%9C%E7%A8%8B%E5%8A%A0%E8%BD%BD%E5%99%A8%E6%94%B9%E9%80%A0%E8%AE%A1%E5%88%92.html>