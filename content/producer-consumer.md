Title: 生产者消费者模型
Category: Learning
slug: producter-consumer
Date: 2017-12-11

代码捉急,先看例子:

```python
<http://www.jianshu.com/p/d85a4329d0c2>
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import Queue
import random
import time


class Producter(threading.Thread):
    """生产者线程"""
    def __init__(self, t_name, queue):
        self.queue = queue
        threading.Thread.__init__(self, name=t_name)

    def run(self):
        for i in range(10):
            randomnum = random.randint(1, 99)
            self.queue.put(randomnum)
            print 'put num in Queue %s' %  randomnum
            time.sleep(1)

        print 'put queue done'


class ConsumeEven(threading.Thread):
    """奇数消费线程"""
    def __init__(self, t_name, queue):
        self.queue = queue
        threading.Thread.__init__(self, name=t_name)

    def run(self):
        while True:
            try:
                queue_val = self.queue.get(1, 3)
            except Exception, e:
                print e
                break;

            if queue_val % 2 == 0:
                print 'Get Even Num %s ' % queue_val
            else:
                self.queue.put(queue_val)


q = Queue.Queue()
pt = Producter('producter', q)
ce = ConsumeEven('consumeeven', q)
ce.start()
pt.start()
pt.join()
ce.join()

```

照着写:

```
#!/usr/bin/env python
# coding: utf-8

from elasticsearch import Elasticsearch
import requests
from Queue import Queue
import time
import threading
import datetime

es = Elasticsearch('xxxxxx:9200', http_auth=('user', 'password'))


class Producter(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.initime = datetime.datetime.now().strftime('%Y.%m.%d')


	def initsearch(self):
		dsl_query = {
		  "query": {
		    "match": {
		      "method": {
		        "query": "GET",
		        "type": "phrase"
		      }
		    }
		  },
			"size": 100,
		"sort": [{"@timestamp": {"order": "desc"}}]
		}
		res = es.search(index="packetbeat-" + self.initime, body=dsl_query)
		latest_time = res['hits']['hits'][0]['_source']['@timestamp']
		return latest_time


	def run(self):
		latest_time = self.initsearch()
		while 1:
			lastindex = latest_time.split('T')[0].replace('-', '.')  # 获取最新的index
			dsl_query2 = {
				"query": {
					"bool": {
						"must": {
							"match": {
								"method": "GET"
							}
						},
						"filter": {
							"range": {
								"@timestamp": {
									"gte": latest_time
								}
							}
						}
					}
				},
				"sort": [{"@timestamp": {"order": "desc"}}],
				"size": 1000
			}
			time.sleep(10)
			res2 = es.search(index="packetbeat-" + lastindex, body=dsl_query2)
			for hit in res2['hits']['hits']:
				# print hit['_source']['@timestamp'], hit['_id'], hit['_source']['path']
				self.queue.put([hit['_source']['path'], hit['_source']['http']['request']['params'], hit['_source']['method']])
				print "Put %s" % hit['_id']
				print hit['_source']['@timestamp']
			latest_time = res2['hits']['hits'][0]['_source']['@timestamp']


class Consumer(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	#
	# def http_curl(self):
	# 	# http_client = AsyncHTTPClient()
	# 	path = self.request[0]
	# 	param = self.request[1]
	# 	method = self.request[2]
	# 	if method == "GET":
	# 		##判断get的param是否是空
	# 		if not param:
	# 			pass
	# 		else:
	# 			rep = requests.get("http://xxxxxx:9999" + path + '?' + param + "union select")
	# 			print "Curl %s" % self.request
	# 			print rep.status_code
	# 	else:
	# 		#留着写POST请求判断
	# 		pass


	def run(self):
		while 1:
			try:
				request = self.queue.get()
				path = request[0]
				param = request[1]
				method = request[2]
				if method == 'GET':
					if not param:
						pass
					else:
						rep = requests.get("http://xxxxx:9999" + path + '?' + param + "union select")
				#else  写POST
				print "Get %s" % request
				print rep.status_code
			except Exception as e:
				raise e

q = Queue()
pt = Producter(q)
ce = Consumer(q)
ce.start()
pt.start()
pt.join()
ce.join()
```

代码应该还有点问题，先记录下大概的流程：

使用: `packetbeat`在A服务器抓包，格式化之后把数据发送到B服务器，存储在elk里面，然后B服务器画图对这些请求进行分析，比如某个接口报警之类的。

这个时候在B服务器设置一个naxsi防火墙代理，然后把es里面的输出取出来，再发送一遍给B。经过测试，虽然这样子请求大部分都是404，但是如果请求中存在恶意payload，防火墙会记录日志。（所以这里的规则要设置的特别严格，严格到每个请求都不放过）

上面的脚本就是在B防火墙的转发脚本demo，测试为GET请求，因为POST请求的body没有存储到es里面，脚本的大概思路是这样的：

```
因为es里面存储的数据包是这样的格式: packet-[year]-[days]
所以先得到今天的日期，随便选100条，记录最新的时间戳，此时初始化完成。

下面的请求都是基于这个时间戳来的，每隔10s，在这个时间戳的基础上，轮询请求一次es，然后组装起来发送到B服务器。
记录下每次请求的最新日期，然后请求这个index，因为packet的格式: packet-[year]-[days],所以记录下每次请求的最新时间，格式化抓取最新的时间:

latest_time = res2['hits']['hits'][0]['_source']['@timestamp']

当es的存储数据按照大于某个时间点去筛选的时候，只会出现匹配的时间条数，所以可以把请求的size设置得大一点

```

暂时的问题：

* requests是同步请求库，追求效率可以使用异步请求
* 防火墙的正则匹配如果要得到准确的请求，需要进一步修改


