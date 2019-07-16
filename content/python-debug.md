Title: 记一次python调试
Category: Python
Date: 2017-11-10
Slug: python-debug

Hawkeye在爬虫的时候，总是阻塞卡住不动了。使用Pycharm调试，如下流水账:

原理就是pycharm作为server，远程要debug的是client。在client要安装pycharm-debug.egg，安装之后

```
python -m easy_install pycharm-debug.egg
```

```
import pydevd
```

没毛病就表示安装成功。

这个pycharm的包一般在这个目录:

```
/Applications/PyCharm.app/Contents/debug-eggs
```

然后配置pycharm:

```
在Preferences -> project 会有当前项目，先设置 project Interpreter

点开最右边的小齿轮，选择添加remote interpreter。

然后在配置项目运行的配置文件，添加一个python remote debug。

其中的`local host name`要设置pycharm机子的IP，PORT随便填，最后把两行代码加到要debug的机子文件上:


import pydevd

pydevd.settrace('192.168.140.40', port=10000, stdoutToServer=True, stderrToServer=True)
```


先pycharm启动调试，然后远程运行即可。

```
strace -p 27691 -e trace=read,write -s 1024
```

调试的时候可以看读写调用。