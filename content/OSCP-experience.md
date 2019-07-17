Title: OSCP经验
Category: Pentest
Date: 2019-04-02
Slug: oscp-experience


##0x01: 网络问题


```
socks-proxy 127.0.0.1 6876
uth-user-pass auth.txt

```
在openvpn的配置文件里面，我加了上面两行。
第一行因为国内网络不稳定，我加了ss的代理，后来换成了v2ray.
第二行是理由同上，因为网络不稳定，每次连接VPN都要输入用户密码，这样方便点.

具体网络不稳定有两个表现:

1. nmap扫描全部的端口长时间没有反应.
2. dirbuster扫描的时候会卡死进行不下去了.

上面两个问题有两个解决方法:

1. nmap换成https://github.com/AnthraX1/InsightScan, 先用单文件扫描全部的开放端口，然后用nmap扫描开放端口服务: `nmap -sS -sV -sC <IP> -p <PORT>`
2. dirbuster换成gobuster，词典不变，线程控制在25个左右.

##0x02: 报告问题

我的报告格式和下面这个人的差不多。如果可以尽量使用官方的模版就用官方的模版，不然容易凉，我写了50多页的报告，做了4道半题目。
https://www.cnblogs.com/xiaoxiaoleo/p/9040339.html

##0x03: 监考问题

监考放松，当监考老师不存在。想吃啥吃啥，想喝就喝，放松心态。