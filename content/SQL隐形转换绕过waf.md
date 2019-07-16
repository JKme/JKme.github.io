Title: SQL隐形弱类型转换绕过
Date: 2017-1-5
Category: SQL
slug: sql-waf-bypass



<https://tom.vg/2013/04/mysql-implicit-type-conversion/>
<https://www.t00ls.net/articles-24308.html>

如果PHP语句中存在这样的登录漏洞比如：

`$sql="select * from users where id='".$user."' and password='".md5($pass)."';`

但是在登录框处限制了用户名长度

```
if (strlen($user)>4){
print "用户名不能超过4个字符串";
echo $user;
echo strlen($user);
die();
}

```

如果未做限制的情况下可以构造这样的语句
`select * from users where userid = 1 or 1=1`

在限制的情况下可以利用sql隐形转换这样子：
`select * from users where userid=''=0#`

这个就全部选择出来了，然后重要的点在后面`userid=''=0#`，闭合前面单引号，于是整个数值就恒等于了，也可以这么写

`userid=''=false#`,`userid=''=(1-1)`,`userid='a'=0`

基本原理就是上面文章提到的：

算数操作符`+`会将字符型的user转换为数值型的user，
`dah`,`tagi`,`admin`对应的数值是0，
`1232dfs`，`123idu`对应的数值是123。

除去`+`号，其他操作符也会发生类型转换比如`MOD,DIV,*,/,%, -`