Title: XSS编码(2)
Category: Learning
Date: 2017-4-12
slug: xss-encode 

* <http://jkme.github.io/xss-encode-decode.html>
* <http://joychou.org/index.php/web/domxss-cause-by-html-auto-decode.html>

在前面文章里面xss的编码提到过这个东西: 

```
Fun fact Decoding Order:
1. HTML Decoding
2. URL Decoding
3. Javascript Decoding

http://slides.com/mscasharjaved/deck-13#/169

```

在**HTML标签里面**，js之行之前，html形式的编码会自动decode。

解释：

`<button type="submit" onclick="x='<img src=@ onerror=alert(123) />';document.write(HtmlEncode(x))">xsstest</button>`

丢到test.html里面，使用浏览器打开还是原样。

所以xss存在的步骤来说是这样的：
`代码--> 浏览器执行 --> xss`

浏览器解释了其中的代码展现给人看。

HTML的自动解码是在执行js代码之前，并且on*事件内可以执行js脚本，即 **html解码之后才可以执行js**。

如下的代码先htmldecode，然后执行js，最终造成DOM Xss：
```
<button type="submit" onclick="x='&lt;img src=@ onerror=alert(123) /&gt;';document.write(x)">xsstest2</button>
```
自动解码之后的代码如下：
`<button type="submit" onclick="x='<img src=@ onerror=alert(123) />';document.write(x)">xsstest2</button>
`

OK到了上面的地方，如果这里想要试用URL编码，看这里
<https://www.leavesongs.com/PENETRATION/use-location-xss-bypass.html>利用location变形xss代码。

加个例子（快把原文的摘抄完了）:

```
<?php 
$para = $_GET['category'];
$para = htmlspecialchars($para, ENT_QUOTES); // 将单引号进行HTML编码
//$para = urlencode($para);
$url_herf = "http://joychou.org/?category=" . $para ;
?>

<button type="submit" onclick="window.location.href='<?php echo $url_herf; ?>'">click</button>
```
POC:
`http://localhost/pentest/xss/domxss/onclick.php?category=web'-alert(1)-'`

上面代码进去之后，结果会是这样的:

`<button type="submit" onclick="window.location.href='http://joychou.org/?category=web&#039;-alert(1)-&#039;'">click</button>`

减号是一个操作符，在js里面，减号两边的表达式都会执行，最后产生一个domxss。

一般来说xss的防御就是在前端或者后端统一对输出进行html编码，但是不管前端还是后端统一做HTML编码，都会存在这样一个问题：如果编码之后的变量赋值在可执行的javascript的html tag中，会导致domxss。

作者给出了两种修复方式：

* 进行URL编码（不影响显示的情况)
* 针对变量值的范围做具体的限制（比如value的白名单，value长度，value类型)

<http://joychou.org/index.php/web/domxss-cause-by-html-auto-decode.html>
