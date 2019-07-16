Title: Bash
Category: Fun
Date: 2017-11-24
slug: bash

```
#!/bin/bash
NUM=`ps -ef|grep spider|grep -v grep|wc -l`
echo $NUM
if [ $NUM -gt 4 ]
then
    `ps -ef |grep spider |grep -v grep |awk '{print $2}' |xargs kill -9`
else
    echo "hehe"
fi
```



```
#!/bin/bash

DATE=`date +%Y.%m.%d --date='7 days ago'`
MDATE=`date +%Y.%m.%d --date='7 days ago'`
curl -XDELETE "http://x.x.x.x:9200/logstash-"$DATE -u user:password
curl -u user:password  -XDELETE "http://x.x.x.x:9200/.monitoring-es-6-"$MDATA
NUM=`df -h |awk '{print $5}'|awk "NR==4"|grep -o '[0-9]*'`
if [ $NUM -gt 90 ]
then
  curl -XDELETE "http://x.x.x.x:9200/logstash-*" -u user:password
fi
```


```
这里使用curl发送的body如果有变量有个坑点，需要单引号和双引号加一起
#!/bin/bash
body=`curl "https://pwnhub.cn/api/hackgame/publicgame/list/?limit=10"|jq '.data.results[0]|{name,start_time,end_time,tag,status}'`
name=`echo $body|jq -r .name`
start_time=`echo $body|jq -r .start_time`
end_time=`echo $body|jq -r .end_time`
tag=`echo $body|jq -r .tag[0]`
status=`echo $body|jq -r .status`
if [ $tag != "CRYPTO" ];then
    curl -X POST -H "Content-Type: application/json" -d '{"text":"name: '$name'\nstart_time:'$start_time'\nend_time:'$end_time'\ntag:'$tag'\nstatus:'$status'"}' https://hook.bearychat.com/=bwBYn/incoming/xxxxx
fi
```