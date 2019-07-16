Title: Hashcat笔记
Category: Pentest
Slug: hashcat
Date: 2019-03-01

在windows里面任意读取的文件，找到了sam.old文件和system.old文件，读取之后用burp保存到文件，可以使用如下的命令来提取密码:

```
root@kali:~# cachedump
usage: /usr/bin/cachedump <system hive> <security hive>

root@kali:~# lsadump
usage: /usr/bin/lsadump <system hive> <security hive>

root@kali:~# pwdump
usage: /usr/bin/pwdump <system hive> <SAM hive>

或者mimikatz: lsadump::sam /system:<SYSTEM> /SAM:<SAM>
```

提取的格式大概是这样:

```
root@kali:~# pwdump system sam
Administrator:500:41aa818b512a8c0e72381e4c174e281b:1896d0a309184775f67c14d14b5c365a:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
HelpAssistant:1000:667d6c58d451dbf236ae37ab1de3b9f7:af733642ab69e156ba0c219d3bbc3c83:::
SUPPORT_388945a0:1002:aad3b435b51404eeaad3b435b51404ee:8dffa305e2bee837f279c2c0b082affb:::
```


用户名称是:Administrator
RID是: 500
LM-HASH值: 41aa818b512a8c0e72381e4c174e281b
NT-HASH(NTLM)值: 1896d0a309184775f67c14d14b5c365a


可以使用hashcat来跑密码:

```
hashcat -m 1000 -a 0 --force hash.txt /usr/share/wordlists/rockyou.txt
```
其中的hash.txt 可以指的是上面的NT-HASH。

```
-m 1000 hash的类型，这里是NTLM
-a 0  0表示词典碰撞，这里是kali自带的辞典，还有3表示使用GPU来爆破，不用指定词典。
--force 忽略无显卡，直接跑
hash.txt 就是上面的NT-HASH

```

* <https://www.objectif-securite.ch/en/ophcrack.php>
 
* <https://cyberloginit.com/2017/12/26/hashcat-ntlm-brute-force.html>

* <https://medium.com/@petergombos/lm-ntlm-net-ntlmv2-oh-my-a9b235c58ed4>