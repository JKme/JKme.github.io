Title: Mysql字符集
Date: 2017-9-21
Slug: mysql-char
Category: SQL


```
Illegal mix of collations (gbk_chinese_ci,IMPLICIT) and (latin1_bin,IMPLICIT)
```

然后看看两个表:

```
SELECT table_schema, table_name, column_name, character_set_name, collation_name  FROM information_schema.columns  WHERE collation_name = 'gbk_chinese_ci'  ORDER BY table_schema, table_name,ordinal_position;


SELECT table_schema, table_name, column_name, character_set_name, collation_name  FROM information_schema.columns  WHERE collation_name = 'latin1_bin'  ORDER BY table_schema, table_name,ordinal_position;
```

修改方法:

```
先切换到mysql表
ALTER TABLE user CONVERT TO CHARACTER SET gbk;
```



后续:

这里有个重大问题，P神博客里面写到过mysql字符集的问题。