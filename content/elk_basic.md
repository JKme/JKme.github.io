 Title: elk操作相关
 Category: Learning
 Date: 2017-08-15
 slug: elk-log
 
 
 kibana里面开始添加index的时候，先查看es的索引:
 
 `curl 'localhost:9200/_cat/indices?v'`
 
 然后添加的时候直接写索引名字就行了。
 
 
 在kibana里面添加filter:

 搜索近三天的数据:

```
 
 {
  "query": {
    "range": {
      "@timestamp": {
        "gt": "now-3d"
      }
    }
  }
}
```
 
 
 搜索某一天的数据:
 
```
 
{
  "query": {
    "range": {
      "@timestamp": {
        "gt": "2017-08-15T01:00:00.900",
        "lt": "2017-08-15T23:59:00.900"
      }
    }
  }
}

```
 
 
 在kibana里面的Dev Tools可以直接操作es数据库:
 
 查询数据库某一天的数据:
 
```
 
 GET [index]/_search
{
  "query": {
    "range": {
      "@timestamp": {
        "gt": "2017-08-15T01:00:00.900",
        "lt": "2017-08-15T23:59:00.900"
      }
    }
  }
}

```

根据查询删除某一天的数据:

```
POST assets/_delete_by_query
{
  "query": {
    "range": {
      "@timestamp": {
        "lt": "2017-08-10T23:59:00.900"
      }
    }
  }
}
```

删除12小时之前的所有数据:

```
curl -XPOST "http://localhost:9200/assets/_delete_by_query" -H 'Content-Type: application/json' -d'
{ "query": { "range": { "@timestamp": { "lt": "now-12h" } } } }'
```

###logstash

在使用grok处理json格式的数据的时候，匹配是这样的:

```
grok {
        match => [
              "[http][request][body]",  "(?<waf>(?i)(.*)union(.*))"
        ]
      }
```