Title: SVN匿名扫描
Date: 2016-4-15
Category: Python
slug: svn-scan

程序是最开始学习Python写的，基本是东拼西凑，从这个程序开始接触多进程。有两个版本第一种是直接使用`sock`的`connect`连接来判断，第二种使用了`scapy`，本着追求最快的程序，结果使用`scapy`比`socket`要慢好多。

下面是第一个程序，使用`socket`扫描:

```python
#!/usr/bin/env python
# -*-coding:utf-8-*-

from subprocess import Popen,PIPE
import re
from netaddr import IPNetwork
import socket
from Queue import Queue
import threading
import time
import os

iplist = list(IPNetwork('1.2.3.4/24'))
def svn_scan(ip):
            s = socket.socket()
            s.settimeout(0.1)
            if s.connect_ex((str(ip), 3690)) == 0:
                p = Popen("svn info svn://" + str(ip),shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
                (out, err) = p.communicate()
                if re.search(r'UUID', out):
                     print ip
            s.close()


def worker():
    while not q.empty():
       ip = q.get()
       try:
            svn_scan(ip)
       finally:
            q.task_done()
start = time.time()

if __name__ == '__main__':
    q = Queue()
    map(q.put,iplist)
    threads = [threading.Thread(target=worker) for i in range(50)]
    map(lambda x: x.start(), threads)
    q.join()
    print 'need time %s' % (time.time() - start)
```


然后是使用了`scapy`的`syn`扫描：

```python
#!/usr/bin/env python
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR) #关闭import scapy的警告
from scapy.all import *
from netaddr import IPNetwork
from subprocess import Popen, PIPE
import re
import time
from Queue import Queue
import threading

conf.verb = 0  #关闭输出
targets = list(IPNetwork('1.2.3.4/24'))
start = time.time()
def svn_scan(target):
    ans = sr1(IP(dst=target)/TCP(dport=3690, flags="S"), timeout=0.5)
    if ans is None:
        pass
    elif ans.haslayer(TCP):
        if ans.getlayer(TCP).flags == 18:
            sr(IP(dst=target)/TCP(dport=3690, flags="RA"), timeout=0.01)
            p = Popen("svn info svn://" + target, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            out, err = p.communicate()
            if   re.search(r'UUID', out) :
                print target

def worker():
    while not q.empty():
        item = q.get()
        try:
            svn_scan(str(item))
        finally:
            q.task_done() 
if __name__ == '__main__':
    q = Queue()
    map(q.put, targets)
    threads = [ threading.Thread(target=worker) for i in range(50)]
    map(lambda x: x.start(), threads)
    q.join()
    print 'need time %s' %(time.time() - start)
```

====2017-12-15更新

关于多线程，上面两个的`q.join`写错了，删掉之后改为:

```
map(lambda x: x.join(), threads)
```

扫描`/24`的主机，花费的时间从8s变为了0.5s，时间不是这么计算的。

如果上面没有设置线程的daemon，最后运行的时候会一直卡着，因为进程默认不会停的，要这样:

```
map(lambda x: x.setDaemon(True), threads)
map(lambda x: x.start(), threads)
map(lambda x: x.join(3), threads)
```

最后的几句修改为上面的样子才是终极形态：

1. 设置了daemon，这样程序在子线程结束之后才回正常结束
2. join设置了超时时间，因为有时候线程会出现生产者没有，消费者等待（也就是消费者阻塞了）的情况，相当于设置了一个等待超时时间，如果不设置，消费者就会一直阻塞。


Python里面，当线程比较多的时候，线程的切换是一件十分耗时的工作，但是python里面提供了一个比较好玩的东西，协程来解决这个问题