Title: pymultitor切换IP
Category: Fun
slug: pymultitor
Date: 2018-06-14


<https://github.com/realgam3/pymultitor>

安装方法看github就可以了，mac下需要安装tor和mitmproxy

```
brew install mitmproxy
brew install tor
```

设置下proxifier的规则，tor使用代理，然后:

```
pymultitor -lp 8081 -lh 127.0.0.1 --on-count  2 -d
``` 
在本机的8081端口开了一个http代理，这个代理可以转成socks，未测试。

可以在目标是用waf的情况下测试使用，比如sql注入等容易触发防火墙的情况下，burp设置一个代理，就可以随便跳代理了,实际效果未测试。