Title: Tips
##Linux
###Find
删除一定时间内的文件：
`find . -type f -cmin -20 | xargs rm -rf `

* 访问时间 （-atime/天, -amin/分钟)Access :用户最近一次访问时间
* 修改时间 （-mtime/天, -mmin/分钟)Modify :文件最后一次修改时间
* 变化时间 （-ctime/天, -cmin/分钟)Change :文件数据元（例如权限等）最后一次修改时间

> 时间后面`-20`，带`+`表示符合**该数量以前**, `-`表示符合符合**该数量以后**

查找当前包含`oldString`文件，然后替换为字符串,`-i`对源文件生效
` grep -rl "oldString" . |xargs sed -i 's/oldString/newString/g''`

##Mac屏幕共享
###开启
`sudo  /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -on -clientopts -setvnclegacy -vnclegacy yes -clientopts -setvncpw -vncpw mypasswd -restart -agent -privs -all`
###关闭
`sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -deactivate -configure -access -off`
##所有用户开启
`sudo /System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart -activate -configure -access -off -restart -agent -privs -all -allowAccessFor -allUsers`

`http :9200/_cat/indices?v  查看elasticsearch节点状态`
`http DELETE	:9200/some_index  删除节点`

`inotifywait -mrq --timefmt '%d/%m/%y/%H:%M' --format '%T %e %w %f' -e open,close_write,modify,delete,create,attrib /tmp`

```
%T time
%e 文件的变化
%w 工作目录
%f 文件
输出如下：

19/10/16/11:08 CREATE /tmp/ phpc3MhO9
19/10/16/11:08 MODIFY /tmp/ phpc3MhO9
19/10/16/11:08 DELETE /tmp/ phpc3MhO9
```
子域名最长长度是63个字节，或者说63个字母。

```
kiallall php-fpm  杀死php-fpm进程

php-fpm -c /usr/local/etc/php/5.5/php.ini -y /usr/local/etc/php/5.5/php-fpm.conf -D  重启php-fpm

php-fpm一般监听9000端口，如果使用xdebug，制定9001端口

lsof -Pni4 | grep LISTEN | grep php  查看php占用端口
```

##Git删除敏感信息

```
测试可用:
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch [sensitive-data.txt]' --prune-empty --tag-name-filter cat -- --all

git push origin --force -all


测试失败:
删除敏感文件：
bfg --delete-files [sensitive-data.txt] [git repo]
git push origin --force -all

替换掉文件里面的敏感信息
bfg --replace-text [sensitive-data.txt] [git repo]
```

##rsync使用私钥

```
rsync -Pav -e "ssh -i $HOME/.ssh/private"  jdk-8u101-linux-x64.tar.gz root@xxxxx:/root/
```

update-alternatives --config java


##MONGO基本操作
```
show dbs
use [db]
show collections
db.[col].find({_id:"[id]"})
db.[col].remove({_id:"[id]"})
var ids = db.[col].distinct('_id', {}, {}); 获取所有的ID值
db.leakage.find({"ignore":0},{"_id":1})   查找ignore为0，返回所有对应的id值
DBQuery.shellBatchSize = 1500  返回条数有限制，这个是返回的数量
db.leakage.find({},{"ignore":1}).forEach(function(f){print(tojson(f, '', true));}); 返回所有的对应id和字段
 
```

##INSTALL ss 2.8.2

```
wget https://pypi.python.org/packages/source/s/shadowsocks/shadowsocks-2.8.2.tar.gz
tar zxvf shadowsocks-2.8.2.tar.gz
cd shadowsocks-2.8.2
python setup.py install
```

##SHELL组合
```
ps -ef |grep "sh -c" |grep -v grep |awk '{print $2}' |xargs kill -9
```
##Iterm2背景颜色
```
R:14
G:40
B:50
```
##zlib解压缩

```
openssl zlib -d < [zlibfile]
如果使用hexdump查看文件，hexdump -C [zlibfile]
文件头是 78 9c
```
##ssh-agent的forward

```
A主机有私钥，B,C有公钥。
现在从A登录到B，再从B登录到C，使用ssh-agent步骤:
A配置ssh的config，添加:
ForwardAgent yes
A使用ssh-add添加私钥
A启动ssh-agent: eval $(ssh-agent)

B主机启动ssh-agent即可:
eval $(ssh-agent) 
然后从B到C登录就不需要密码，可以使用
ssh -vvv root@ip 查看详细信息。
```

##SSH的反向代理端口
```
A是vps主机，B,C 是内网
现在从C通过A主机去连接B主机，步骤如下:
B: ssh -p 22 -qngfNTR "*:7777:localhost:22" root@A的vps
（注意是*,如果没有*，在A主机默认监听的是127.0.0.1地址），相当于把B主机的22端口反弹到转发的vps的7777端口，这个时候直接连接A端口的7777就可以连B的ssh了
然后编辑A主机的sshd配置文件/etc/ssh/sshd_config添加：
GatewayPorts yes

在C主机上面运行:
C: ssh -p 7777 -qngfNTD 8888 root@A的vps 
然后输入B主机的ssh密码,此时就可以以C主机的8888端口作为socks5代理来进入B的内网。

socat挺好使，在第一步的时候，反弹到127.0.0.1端口了，然后使用socat，监听0.0.0.0的某个端口，把流量转发到7777即可
socat -v tcp-listen:7777,fork tcp-connect:localhost:6666


本地访问127.0.0.1:port1就是host:port2
ssh -CfNg -L port1:127.0.0.1:port2 user@host    #本地转发

访问host:port2就是访问127.0.0.1:port1
ssh -CfNg -R port2:127.0.0.1:port1 user@host    #远程转发
远程转发可以用于msf反弹，使用本地的msf，将远程vps的端口流量转发到本地,在mac下可以这样:

autossh -M 20000 -N -R 11111:192.168.14.102:10000 vps
-M 20000选项指定了中继服务器上的见识端口，用户交换监视ssh会话的测试数据



可以将dmz_host的hostport端口通过remote_ip转发到本地的port端口
ssh -qTfnN -L port:dmz_host:host：port -l user remote_ip   #正向隧道，监听本地port

可以将dmz_host的hostport端口转发到remote_ip的port端口
ssh -qTfnN -R port:dmz_host:host：port -l user remote_ip   #反向隧道，用于内网穿透防火墙限制之类

-C 进行数据压缩 -q 安静模式 -T 不占用 shell 了 -f 后台运行，并推荐加上 -n 参数 -N 不执行远程命令，端口转发就用它 -g 允许所有远程主机连接到转发的端口
```

###F5解密脚本

```
#Set-Cookie: BIGipServerpool_8.29_8030=487098378.24095.0000
$ python /tmp/1.py 487098378.24095.0000
10.136.8.29:8030

import struct
import sys

def decode(cookie):
    (host, port, end) = cookie.split('.')
    (a, b, c, d) = [ord(i) for i in struct.pack("<I", int(host))] 
    p = [ord(i) for i in struct.pack("<I", int(port))]
    port = p[0]*256 + p[1]
    print "%s.%s.%s.%s:%s" % (a,b,c,d,port)

decode(sys.argv[1])
```

###Linux下elf与txt的互相转化

```
https://stackoverflow.com/questions/15490728/decode-base64-invalid-input

把elf文件转成base64，mac下是这样的：

cat [elf]|base64| tee[res.txt]

然后在Linux上面:
cat res.txt|base64 -di [elf-file]
```
###tomcat相关的路径
```
/webapps/WEB-INF/web.xml
/webapps/WEB-INF/classes/
/webapps/WEB-INF/classes/sysinfo.properties
/webapps/WEB-INF/lib/
```

Linux上面经常查看自己IP，偷懒

```
在／etc/profile.d/下面新建一个文件alias.sh

alias ip="hostname -I"

保存，然后source /etc/profile.d/alias.sh
```

###NAVICAT连接mysql，1146错误

```
mysql里面没有performance_schema表
mysql_upgrade -u root -p --force
重启mysql
```

###iptables只允许某个国家连接

```
https://superuser.com/questions/996526/ubuntu-iptables-allow-only-allow-1-country

apt-get install xtables-addons-common
mkdir /usr/share/xt_geoip
apt-get install libtext-csv-xs-perl unzip
/usr/lib/xtables-addons/xt_geoip_dl
/usr/lib/xtables-addons/xt_geoip_build -D /usr/share/xt_geoip *.csv

iptables -A INPUT -m geoip --src-cc CN  --dstport <port> -j ACCEPT
iptables -A INPUT -p tcp --dport <port> -j DROP
```

###AWS创建ENA支持的AMI

```
1. 登录到主机检测是否支持ena: modinfo ena
2. 关机之后启用ena:
aws ec2 modify-instance-attribute --instance-id instance_id --ena-support

3. 创建snap之后根据snap创建AMI:
aws ec2 register-image --architecture x86_64 --descriptio 20190226 --ena-support --name 20190226 --virtualization-type hvm  --block-device-mappings '[{"DeviceName": "/dev/sda1","Ebs": {"SnapshotId": "snap-XXXX"}}]'  --root-device-name /dev/sda1
```

###持续监听某个端口

```
socat -v -dd tcp-listen:<port>,reuseaddr,fork system:'echo "$SOCAT_PEERADDR"'

socat -v -dd tcp-listen:444,reuseaddr,fork system:'echo "some command";echo "exit"'

可以用来持续监听端口，shell来之后执行后面的操作
```

###LINUX自带ping扫描

```
扫描整个段，B段的话去掉一个for
for i in $(seq 1 255);do for j in $(seq 1 255);do for x in $(seq 1 255);do if ping -c 1 -w 3 10.$i.$j.$x &>/dev/null; then echo 10.$i.$j.$x;fi >>/tmp/scan.txt;done;done;done
```