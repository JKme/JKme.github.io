Title: NAXSI和ELK
Category: Learning
Date: 2017-10-25
slug: naxsi-elk


NAXSI防火墙介绍: https://github.com/nbs-system/naxsi
配置安装: https://klionsec.github.io/2017/09/18/naxsiwaf/
主要功能：
 
过滤XSS，SQL注入，文件上传，文件遍历

NAXSI拦截攻击之后，会产生对应的日志。类似格式是这样的：

```
2017/10/25 14:52:34 [error] 896#0: *15 NAXSI_EXLOG: ip=192.168.141.232&server=192.168.182.141&uri=/sqli-labs/Less-11/index.php&id=1200&zone=BODY&var_name=passwd&content=admin../../../etc/passwd, client: 192.168.141.232, server: _, request: "POST /sqli-labs/Less-11/index.php HTTP/1.1", host: "192.168.182.141:8000", referrer: "http://192.168.182.141:8000/sqli-labs/Less-11/index.php"
2017/10/25 14:52:34 [error] 896#0: *15 NAXSI_FMT: ip=192.168.141.232&server=192.168.182.141&uri=/sqli-labs/Less-11/index.php&learning=0&vers=0.55.3&total_processed=4&total_blocked=4&block=1&cscore0=$TRAVERSAL&score0=12&zone0=BODY&id0=1200&var_name0=passwd, client: 192.168.141.232, server: _, request: "POST /sqli-labs/Less-11/index.php HTTP/1.1", host: "192.168.182.141:8000", referrer: "http://192.168.182.141:8000/sqli-labs/Less-11/index.php"
```

这里我打开了naxsi的EXLOG开关，这样当收集到攻击的日志，可以查看对应的请求内容: https://github.com/nbs-system/naxsi/wiki/naxsilogs
现在的目标是如何把上面的日志手收集到elk里面方便图形化查看，以下操作，先在logstash里面新建文件夹，写自己的正则：


```
logstash> mkdir pattern
logstash> cd pattern
logstash> vim naxsi
DA1 \d{4}/\d{2}/\d{2}
TM1 \d{2}:\d{2}:\d{2}
LEVEL (\w+)
NUM1 \d+(?:#0: \*)
NUM2 \d+
EXLOG NAXSI_EXLOG
FMT NAXSI_FMT
ID1 (\d+)
ZONE \w+
VAR1  (.*)
CONTENT (.*)
T3 \w+
T4 HTTP/1\.1", host: "(.*)", referrer: "
HOST (.*)
NAXSI %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s%{NUM1:num1}%{NUM2:request_id}\s(?<logtype>NAXSI_EXLOG):\s\w+=%{HOST:client_ip}&server=%{HOST:hostname}&uri=%{PROG:filepath}&id=%{ID1:id}&zone=%{ZONE:zone}&var_name=%{VAR1:var}&content=%{CONTENT:content},\sclient\:\s%{HOST:ip3},\sserver:\s(.*)\srequest:\s"%{T3:method}\s%{HOST:uri}\sHTTP/1\.1",\shost:\s"%{HOST:host22}"
NAXSI2 %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s%{NUM1:num1}%{NUM2:request_id}\s(?<logtype>NAXSI_EXLOG):\s\w+=%{HOST:client_ip}&server=%{HOST:hostname}&uri=%{PROG:filepath}&id=%{ID1:id}&zone=%{ZONE:zone}&var_name=%{VAR1:var}&content=%{CONTENT:content},\sclient\:\s%{HOST:ip3},\sserver:\s(.*)\srequest:\s"%{T3:method}\s%{HOST:uri}\sHTTP/1\.1",\shost:\s"%{HOST:host22}",\sreferrer:\s"(?<referrer>(.*))
NAXSI3 %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s(\d+(?:#0:\s\*))%{NUM2:request_id}\s(?<logtype>NAXSI_EXLOG)(.*)&var_name=%{VAR1:var}&content=%{CONTENT:content},\sclient\:\s(.*),\sserver:\s(.*)\srequest:\s"%{T3:method}\s%{HOST:uri}
NAXSI4 %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s(\d+(?:#0:\s\*))%{NUM2:request_id}\s(?<logtype>NAXSI_EXLOG)(.*)&var_name=%{VAR1:var}&content=%{CONTENT:content},\sclient\:\s(.*),\sserver:\s(.*)\srequest:\s"%{T3:method}\s%{HOST:uri}\sHTTP/1\.1",\shost:\s"%{HOST:host}",\sreferrer:\s"(?<referrer>(.*))
FMT %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s%{NUM1:num1}%{NUM2:request_id}\s(?<logtype>NAXSI_FMT):\sip=%{HOST:client_ip}&server=%{HOST:server_ip}&uri=%{UNIXPATH:uri}&learning=%{HOST:learing}&vers=%{HOST:vers}&total_processed=%{HOST:toal_processed}&total_blocked=%{HOST:total_blocked}&block=%{HOST:block}&cscore0=%{HOST:attack}&score0=%{HOST:score0}&cscore1=%{HOST:xss}&score1=%{HOST:score}&zone0=%{WORD:args}&id0=%{NUMBER:id}&var_name0=%{HOST:varname},\sclient:\s%{HOST:ip3},\sserver:\s(.*)\srequest:\s"%{T3:method}\s%{HOST:uri}\sHTTP/1\.1",\shost:\s"%{HOST:host22}"
FMT_R %{DA1:date}\s%{TM1:time}\s\[%{LEVEL:level}\]\s%{NUM1:num1}%{NUM2:request_id}\s(?<logtype>NAXSI_FMT):\sip=%{HOST:client_ip}&server=%{HOST:server_ip}&uri=%{UNIXPATH:uri}&learning=%{HOST:learing}&vers=%{HOST:vers}&total_processed=%{HOST:toal_processed}&total_blocked=%{HOST:total_blocked}&block=%{HOST:block}&cscore0=%{HOST:attack},\sclient:\s(.*)
```

上面这一坨翔就是解析最上面日志的正则，其中用到的是NAXSI3,NAXSI4,FMT_R,其他是调试用的。然后給logstash添加plugin:


```
bin/logstash-plugin install logstash-filter-grok
bin/logstash-plugin install logstash-filter-ruby
```


然后配置`/etc/logstash.conf`文件：


```
input{
     file {
       path => "/usr/local/nginx/logs/naxsi.err"
       type => "naxsi-error"
       start_position => "beginning"
   			}
}
filter{
     if [type] == "naxsi-error" {
	grok {
		patterns_dir => "/opt/logstash-5.5.1/pattern"
		match => [ "message" , "%{NAXSI4}",
			   "message" , "%{NAXSI3}",
			   "message" , "%{FMT_R}"
			]
  	     }
	ruby {
	code => "require 'digest/md5';
	event.set('computed_id', Digest::MD5.hexdigest(event.get('request_id')+event.get('time')) + '_' + event.get('logtype'))"
	    }

}
}
output{
      if [type] == "naxsi-error" {
	elasticsearch {
	   hosts => ["localhost"]
	   index => "nxapi"
           document_id => "%{computed_id}"
	}
	stdout { codec => rubydebug}
     }
}
```
配置好之后，启动logstash，这样对于同一次拦截会产生两条elk的日志，其中日志的document_id，前缀是请求的id和时间计算的hash，类似这样：
 
```
e0737c661e5e3457fbc3d847f75817fa_NAXSI_FMT
e0737c661e5e3457fbc3d847f75817fa_NAXSI_EXLOG
```
在线调试正则: <https://grokdebug.herokuapp.com>
