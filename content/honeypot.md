Title: SSH honeypot
Category: Fun
Slug: ssh-honeypot
Date: 2017-11-28



<https://github.com/ohmyadd/wetland> 

使用上面的源代码搭建一个ssh蜜罐，然后配置bearychat，可以在手机上面实时接收蜜罐里面的命令等信息。

安装步骤很简单，使用python2.7，按照github上面的说明一步步安装就可以了。



配置bearychat：



1. 先<http://bearychat.com>这里注册用户，然后添加一个机器人，incoming 类型的。新建立之后会获取一个类似token的链接，然后在wetland里面的配置文件替换掉自己的机器人请求。
2.  然后跑蜜罐`python main.py`就可以了。



注意事项：

 因为蜜罐监听的是服务器的22端口，所以宿主机本身需要修改下ssh的默认监听端口，重启ssh服务器之后蜜罐就可以正常运行了，蜜罐的密码是`root` ，自己尝试登陆之后，在手机端就会收到机器人的提醒通知。



重要的不是ssh这个蜜罐，而是这个机器人通知。可以设想在某些特定的情况下，服务器使用这个机器人来向手机发送提醒，比如运维监控、TCP反弹监听、敏感日志监测
