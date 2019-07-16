Title: naxsi的规则
Category: Learning
Date: 2017-11-2
Slug: naxsi-rule

* MainRule: 定义检测的规则和分数
* BasicRule: 定义MainRule的白名单
* CheckRule: 定义当分值达到阈值采取的动作


###Checkrules
Checkrules指令有四种动作：

```
LOG, BLOCK, DROP, ALLOW
```
何时执行这四种动作？根据制定的得分(score)

####Basic Usage

```
CheckRule "$SQL >= 8" BLOCK;

```

如果`$SQL`大于等于8，则`BLOCK`掉这个请求。（前提是打开防火墙的过滤模式，而不是learning模式）

####Other Usages
看看另外的一种用法，白名单和黑名单一起用的时候，比如有这样的规则:

```
CheckRule "$UWA >= 4" DROP;
CheckRule "$XSS >= 8" BLOCK;
```
意思是任何请求只要匹配了`$UWA`规则，得分大于等于4，就block掉这个请求。
下面这个`$XSS`规则，只有开启了过滤（不是learning mode)，得分大于等于8就block

##Rules BNF

###RUles

规则是用来匹配请求中的攻击。比如DROP掉任何包含字符串`zz`的GET或者POST请求:

```
MainRule id:424242 "str:zz" "mz:ARGS|BODY" "s:DROP";
```

Rules can be present at location level(BasicRule) or http level (MainRule)


* 规则在写的时候，每个部分都必须要用双引号包含起来，除了id的那部分。


####id(id:...)

`id:num` 在规则里面必须是独一无二的，最终会出现在NAXSI_FMT日志里面

id小于1000时是naxsi里面的保留规则id值。


###Match Pattern

匹配的规则可以是正则，字符串或者调用一个库

* `rx:foo|bar`: 匹配`foo`或者`bar`   (rx应该是regex，正则匹配的意思)
* `str:foo|bar`: 匹配`foo|bar`
* `d:libinj_xss`: 如果libinjection返回结果是XSS，则匹配(>=0.55r2版本)
* `d:libinj_sql`: 如果libinjection返回结果SQLI,则匹配 (>=0.55r2版本)

官方建议: 在可以使用字符串匹配的时候，尽量使用字符串，这样会快点。所有的字符串要小写
naxsi的匹配值大小写不敏感的。

###Score(s:..)

你可以创建一个计分的规则:`s:$FOOBAR:4`，符合这个规则的时候，`$FOOBAR`的值就增加4积分。
一条规则可以有多个计分规则:`s:$FOO:4,$BAR:8`，同理`$FOO`会增加4积分，`$BAR`增加8积分
`s:`后面可以直接制定匹配的动作`DROP`或者`BLOCK`

###MatchZone(mz:...)

mz是匹配区域，决定了规则匹配哪一部分:

```
MainRule id:4242 str:z "mz:$ARGS_VAR:X|BODY";
```
在GET请求的参数X里面或者BODY里面的参数，搜索字符串z

```
MainRule id:4342 str:z "mz:$ARGS_VAR:X|BODY|$URL_X:^/foo";
```

在GET请求的X参数里面或者BODY里面或者URL里以/foo开头的路径搜索是否有z字符串
从0.55rc0版本里面，对于不知道的content-type,可以使用RAW_BODY来匹配:

```
MainRule id:4241 s:DROP str:z mz:RAQ_BODY;
```

只有在以下情况才会匹配RAW_BODy:

* Content-type是未知的，表示naxsi不知道如何处理
* `id 11`（内置的一个规则，对于所有未知类型，都是白名单处理）


##Match Zones

###Global Zones
<https://github.com/nbs-system/naxsi/wiki/matchzones-bnf>
有4个主要的匹配区域: URL, ARGS, HEADERS, BODY

* `ARGS`: GET参数
* `HEADERS`: HTTP头
* `BODY`: POST参数(and RAW_BODY)
* `URL`: URL（before '?')


或者具体点:

* `$ARGS_VAR:string`:具体的GET参数
* `HEADERS_VAR:string`:具体的HTTP头
* `$BODY_VAR:string`:具体的POST参数

或者用正则来表示:

* `$HEADERS_VAR_X:regex`: 正则匹配具体的HTTP头(>=0.52)
* `$ARGS_VAR_X:regex`: 正则匹配具体的GET参数
* `$BODY_VAR_X:regex`: 正则匹配具体的POST参数

具体点:
* `FILE_EXT`: 文件名







nasxi在业务防火墙中的应用：

两个问题：

