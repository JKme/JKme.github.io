Title: ubuntu安装msf的坑
Date: 2017-6-14
slug: msf-ubuntu
Category: Fun

* 安装ruby的时候建议使用rbenv

##postgresql

```

    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get purge postgresql*
    sudo apt-get -f install
    sudo apt-get install postgresql

```

然后切换到postgresql

```
sudo -s
su postgres

createuser msf -P -S -R -D 
createdb -O msf msf
exit
exit
```

修改config/database.yml

```
production:
    adapter: postgresql
    database: msf
    username: msf
    password: msf
    host: 127.0.0.1
    port: 5432
    pool: 75
    timeout: 5
```

根据对应位置把以下内容丢进去

```
sudo sh -c "echo export MSF_DATABASE_CONFIG=/opt/metasploit-framework/config/database.yml >> /etc/profile"

source /etc/profile
```

`for MSF in $(ls msf*); do ln -s /pentest/framework3/$MSF /usr/local/bin/$MSF;done`

##postgresql基本使用

postgres初次安装后，默认生成一个名为postgres的数据库和一个名为postgres的数据库用户，需要注意的是，同时还生成一个postgres的Linux系统用户。
添加新用户有两种方法:

第一种:

```
sudo adduser dbuser
sudo su - postgres
psql
\password postgres
create user dbuser with password 'password';
create database exampledb owner dbuser;
grant all privileges on database exampledb to dbuser;
\q
```

第二种:

```
sudo -u postgres createuser --superuser dbuser
sudo -u postgres psql
\password dbuser
\q 
sudo -u postgres createdb -O dbuser exampledb
```

登录数据库:

```
psql -U msf -d msf  -h127.0.0.1 -p 5432
drop database msf;  删除msf数据库
drop user msf;     删除msf用户
```
控制台命令:

使用psql进入控制台之后可以使用如下命令:

```
\du  列用户
\l   列数据看
\c    链接到其他数据看
```