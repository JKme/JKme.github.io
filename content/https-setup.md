Title: HTTPS 配置
Category: Learning
Date: 2016-11-14
slug: https-setup

HTTPS配置步骤，其实比较简单,先配置好nginx，然后安装certbot
` certbot certonly  --webroot -w /var/www/ -d abc.jozxing.cc`
会在`/etc/letsencrypt/live/domain.com/`目录下生成好文件。

这个时候就差不多done了，然后配置下nginx
https://mozilla.github.io/server-side-tls/ssl-config-generator

这个是mozilla一个HTTPS配置文件自动生成器。重点是以下几行：

```
server {  
    listen 443 ssl http2;
    ....
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;

    ssl_trusted_certificate /etc/letsencrypt/live/example.com/root_ca_cert_plus_intermediates;

    resolver <IP DNS resolver>;
    ....
}
```

ssl_dhparam通过下面的命令生成：

```
mkdir /etc/nginx/ssl
openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
```
ssl_trusted_certificate可选：

```
 cd /etc/letsencrypt/live/example.com
$ sudo wget https://letsencrypt.org/certs/isrgrootx1.pem
$ sudo mv isrgrootx1.pem root.pem
$ sudo cat root.pem chain.pem > root_ca_cert_plus_intermediates
```

resolver作用是解析OCSP服务器域名，建议填写VPS提供的DNS服务器。
最后下面是配置文件

```

server {
       	listen 80 default_server;
#      	ssl on;
       	server_name domain.com ;
       	return 301 https://$host$request_uri;
}
server
{

  
    root /var/www;
    index index.html;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
        ssl_ciphers 'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS';

  ssl_prefer_server_ciphers on;
    ssl_certificate /etc/letsencrypt/live/domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain.com/privkey.pem;
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    resolver 108.61.10.10;
    ssl_trusted_certificate /etc/letsencrypt/live/domain.com/root_ca_cert_plus_intermediates;
   # location ^~ /.well-known/acme-challenge/ {
   #     alias /var/www/challenges/;
   #     try_files $uri =404;
   # }
   # if ($host != 'domain.com'){
#      	    rewrite "^/(.*)$" http://domainc.om/$1 permanent;
    #}
#  location / {
#       rewrite ^/(.*)$ https://domain.com/$1 permanent;
 #  }

#    error_page 404 =301 http://domain.com;
#    location /index.php {
#        rewrite .* / permanent;
#   }
#    location / {
#        proxy_redirect off;
#        proxy_set_header Host $host;
#        proxy_set_header X-Real-IP $remote_addr;
#        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#        proxy_pass http://127.0.0.1:8888;
#    }
 location ~* (robots\.txt|favicon\.ico|crossdomain\.xml|google4c90d18e696bdcf8\.html|BingSiteAuth\.xml)$ {
        root             /var/www/index.html;
        expires          1d;
    }

    access_log /root/abc.log;
    error_log /root/err.log;
}
```

source:<https://ksmx.me/letsencrypt-ssl-https/>


