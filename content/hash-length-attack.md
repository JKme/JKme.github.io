Title: Hash Length Extension Attack 
Date: 2016-7-25
Category: Learning
slug: hash-length-extension-attack

https://www.leavesongs.com/PENETRATION/zhangyue-python-web-code-execute.html

这篇文章里有提到的哈希长度扩展攻击看了下做个笔记。理解哈希长度扩展攻击以md5为例，需要理解下面几点：

### MD5的**部分工作原理**
 
#### 一. 先看下MD5的计算过程，只需要理解一半：
 对于一个message进行md5计算的过程是这样的：
 经过三个步骤，这部分可以看[RFC](https://tools.ietf.org/html/rfc1321):
 
 The message is "padded" (extended) so that its length (in bits) is congruent to 448, modulo 512. 
   先进行补位，使得整体长度对512取模之后的值为448，len(message)%512 == 418，计算单位是bit（位）。
   
1. Append Padding Bits

    补位是这样的，先在message后面加0x80标识，然后加无限个0，一直满足对512bit取模之后等于448bit。
    
2. Append Length

    512bit和448相差64bit，即8Byte，这个8字节用来表示补位之前message的长度。
3. 计算消息摘

   有一个初始链变量，用来参与第一轮的运算，MD5的初始变量为：
 A = 0x67452301
 B = 0xefcdab89
 C = 0x98badcfe
 D = 0x10325476
 
 整体来说就是先补位，然后补长度，这个长度占8Byte，用来表示补位之前message的长度，然后计算md5。现在记住下面这句话：
 >每经过一次消息摘要计算，上面的**链变量会被新的值覆盖**，最后一轮经过高低位互换（aabbccdd -> ddccbbaa）就是最终的MD5值。

现在来进行md5扩展长度攻击：
我觉得直接把这个看完就差不多了：https://github.com/iagox86/hash_extender
 
骚年我们来翻译下：
准备下5个变量：

* secret = `secret`
* data = `data`
* H = md5()
* signature = hash(secret || data) = 6036708eba0d11f6ef52ad44e8b74d5b
* append = `append` （这个就是我们的payload，换句话说就是攻击的精华啊）
 
 服务器发送`data`和`signature`给小白，然后小白一看就知道是md5加密（md5加密是128bits，就是16bytes，或者是从源代码推算出来的），现在我们有三个已知：`data`, `加密算法`， `signature`，小白的目标就是把如何把`append`添加到`data`，然后产生一个新的data，同时一个新的signature。现在我们来进行md5的计算步骤，不了解的话看看前面。话说那个作者在研究各种hash算法的时候说了这么一句话，这都是人家费了几天时间的，赶紧记下来:
 
     The endianness of the length field is also important. MD4, MD5, and RIPEMD-160 are little-endian, whereas the SHA family and WHIRLPOOL are big-endian. Trust me, that distinction cost me days of work!
 
回到我们的例子来，`length(secret || data) = length("secretdata")`（为毛要这样写呢，因为md5计算里面，后面的pading里有表示message长度的字段），这个总共是10（0x0a）bytes，or 80(0x50)bits。 然后先补位（补到什么时候呢？满足对512bit取模之后等于448bit，也就是总共56Byte，再减去前面10Bytes），也就是补46bytes(80 00 00 00 ...)，然后是8 byte的长度字段(50 00 00 00 00 00 00 00)。全部加起来是64bytes, or one block, 这一坨放一起，看起来就是下面这一坨：

```
0000  73 65 63 72 65 74 64 61 74 61 80 00 00 00 00 00  secretdata......
0010  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0030  00 00 00 00 00 00 00 00 50 00 00 00 00 00 00 00  ........P.......
```
这一坨的结构是如下：

* "secret" = `secret`
* "data" = `data`
* 80 00 00... The 46 Bytes of padding, start with 0x80
* 50 00 00 00 00 00 00 00 -- message的长度

然后小白可以开始attack， Fire The Hole.
拿起来我们存半年的append，添加到上面这一坨，添加之后就变成这样了：

```
0000  73 65 63 72 65 74 64 61 74 61 80 00 00 00 00 00  secretdata......
0010  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0030  00 00 00 00 00 00 00 00 50 00 00 00 00 00 00 00  ........P.......
0040  61 70 70 65 6e 64                                append
```

这一坨就是最后我们把他返回给服务器的data，`data`是我们可以控制的。我们继续：
服务器接受到上面那坨之后开始计算md5，我们也可以计算这一坨的md5。先说说服务器是怎么算的，简单来说就是直接算：
```
0000  73 65 63 72 65 74 64 61 74 61 80 00 00 00 00 00  secretdata......
0010  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0020  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
0030  00 00 00 00 00 00 00 00 50 00 00 00 00 00 00 00  ........P.......
0040  61 70 70 65 6e 64                                append
```
歪果仁给的结果是`6ee582a1669ce442f3719c47430dadee`
小白怎么算呢？

* signature = hash(secret || data) 
现在小白手里有signature，但是小白修改了data啊，小白又不知道secret，只知道secret的长度。

> 每经过一次消息摘要计算，上面的**链变量会被新的值覆盖**，最后一轮经过高低位互换（aabbccdd -> ddccbbaa）就是最终的MD5值。

signature可以作为上一次的链变量，只需要从网上找一个md5算法，修改初始的链变量为现在的signature，重新计算下md5，结果就出来了。
 
简单来说hash长度扩展攻击就是给数据再加点长度，服务器那边计算哈希值，然后自己又有上一次的哈希结果，自己再算一下就跟服务器的一样了。
解决方案就是`hash(secret || md5(data))`，这么像sql注入发生的危害，用户的输入永远都是危险的。

配合以下资料看效果更好：

* http://ricterz.me/posts/%E5%93%88%E5%B8%8C%E9%95%BF%E5%BA%A6%E6%89%A9%E5%B1%95%E6%94%BB%E5%87%BB%E8%A7%A3%E6%9E%90
* http://blog.chinaunix.net/uid-27070210-id-3255947.html 
 
 
 
 
 
 
 
 
 
 
 
 
 

