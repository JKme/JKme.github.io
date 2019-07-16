Title: 根据IP获取地址
Date: 2016-8-19
Category: Fun
slug: get-address-from-ip


```php
<?php
error_reporting(E_ALL ^ E_NOTICE);
    header('Content-Type:text/html;charset=utf-8');
    function get_addr($_ip) { 
        $_ip=array("X-Forwarded-For:{$_ip}");
            //初始化curl模块 
        $curl = curl_init();
        //需要获取的URL地址，也可以在 curl_init() 函数中设置。
        curl_setopt($curl, CURLOPT_URL, 'http://ip.zishuo.net/');
        //在启用 CURLOPT_RETURNTRANSFER 的时候，返回原生的（Raw）输出。
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
        //设置"User-Agent: "头
        curl_setopt($curl, CURLOPT_USERAGENT  , 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36');
        curl_setopt($curl, CURLOPT_HTTPHEADER, $_ip);
        //执行cURL
        curl_exec($curl); 
        //关闭cURL资源，并且释放系统资源 
        $retn=curl_exec($curl); 
        curl_close($curl);
        return json_decode($retn);
    } 
    $_addr=get_addr($_GET['ip']);
    if ($_addr->code=='200') {
        echo $_addr->desc.'->'.$_addr->position;
    }elseif($_addr->code=='404'){
        echo $_addr->message;
    }else{
        echo '异常!';
    }
 
?>
```
上面保存为test.php,然后是`1.php`：

```php

<?php
header('Content-Type:text/html;charset=utf-8'); 
$_ip=$_SERVER['REMOTE_ADDR']; 
$_ip_addr=file_get_contents('http://127.0.0.1/test.php?ip='.$_ip); 
$fh = fopen('ip.txt', 'a'); 
fwrite($fh, 'IP:'.$_ip.' Time:'.date("Y-m-d H:i",time()+28800).' Address:'.$_ip_addr."\r\n"); fclose($fh); 
$im = imagecreatefromjpeg("n00b.png"); 
header('Content-Type: image/jpeg'); 
imagejpeg($im); 
imagedestroy($im); 
?>
```
找个`2.jpg`的图片，在windows下执行：`copy 2.jpg+1.php ip.jpg`。

最后在vps上面配置nginx解析jpg图片，这里需要设置下：

对于**5.3.9**以上版本的php，需要设置`php-fpm.ini`，加上这个字段:
`security.limit_extensions = .php .jpg`或者直接修改为`true`，然后在nginx配置的`location`位置加上这样的语句：

```
location ~ \.jpg$ {
       	    fastcgi_pass unix:/tmp/php-cgi.sock;
       	    include /usr/local/nginx/conf/fastcgi.conf;
}
```
不管怎么配置，大概意思就是让jpg结尾的图片，丢到`php-fpm`去处理，然后解析执行。