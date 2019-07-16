Title: 《白帽子讲Web安全》
Date: 2016-9-25
Category: CTF
slug: web-security

##PHP
###文件包含漏洞（File Inclusion）

文件包含可能会出现在JSP、PHP、ASP等语言中，常见的函数如下：
`PHP: include()、include_once()、require()、require_once()、fopen()、readfile()`

文件包含是PHP的一种常见用法，主要由四个函数组成：

* include()
* require()
* include_onec()
* require_once()

当使用这4个函数包含一个新的文件，该文件将作为PHP代码执行，PHP内核并不会在意被包含的文件是什么类型。

所以如果被包含的是txt文件，图片文件，远程URL等都会作为PHP代码执行。

能够打开并且包含本地文件的漏洞称为本地文件包含漏洞（Local File Inclusion，LFI）

PHP语言是由C语言实现的，因此使用了C语言中一些字符串处理函数，在连接字符串的时候，0字节（\x00）讲作为字符串结束符。所以攻击者可以加一个0字节，截断file变量后面的字符串，即
`../../etc/passwd\0`，在get请求的时候进行Urlencode，变成`../../etc/passwd%00`。

如果禁用了0字节可以利用操作系统对目录最大长度的限制，可以不需要0字节而达到截断的目的。目录字符串，在windows下256字节，Linux下4096字节会达到最大值，最大值长度之后的字符串将会被丢弃。可以通过如下构造:
`../../../../../../../../../../../../../../abc`

* %2e%2e%2f 等同于 ../
* %2e%2e/ 同上
* ..%2f 同上
* %2e%2e%5c ..\
* %252%252%255c等同于..\


open_basedir的作用是跨越目录读取文件的方法，当PHP配置open_basedir讲保护服务器，使得这种攻击无效。

关于这一点可以搜索P牛的文章，其中有绕过open_basedir。

如果PHP的配置选项allow_url_include为On的时候，则include/require函数可以加载远程文件，这种漏洞称为远程文件包含漏洞（Remote File Inclusion，RFI)。
远程文件包含漏洞可以直接执行任意命令，比如攻击者服务器有以下文件:

```
<?php
echo system("ver;");
?>
```

远程文件包含之所以可以执行命令，因为攻击者可以自定义被包含的文件内容，因此本地文件包含漏洞想要执行命令，需要找到一个攻击者可以控制内容的本地文件。

* 用户文件上传
* 包含data:// 或php://input等伪协议
* 包含Session文件
* 包含日志文件
* 包含/proc/self/environ文件
* 包含上传的临时文件
* 包含其它应用创建的文件，比如数据库文件，缓存文件，应用日志等

包含日志文件是比较通用的技巧，因为服务器一般会往Web Server的access_log记录客户端的请求信息，在error_log记录出错请求。因此攻击者可以间接讲PHP代码写入到日志文件中，在文件包含的时候，包含即可执行。

如果网站访问量比较大，php可能会僵死，但Web Server往往滚动生成日志，因此在凌晨包含日志文件讲提高攻击的成功性。

PHP创建的上传临时文件，往往处于PHP允许访问的目录内，包含这个临时文件，PHP会为上传文件创建临时文件，其目录在php.ini的upload_tmp_dir中定义，但该值默认为空，在Linux中会使用/tmp目录，在windows中使用C:\windows\temp目录。这个例子可以查看`wooyun-2015-134185 Chroa的文件包含漏洞`


###变量覆盖漏洞
####全局变量覆盖

变量如果未被初始化，且能被用户所控制，那么很可能会导致安全问题。

* extract() 变量覆盖
* 遍历初始化变量
* import_request_variables变量覆盖
* parse_str()变量覆盖

###代码执行漏洞
文件包含可以造成代码执行，popen(),system(),passthru(),exec()等可以直接执行系统命令。
可以执行代码的函数：`eval(),assert(),system(),exec(),shell_exec(),passthru(),escapeshellcmd(),pcntl_exec()`

###与安全有关的php.ini配置:

####register_globals

当register_globals为on的时候，php不知道变量从何而来，容易出现变量覆盖的问题。因此强烈建议设置register_globals = OFF，这个也是新版本中的默认配置。

####open_basedir
open_basedir限制PHP只能操作指定目录下的文件，在对抗文件包含，目录遍历等攻击的时候非常有用，如果设定的值是一个指定的目录需要在最后加上一个`/`，否则会认为是该目录的前缀

####allow_url_include
对抗远程文件包含，同时还有allow_url_fopen, allow_url_include

####magic_quotes_gpc 
推荐关闭，在开启的时候回在特殊字符前加`\`进行转义
####cgi.fix_pathinfo
PHP以CGI的方式安装，则需要关闭此项，以避免出现文件解析的问题。
####session.cookie_httponly
开启HttpOnly
