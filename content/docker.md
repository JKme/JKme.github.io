Title: Docker笔记
Date: 2016-10-8
Category: Learning
slug: docker-notes

* Docker container(容器): 应用在内部跑，有自己完整的文件系统和操作系统。
* Docker image(镜像): 应用代码各种库和文件打包一个文件，这个就是image，需要加载到容器才能运行。

```
docker info  #列出container和image的数量，宿主操作系统等

docker run -t -i ubuntu /bin/bash
#run 运行一个容器，-t 创造一个伪TTY, -i表示吧STDIN打开，这两个参数是让终端可用，ubuntu是指镜像名，/bin/bash是要运行的命令。exit或者Ctrl+d 退出

docker ps -a #查看有哪些容器在运行

docker start e0521aa52895 #启动那个容器
docker attach e0521aa52895 #再次登录上去，不能用run，否则会新建一个容器

上面两个命令用一个命令代替：
docker start -a -i e0521aa52895
# -a 表示attach， -i 表示开启stdin

如果想多连shell，attach命令会卡，可以用exec让这个容器再运行一个bash
docker exec -i -t e0521aa52895 /bin/bash

docker rm e0521aa52895 #删除容器
docker rm $(docker ps -q -f status=exited)d
#删除所有退出状态的容器

docker run -it -p 8888:80 imagine10255/centos6-lnmp-php56
#lnmp的80端口映射到8888端口，并且开启一个交互的shell


```

我想要docker在后台运行，每次都可以进去修改一些东西，但是查了资料不太如意，docker后台运行的时候，他里面必须要有一个程序一直在运行。为了偷懒我用了screen，然后`docker run -it -p 8888:80 --name web  imagine10255/centos6-lnmp-php56`，这样退出之后使用`docker exec -t -i 35f89fd74804 /bin/bash`。突然感觉好方便=。=

```
给docker起一个名字之后可以这样执行命令
docker exec web ls
docker start web
docker port web
```

docker修改了部分文件之后可以先退出，使得docker的container是exited状态，然后docker commit 3d1d1748aaeb web 这样保存，下次直接运行web这个images即可。

```
docker save IMAGENAMW |bazip2 -9 -c > img.tar.bz2
bzip2 -d -c < img.tar.bz2 |docker load


docker export <container id> |bzip2 -9 -c > img.tar.bz2
bzip2 -d -c < img.tar.bz2 | docker import - name/versio:tag
```

现在做一个lnmp的docker，使用ubuntu12.04,lnmp1.3版本，dockerfile如下

```
FROM ubuntu:12.04

ENV ROOT_PATH /root
RUN apt-get update && apt-get upgrade -y && apt-get install axel -y && apt-get install net-tools -y
WORKDIR $ROOT_PATH
RUN axel ftp://soft.vpser.net/lnmp/lnmp1.3-full.tar.gz && tar zxvf lnmp1.3-full.tar.gz && cd lnmp1.3-full
WORKDIR /root/lnmp1.3-full
RUN echo -e 8e17f72 | bash install.sh


EXPOSE 80 3306 9000
CMD ["bash"]
```

` docker build -t user/lnmp:tag  .`，在vps上面等等就ok，最后可以看到新生成的images，`docker start -it IMAGEID bash`删除一些东西，mysql进不去可以这样修改

```
/etc/init.d/mysql stop
mysqld_safe --user=mysql --skip-grant-tables --skip-networking &
mysql -uroot -p

update user set Password=PASSWORD('newpassword') where USER='root'
FLUSH PRIVILEGES;
quit

```
最后删除掉lnmp1.3.tar.gz和解压缩不必要的文件，最后保存推送到hub.docker.io，下次直接下载即可。

```
docker commit ContainerID  user/lnmp:tag
docker login
docker push ImageID
```


<https://www.keakon.net/2016/03/07/Docker学习后记>