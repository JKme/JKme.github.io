Title: aria2c下载说明书
Date: 2017-11-9
Category: Fun
slug: aria2c-download

###Install

```
brew install aria2(OSX)
sudo apt-get install aria2(Linux)
```

###Conf

```
wget https://raw.githubusercontent.com/acgotaku/BaiduExporter/master/aria2c/aria2.conf
```

###百度网盘转aria2c

```
git clone https://github.com/acgotaku/BaiduExporter.git
```
然后打开chrome的扩展程序，开发者模式，安装。

###supervisorctl

```
[program:aria2c]
command = aria2c --conf /soft/yaaw/aria2.conf
user = root
autostart = true
```

配置插件的设置RPC的地方，修改对应的地址

##可选:

###yaaw

```
git clone https://github.com/binux/yaaw.git

复制到nginx的目录下，打开nginx即可，下载的时候就可以看到下载进程

```