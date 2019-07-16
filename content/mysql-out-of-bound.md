Title: MySQL Out-of-Band Hacking
Date: 2017-3-31
Slug: mysql-out-of-band
Category: SQL

<https://osandamalith.com/2017/02/03/mysql-out-of-band-hacking/>
>In MySQL there exists a global system variable known as `secure_file_priv`, this variable limit the effiect of data import and export operations, such as those performed by the LOAD DATA and SELECT...INTO OUTFILE statements and the LOAD_FILE() function.

* If set to the name of a directory, the server limits import and export operations to work only with files in that directory. The directory must exitst, the server will not create it.
* If the variable is empty it has no effect, thus insecure configuration.
* If set to NULL, the server disables import and export operations. theis value is permitted as of MySQL 5.5.53


Before MySQL 5.5.53 this variable is empty by default, hence allowing us to use these functions. But in the versions after 5.5.53 the value 'NULL' will disable these functions.

To check the value of this variable you can use any of these methods. The `secure_file_priv` is a global variable and it's a read only variable, which means you cannot change this during runtime.

有以下三种方法可以查看`secure_file_priv`字段:

```
select @@secure_file_priv;
select @@global.secure_file_priv;
show variables like "secure_file_priv";
```

for example the default in MySQL 5.5.34 is empty, which means we can use these functions.

5.5.34版本这个字断是空的，就是说我们可以使用上面说到的函数：

没图。。。请看原链接

在MySQL 5.6.34里面，这个值默认是NULL, 然后就没法用导入导出函数操作了。

没图。。。请看原链接


