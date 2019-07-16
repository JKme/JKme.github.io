Title: Crontab反弹shell
Category: Pentest
Date: 2017-3-22
slug: crontab-shell

第一个先看看系统内crontab是否在运行:

`ps -ef |grep cron`

如果没有运行，以ubuntu为例子需要：

`service cron start` 开启cron服务

用systemctl也行

```
systemctl start cron  开启cron
systemctl enable cron 开机运行
systemctl status cron  查看状态
```


不知道为什么python的反弹脚本反弹之后，当前shell的环境变量是`/usr/bin:/bin`，先设置下环境变量

`export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`

另外这两篇文章讲了redis里面设置crontab的坑：

* http://joychou.org/index.php/web/linux-crontab-rebound-shell-hole.html

* http://joychou.org/index.php/web/hackredis-enhanced-edition-script.html 